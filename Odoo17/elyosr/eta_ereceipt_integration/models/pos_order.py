from datetime import datetime, timedelta
import json
import pprint
import logging
import psycopg2
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import requests
from odoo import api, models, _
import urllib3
import ssl
import math
from time import sleep
from odoo.tools.float_utils import json_float_round

_logger = logging.getLogger(__name__)

ETA_URLS = {
    'access_token_pre': 'https://id.preprod.eta.gov.eg/connect/token',
    'access_token_pro': 'https://id.eta.gov.eg/connect/token',
    'submit_receipt_pre': 'https://api.preprod.invoicing.eta.gov.eg/api/v1/receiptsubmissions',
    'submit_receipt_pro': 'https://api.invoicing.eta.gov.eg/api/v1/receiptsubmissions',
    'get_receipt_pre': 'https://api.preprod.invoicing.eta.gov.eg/api/v1/receipts/%s/raw',
    'get_receipt_pro': 'https://api.invoicing.eta.gov.eg/api/v1/receipts/%s/raw',
    'get_receipt_submission_pro': 'https://api.invoicing.eta.gov.eg/api/v1/receiptsubmissions/%s/details?PageNo=%s&PageSize=100'
    # 100 receipts count per page is max
}


class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    '''Transport adapter" that allows us to use custom ssl_context.'''

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


