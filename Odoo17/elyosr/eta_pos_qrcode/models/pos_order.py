# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class POSOrder(models.Model):
    _inherit = 'pos.order'

    pos_qr_code_backend = fields.Char('E-Receipt URL')

    @api.model
    def generate_qr_code_value(self, order_id):
        order = self.browse(order_id)
        if order.config_id.device_config_id.production_env:
            url = 'https://invoicing.eta.gov.eg'
        else:
            url = 'https://preprod.invoicing.eta.gov.eg'

        qr_code = f"{url}/receipts/search/{order.eta_uuid}/share/{order.date_order.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        order.pos_qr_code_backend = qr_code
        return qr_code


    @api.model
    def get_eta_qr_code(self, order_number):
        order = self.search([('pos_reference', '=', f'Order {order_number}' if 'Order' not in order_number else order_number)], limit=1)
        if order:
            if order.config_id.dont_send_e_receipt:
                return False

            return "/report/barcode/QR/%s?width=200&height=200" % order.pos_qr_code_backend

        return False

    @api.model
    def _process_order(self, order, draft, existing_order):
        res_id = super()._process_order(order, draft, existing_order)
        self.generate_qr_code_value(res_id)
        return res_id

    # Generate QR URL after sending the receipt
    def action_send_eta_receipt(self):
        super(POSOrder, self).action_send_eta_receipt()
        self.generate_qr_code_value(self.id)

    def _export_for_ui(self, order):
        result = super(POSOrder, self)._export_for_ui(order)
        result.update({
            'pos_qr_code': "/report/barcode/QR/%s?width=200&height=200" % order.pos_qr_code_backend,
        })
        return result