class POSOrder(models.Model):
    _inherit = 'pos.order'

    eta_uuid = fields.Char('ETA UUID', copy=False, index=True)
    eta_submission_uuid = fields.Char('ETA Submission UUID')
    eta_submit_state = fields.Selection([('unsent', _('Unsent')),
                                         ('sent', _('Sent'))], default='unsent', copy=False)
    eta_status = fields.Selection([('invalid', 'Invalid'),
                                   ('valid', 'Valid'),
                                   ('inprogress', 'In progress'),
                                   ('undetected', 'Undetected')], copy=False)
    invalid_reason = fields.Text('Validation Error')

    can_edit_order_date = fields.Boolean(compute='_compute_can_edit_order_date')

    def _compute_can_edit_order_date(self):
        for order in self:
            if order.eta_submit_state == 'sent' and order.eta_status in ['valid', 'inprogress']:
                order.can_edit_order_date = False
            elif self.env.user.has_group('eta_ereceipt_integration.group_pos_order_date'):
                order.can_edit_order_date = True
            else:
                order.can_edit_order_date = False

    def _prepare_header_info(self, date_order=False):
        if not date_order:
            date_order = self.date_order

        date_order -= timedelta(
            minutes=5)  # Reduce 5 min from issued date to avoid future issued date issue in sending E-receipt
        date_string = date_order.strftime('%Y-%m-%dT%H:%M:%SZ')
        company_currency_id = self.company_id.currency_id
        currency_id = self.currency_id
        header = {
            "dateTimeIssued": date_string,
            "receiptNumber": self.pos_reference,
            "uuid": "",
            "previousUUID": self._get_previous_order(),
        }

        if self.amount_total < 0.0:
            referenceUUID = False
            if self.refunded_order_ids:
                referenceUUID = self.refunded_order_ids.filtered(lambda r: r.eta_uuid)
                if not referenceUUID:
                    raise ValidationError(_('It must to send the origin receipt to ETA before the refund.'))
                else:
                    referenceUUID = referenceUUID[-1].eta_uuid

            header.update({
                'referenceUUID': referenceUUID or self.eta_uuid
            })

        header.update({
            "referenceOldUUID": "",
            "currency": currency_id.name,
            "exchangeRate": self.currency_rate if currency_id.id != company_currency_id.id else 0,
            "sOrderNameCode": self.name,
            "orderdeliveryMode": "FC",
            "grossWeight": 0.0,
            "netWeight": 0.0
        })

        return header

    def _get_previous_order(self):
        order_ids = self.search(
            [('config_id', '=', self.config_id.id), ('eta_submit_state', '=', 'sent'), ('eta_status', '=', 'valid'),
             ('id', '!=', self.id)], order='date_order desc')
        if not order_ids:
            return ""
        return order_ids[0].eta_uuid or ""

    def _prepare_seller_info(self):
        device_config_id = self.config_id.device_config_id
        return {
            "rin": device_config_id.partner_id.vat,
            "companyTradeName": device_config_id.partner_id.name,
            "branchCode": device_config_id.branch_code,
            "branchAddress": {
                "country": device_config_id.partner_id.country_id.code,
                "governate": device_config_id.partner_id.state_id.name,
                "regionCity": device_config_id.partner_id.city,
                "street": device_config_id.partner_id.street,
                "buildingNumber": device_config_id.partner_id.building_no,
                "postalCode": device_config_id.partner_id.zip or "",
                "floor": device_config_id.partner_id.floor or "",
                "room": device_config_id.partner_id.room or "",
                "landmark": device_config_id.partner_id.landmark or "",
                "additionalInformation": device_config_id.partner_id.additional_information or ""
            },
            "deviceSerialNumber": device_config_id.serial_number,
            "syndicateLicenseNumber": device_config_id.syndicate_license_number or "",
            "activityCode": device_config_id.activity_code
        }

    def _prepare_buyer_info(self):
        partner = self.partner_id
        if abs(self.amount_total) > 25000:
            if not partner:
                raise ValidationError(_('If receipt is more than 25,000 buyer details are required.'))
            return {
                "type": "B" if partner.company_type == 'company' and partner.country_id.code == 'EG' else "P" if partner.company_type == 'person' and partner.country_id.code == 'EG' else "F",
                "id": partner.vat,
                "name": partner.name,
                "mobileNumber": partner.mobile or "",
                "paymentNumber": ""
            }
        else:
            return {
                "type": "P",
                "id": partner.vat or "",
                "name": partner.name or "",
                "mobileNumber": partner.mobile or "",
                "paymentNumber": ""
            }

    def _prepare_item_lines(self):
        item_data = []
        for line in self.lines:
            if line.price_unit > 0 and line.qty != 0.0:
                qty = self._eta_round(abs(line.qty))
                discount = abs((line.discount / 100.0) * self._get_amount(qty * line.price_unit))

                receipt_data = {
                    "internalCode": line.product_id.default_code or line.product_id.item_code or line.product_id.barcode,
                    "description": line.full_product_name,
                    "itemType": line.product_id.item_type,
                    "itemCode": line.product_id.item_code or line.product_id.barcode,
                    "unitType": line.product_uom_id.unit_type,
                    "quantity": qty,
                    "unitPrice": self._get_amount(line.price_unit),
                    "netSale": self._get_amount(line.price_subtotal),
                    "totalSale": self._get_amount(qty * line.price_unit),
                    "total": self._get_amount(line.price_subtotal_incl)
                }

                receipt_data.update({
                    "valueDifference": 0.0,
                    "taxableItems": [
                        {
                            "taxType": str(tax['eg_eta_code']).split('_')[0].upper(),
                            "amount": self._get_amount(abs(tax['amount'])) or 0,
                            "subType": str(tax['eg_eta_code']).split('_')[1].upper(),
                            "rate": abs(tax['rate']) or 0,
                        } for tax in line.tax_ids_after_fiscal_position.compute_all(line.price_subtotal)['taxes']
                        if tax['eg_eta_code']
                    ]
                })
                if discount:
                    # if line.tax_ids:
                    receipt_data.update({
                        "commercialDiscountData": [{
                            'amount': self._get_amount(discount),
                            'description': str(self._get_amount(discount)),
                        }
                        ],
                    })
                    # else:
                    #     receipt_data.update({
                    #         "itemDiscountData": [
                    #             self._get_amount(discount),
                    #         ],
                    #     })
                item_data.append(receipt_data)
        _logger.info('Item Data: %s.' % item_data)
        return item_data

    def _amount_grouped_tax(self, lines=None):
        tax_lines = []
        if not lines:
            lines = self.lines.filtered(lambda l: l.price_unit > 0.0 and l.qty != 0.0)
        for line in lines:
            taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
            taxes = self.fiscal_position_id.map_tax(taxes)
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = \
                taxes.compute_all(price, line.order_id.pricelist_id.currency_id, abs(line.qty), product=line.product_id,
                                  partner=line.order_id.partner_id or False)['taxes']
            for tax in taxes:
                new_tax = True
                taxType = self.env['account.tax'].sudo().browse(tax['id']).eg_eta_code.split('_')[0].upper()
                for line in tax_lines:
                    if taxType and line['taxType'] == taxType:
                        line['amount'] += self._get_amount(tax['amount'])
                        new_tax = False

                if new_tax:
                    tax_lines.append({
                        'amount': self._get_amount(tax['amount']),
                        'taxType': taxType or ""
                    })

        # to round the total amount of tax after summation
        for tax in tax_lines:
            tax['amount'] = self._eta_round(abs(tax['amount']))

        return tax_lines

    def _prepare_receipt_data(self, date_order=False):
        lines = self._prepare_item_lines()
        return {
            "header": self._prepare_header_info(date_order),
            "documentType": {
                "receiptType": "S" if self.amount_total > 0.0 else "r",
                "typeVersion": "1.2"
            },
            "seller": self._prepare_seller_info(),
            "buyer": self._prepare_buyer_info(),
            "itemData": lines,
            "totalSales": self._get_amount(sum([line['totalSale'] for line in lines])),
            "totalCommercialDiscount": self._get_amount(self._get_total_commercial_discount(lines)),
            "totalItemsDiscount": self._get_amount(self._get_total_items_discount(lines)),
            "extraReceiptDiscountData": [{
                'amount': self._get_amount(self._prepare_global_discount()),
                'description': 'Global Discount',
            }],
            "netAmount": self._get_amount(sum([line['netSale'] for line in lines])),
            # "feesAmount": 0.0,
            "totalAmount": self._get_amount(self.amount_total),
            "taxTotals": self._amount_grouped_tax(),
            "paymentMethod": self.payment_ids[0].payment_method_id.eg_eta_code if self.payment_ids and self.payment_ids[
                0].payment_method_id.eg_eta_code else "C",
        }

    def _get_total_commercial_discount(self, lines):
        return sum(
            [sum(map(lambda l: l['amount'], line.get('commercialDiscountData', [{'amount': 0}]))) for line in lines])

    def _get_total_items_discount(self, lines):
        return sum([sum(map(lambda l: l, line.get('itemDiscountData', [0]))) for line in lines])

    def _action_gen_uuid(self, receipt_data):
        DEVICE_CONFIG = self.env['pos.device.config']
        SERIALIZED_DATA = DEVICE_CONFIG._serialize_receipt(receipt_data)
        UUID = DEVICE_CONFIG._hash_serialized_receipt(SERIALIZED_DATA)
        self.eta_uuid = UUID
        return UUID

    def _prepare_receipt_for_eta(self, date_order=False):
        receipt_data = self._prepare_receipt_data(date_order)
        uuid = self._action_gen_uuid(receipt_data)
        receipt_data['header']['uuid'] = uuid
        return receipt_data, uuid

    def _get_access_token(self):
        token = self._get_exist_access_token()
        if token:
            return token

        if self.config_id.device_config_id.production_env:
            url = ETA_URLS['access_token_pro']
        else:
            url = ETA_URLS['access_token_pre']
        credentials = self._get_pos_credentials()
        payload = 'grant_type={}&client_id={}&client_secret={}'.format(credentials['grant_type'],
                                                                       credentials['client_id'],
                                                                       credentials['client_secret'])
        headers = {
            'posserial': credentials['posserial'],
            'pososversion': credentials['pososversion'],
            'posmodelframework': '',
            'presharedkey': '',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            session = requests.session()
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ctx.options |= 0x4
            session.mount('https://', CustomHttpAdapter(ctx))
            response = session.request("POST", url, headers=headers, data=payload)
            _logger.info('Token Request: %s.' % response.text)
            response_data = response.json()
            if 'error' in response_data:
                raise ValidationError(_(response_data['error']))

            token = response_data.get('access_token')
            if token:
                DEVICE_CONFIG = self.config_id.device_config_id
                DEVICE_CONFIG.access_token = token
                DEVICE_CONFIG.token_expiration_date = datetime.now() + timedelta(
                    seconds=response_data.get('expires_in'))
                return token
        except Exception as ex:
            raise ValidationError(_('%s' % ex))

    def _get_pos_credentials(self):
        DEVICE_CONFIG = self.config_id.device_config_id
        return {
            'grant_type': DEVICE_CONFIG.grant_type,
            'client_id': DEVICE_CONFIG.client_id,
            'client_secret': DEVICE_CONFIG.client_secret,
            'posserial': DEVICE_CONFIG.serial_number,
            'pososversion': DEVICE_CONFIG.pos_os_version
        }

    def _get_exist_access_token(self):
        DEVICE_CONFIG = self.config_id.device_config_id
        if DEVICE_CONFIG.access_token and DEVICE_CONFIG.token_expiration_date and datetime.now() <= DEVICE_CONFIG.token_expiration_date:
            return DEVICE_CONFIG.access_token
        return False

    def _get_amount(self, amount):
        from_currency = self.currency_id
        to_currency = self.company_id.currency_id
        new_amount = amount
        if from_currency != to_currency:
            new_amount = amount * self._exchange_currency_rate()
        _logger.info('Calculate Amount: %s.' % new_amount)
        return self._eta_round(abs(new_amount))

    def _exchange_currency_rate(self):
        from_currency = self.currency_id
        to_currency = self.company_id.currency_id
        company = self.company_id
        rate = 1.0
        if from_currency != to_currency:
            rate = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company,
                                                                 self.date_order)
        _logger.info('Exchange Rate: %s.' % rate)
        return self._eta_round(rate)

    def action_get_eta_receipt_details(self, eta_submission_id=False, access_token=False, device_config_id=False):
        """
        Fetch ETA receipt details and update the order status.
        """

        def fetch_eta_status(order, uuid, access_token, device_config):
            """
            Fetch the ETA receipt status for a specific UUID.
            """
            # Determine the correct URL based on environment
            get_url = ETA_URLS['get_receipt_pro'] if device_config.production_env else ETA_URLS['get_receipt_pre']

            if not get_url:
                raise ValidationError(_('ETA receipt URL not configured for order %s') % order.name)

            # Prepare headers and session for the request
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            session = requests.session()
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ctx.options |= 0x4  # Disable SSL certificate verification warnings
            session.mount('https://', CustomHttpAdapter(ctx))

            # Make the GET request
            response = session.request("GET", get_url % uuid, headers=headers, data={})

            try:
                response_data = response.json()
            except ValueError:
                raise ValidationError(_('Invalid response received from the ETA service for order %s') % order.name)

            # Update order based on response
            receipt = response_data.get('receipt')
            if receipt and receipt.get('status'):
                order.eta_status = receipt.get('status').lower()
                order.eta_submit_state = 'sent'
            else:
                order.eta_status = 'undetected'

        # Handle case when all parameters are passed
        if eta_submission_id and access_token and device_config_id:
            self._action_get_eta_receipt_status(eta_submission_id, access_token, device_config_id)
        else:
            # Loop through orders for processing
            for order in self:
                access_token = order._get_access_token()

                # Try using eta_submission_id if available
                order_eta_submission_id = eta_submission_id or order.eta_submission_uuid
                if order_eta_submission_id:
                    self._action_get_eta_receipt_status(order_eta_submission_id, access_token,
                                                        order.config_id.device_config_id)
                    continue

                # Use the order's UUID if eta_submission_id is not available
                uuid = order.eta_uuid
                if not uuid:
                    raise ValidationError(_('UUID not found to check the status for order %s') % order.name)

                # Fetch the ETA status
                fetch_eta_status(order, uuid, access_token, order.config_id.device_config_id)

    def _action_get_eta_receipt_status(self, eta_submission_id, access_token, device_config_id):
        page_count = math.ceil(len(self.search([('eta_submission_uuid', '=', eta_submission_id)])) / 100)
        for page in range(1, page_count + 1):
            if device_config_id.production_env:
                url = ETA_URLS['get_receipt_submission_pro'] % (eta_submission_id, page)
            else:
                url = ETA_URLS['get_receipt_submission_pre']

            headers = {
                'Authorization': 'Bearer %s' % access_token,
            }

            try:
                session = requests.session()
                ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                ctx.options |= 0x4
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                session.mount('https://', CustomHttpAdapter(ctx))
                response = session.request("GET", url, headers=headers, data={}, verify=False)

                response_data = response.json()
                _logger.info('Receipt status response: %s.' % response.text)

                if 'submissionUuid' in response_data and 'receipts' not in response_data:
                    for receipt in self.search([('eta_submission_uuid', '=', response_data.get('submissionUuid'))]):
                        receipt.write({
                            'eta_status': response_data['status'].lower() if 'status' in response_data else 'undetected'
                        })

                        if 'errors' in response_data:
                            receipt.write({
                                'invalid_reason': response_data['errors']
                            })
                else:
                    for receipt in response_data.get('receipts', []):
                        rec = self.search([('eta_uuid', '=', receipt['uuid'])])
                        rec.write({
                            'eta_status': receipt['status'].lower() if 'status' in receipt else 'undetected'
                        })

                        if 'errors' in receipt:
                            rec.write({
                                'invalid_reason': receipt['errors']
                            })

            except Exception as ex:
                _logger.error('Error When Get Receipt Status: %s.' % ex)
                raise ValidationError(_('%s' % ex))

    def action_send_eta_receipt(self):
        payload = {"receipts": []}
        main_order = False
        for order in self:
            if main_order and main_order.config_id != order.config_id:
                raise ValidationError(_('All orders must be from one pos while send patch.'))

            main_order = order
            if not order.config_id.device_config_id:
                raise ValidationError(_('Create ETA configuration for this POS.'))

            if order.eta_submit_state == 'sent' and order.eta_status == 'valid':
                raise ValidationError(_('This receipt was already sent and valid.'))

            receipt_data, uuid = order._prepare_receipt_for_eta()
            pprint.pprint(receipt_data)

            payload['receipts'].append(receipt_data)

        access_token = main_order._get_access_token()
        _logger.info('Access Token: %s.' % access_token)

        if main_order.config_id.device_config_id.production_env:
            url = ETA_URLS['submit_receipt_pro']
        else:
            url = ETA_URLS['submit_receipt_pre']
        headers = {
            'Authorization': 'Bearer %s' % access_token,
            'Content-Type': 'application/json'
        }

        data = json.dumps(payload, ensure_ascii=False, indent=4).encode('utf-8')
        try:
            session = requests.session()
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ctx.options |= 0x4
            session.mount('https://', CustomHttpAdapter(ctx))
            response = session.request("POST", url, headers=headers, data=data)
            _logger.info('Submit URL: %s.' % url)
            _logger.info('Returned Response: %s.' % response.text)

            response_data = response.json()

            eta_submission_id = response_data.get('submissionId', False)

            if 'acceptedDocuments' in response_data:
                for acc_receipt in response_data['acceptedDocuments']:
                    rec = self.search([('eta_uuid', '=', acc_receipt['uuid'])])
                    if rec:
                        rec.eta_submission_uuid = eta_submission_id
                        rec.eta_submit_state = 'sent'

                # Wait 3 sec then check the status
                sleep(3)
                self.action_get_eta_receipt_details(eta_submission_id, access_token,
                                                    main_order.config_id.device_config_id)

            if 'rejectedDocuments' in response_data:
                for rej_receipt in response_data['rejectedDocuments']:
                    rec = self.search([('eta_uuid', '=', rej_receipt['uuid'])])
                    if rec:
                        rec.eta_submission_uuid = eta_submission_id
                        rec.eta_submit_state = 'sent'
                        rec.eta_status = 'invalid'
                        if 'error' in rej_receipt and 'details' in rej_receipt['error']:
                            errors = []
                            for error in rej_receipt['error']['details']:
                                errors.append('Message: %s, Target: %s,  Property Path: %s' % (
                                    error['message'], error['target'], error['propertyPath']))

                            text_error = '\n'.join(errors)
                            rec.invalid_reason = text_error



        except Exception as ex:
            _logger.error('Error When Send: %s.' % ex)
            raise ValidationError(_('%s' % ex))

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param dict order: dictionary representing the order.
        :param bool draft: Indicate that the pos_order is not validated yet.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns: id of created/updated pos.order
        :rtype: int
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
            pos_order._create_order_picking()
            pos_order._compute_total_cost_in_real_time()

        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order._generate_pos_order_invoice()
        if not pos_order.config_id.dont_send_e_receipt:
            pos_order.action_send_eta_receipt()

        return pos_order.id

    def _prepare_global_discount(self):
        total = 0
        for line in self.lines:
            if line.price_unit < 0:
                total += line.price_subtotal_incl
        return abs(total)

    # methods for handling right receipt format values
    @api.model
    def _eta_round(self, amount, precision_digits=5):
        """
            This method is call for rounding.
            If anything is wrong with rounding then we quick fix in method
        """
        return json_float_round(amount, precision_digits)
