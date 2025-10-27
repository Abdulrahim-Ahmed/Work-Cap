# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ammu Raj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from werkzeug import urls
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CustomClearance(models.Model):
    """Model for custom clearance"""
    _name = 'custom.clearance'
    _description = 'Custom Clearance'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Name', compute='_compute_name',
                       help='Name of custom clearance')
    freight_id = fields.Many2one('freight.order', required=True,
                                 string='Freight Order',
                                 help='Select the freight order', readonly=False)
    date = fields.Date(string='Clearance Creation', help='Date of clearance')
    clearance_start = fields.Date(string='Clearance Start', related='freight_id.receiving_date',
                                  help='Date of clearance')
    consignee_id = fields.Many2one('res.partner', string='Consignee',
                                   help="Select the consignee for the order", readonly=False)
    date_end = fields.Date(string='Clearance End', readonly=False, help='Date of clearance end')
    clearance_days = fields.Char(string="Clearance Duration", compute="_compute_clearance_days", store=True)
    agent_id = fields.Many2one('res.partner', string='Agent', required=True, readonly=False,
                               help='Select the agent for the clearance')
    loading_port_id = fields.Many2one('freight.port', string="Loading Port",
                                      help='Select the port for loading')
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port",
                                          help='Specify the discharging port')
    line_ids = fields.One2many('custom.clearance.line', 'clearance_id',
                               string='Clearance Line',
                               help='Line for adding the document')
    state = fields.Selection([('draft', 'Draft'), ('pending_custom', 'Pending Custom'),
                              ('received_custom', 'Received Custom'),
                              ('received_gafi', 'Open Form 46'),
                              ('received_final_declaration', 'Received Final Declaration'),
                              ('confirm', 'Confirm'),
                              ('done', 'Done')],
                             default='draft', string="State",
                             help='Different states of custom clearance')
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)
    user_id = fields.Many2one('res.users', string='Responsible User',
                              default=lambda self: self.env.user,
                              help="User responsible for this custom clearance")
    type = fields.Selection(related='freight_id.type', store=True)
    bank_id = fields.Many2one('managing.bank', string="Insurance Policy", tracking=True,
                              help="Select the bank for this freight order")
    temporary_bank_guarantee = fields.Many2one('managing.bank', string="Temp. Export Guarantee", tracking=True,
                                               help="Select the temporary export guarantee for this freight order")
    insurance = fields.Integer(string="Insurance", related='freight_id.insurance', store=True,
                               readonly=False, required=False)
    import_type = fields.Selection(related='freight_id.import_type', store=True)
    export_type = fields.Selection(related='freight_id.export_type', store=True)
    import_declaration2 = fields.Char(related='freight_id.import_declaration2', string="Import Declaration",
                                      required=False, readonly=False)
    export_declaration_date = fields.Date(string='Export Declaration Date', store=True)
    export_declaration2 = fields.Char(related='freight_id.export_declaration2', string="Export Declaration",
                                      required=False, readonly=False)
    received_custom = fields.Binary(string="Upload Custom", store=True)
    received_final_declaration = fields.Binary(string="Upload Final Declaration", store=True)
    source_import_declaration = fields.Char('Source Import Declaration', store=True,
                                            related='freight_id.source_import_declaration', readonly=False)
    c_d = fields.Char('CD', store=True, readonly=False)
    final_declaration = fields.Char('Final Declaration', store=True, readonly=False)
    gafi_received_date = fields.Date(string="Form 46 Date", readonly=True,
                                     help="Date when received GAFI state was set")
    gafi_remaining_days = fields.Integer(string="Days Remaining", compute="_compute_gafi_remaining_days",
                                         store=True)
    one_thousand = fields.Float(string="1/1000", compute="_compute_one_thousand", required=False)
    one_thousand_bank = fields.Many2one('managing.bank', string="1/1000 Bank",
                                        help="Select the bank for tracking 1/1000 tax")

    one_thousand_invoice_count = fields.Integer(
        string="1/1000 Invoice Count",
        compute="_compute_one_thousand_invoice_count"
    )
    last_computed_date = fields.Date(string="Last Computed Date", default=fields.Date.today)
    deducted = fields.Boolean('Deducted Insurance')

    @api.depends('insurance')
    def _compute_one_thousand(self):
        for record in self:
            record.one_thousand = record.insurance / 1000 if record.insurance else 0.0

    @api.depends('date', 'date_end', 'state')
    def _compute_clearance_days(self):
        """Compute clearance duration dynamically before confirmation, and fix it after confirmation."""
        for rec in self:
            if rec.clearance_start:
                if rec.state == 'confirm' and rec.date_end:
                    # If confirmed, store the final duration
                    days = (rec.date_end - rec.clearance_start).days
                else:
                    # If not confirmed, calculate days from start date until today
                    days = (date.today() - rec.clearance_start).days
                rec.clearance_days = f"{days} Days" if days > 0 else "0 Days"
            else:
                rec.clearance_days = "0 Days"

    @api.depends('export_declaration_date', 'gafi_received_date', 'state', 'last_computed_date')
    def _compute_gafi_remaining_days(self):
        for rec in self:
            rec.gafi_remaining_days = 0
            if rec.export_declaration_date:
                start_date = rec.export_declaration_date
                deadline = start_date + timedelta(days=90)
                end_date = rec.gafi_received_date or fields.Date.today()
                delta = (deadline - end_date).days
                rec.gafi_remaining_days = max(delta, 0)

    @api.model
    def update_gafi_remaining_days_computation(self):
        """Cron job method to trigger recomputation of GAFI remaining days"""
        today = fields.Date.today()
        # Find all active custom clearance records that need updating
        clearances = self.search([
            ('export_declaration_date', '!=', False),
            ('gafi_received_date', '=', False),  # Only for records without gafi_received_date
            ('last_computed_date', '!=', today)
        ])

        if clearances:
            # Update the trigger field to force recomputation
            clearances.write({'last_computed_date': today})
            _logger.info(
                f"Updated {len(clearances)} custom clearance records for daily GAFI remaining days computation")

    @api.depends('freight_id')
    def _compute_name(self):
        """Compute the name of custom clearance"""
        for freight in self:
            freight.name = 'CC - ' + str(
                freight.freight_id.name) if freight.freight_id else 'CC - '

    @api.onchange('freight_id')
    def _onchange_freight_id(self):
        """Getting default values for loading and discharging port"""
        for rec in self:
            rec.date = rec.freight_id.order_date
            rec.loading_port_id = rec.freight_id.loading_port_id
            rec.discharging_port_id = rec.freight_id.discharging_port_id
            # rec.agent_id = rec.freight_id.agent_id

    def action_deduct_insurance(self):
        for rec in self:
            if not rec.bank_id:
                raise ValidationError(_("No Insurance Policy Selected"))

            rec.deducted = True
            self.env['managing.bank.line'].create({
                'bank_id': rec.bank_id.id,
                'freight_number': rec.freight_id.name,
                'amount': rec.insurance,
            })

    def action_confirm(self):
        """Send mail to inform agents to custom clearance is confirmed"""
        for rec in self:
            rec.name = 'CC' \
                       ' - ' + rec.freight_id.name
            rec.state = 'confirm'

            if not rec.date_end:
                rec.date_end = date.today()

    def action_confirm_temp_export(self):
        """Send mail to inform agents to custom clearance is confirmed"""
        for rec in self:
            rec.name = 'CC' \
                       ' - ' + rec.freight_id.name
            rec.state = 'confirm'

            rec.date_end = date.today()

    def action_send_clearance_documents(self):
        self.ensure_one()

        # 1. Check consignee email
        if not self.consignee_id.email:
            raise ValidationError("Consignee does not have an email address.")

        # 2. Collect attachments from clearance lines
        attachments = []
        for line in self.line_ids:
            if line.document:
                attachment = self.env["ir.attachment"].create({
                    "name": line.name or "Document",
                    "datas": line.document,
                    "res_model": self._name,
                    "res_id": self.id,
                    "mimetype": "application/octet-stream",
                })
                attachments.append(attachment.id)

        if not attachments:
            raise ValidationError("No documents attached to send.")

        # 3. Find template named "Clearance Template"
        template = self.env['mail.template'].search([
            ('name', '=', 'Custom Request Template'),
            ('model_id', '=', self.env['ir.model']._get(self._name).id),
        ], limit=1)

        ctx = {
            'default_model': self._name,
            'default_res_ids': [self.id],
            'default_composition_mode': 'comment',
            'default_partner_ids': [self.consignee_id.id],
            'default_attachment_ids': attachments,
        }

        if template:
            ctx['default_template_id'] = template.id
            ctx['mark_so_as_sent'] = True  # mimic sale order behavior

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def action_pending_custom(self):
        for rec in self:
            rec.state = 'pending_custom'

            if rec.insurance:
                insurance_amount = rec.insurance

                if rec.bank_id:
                    self.env['managing.bank.line'].create({
                        'bank_id': rec.bank_id.id,
                        'freight_number': rec.freight_id.name,
                        'amount': insurance_amount,
                    })

                if rec.temporary_bank_guarantee:
                    self.env['managing.bank.line'].create({
                        'bank_id': rec.temporary_bank_guarantee.id,
                        'freight_number': rec.freight_id.name,
                        'amount': insurance_amount,
                    })

                # if rec.one_thousand and rec.one_thousand_bank:
                #     self.env['managing.bank.line'].create({
                #         'bank_id': rec.one_thousand_bank.id,
                #         'freight_number': rec.freight_id.name,
                #         'amount': rec.one_thousand,
                #     })

    def action_received_custom(self):
        for rec in self:
            rec.state = 'received_custom'

    def action_received_gafi(self):
        for rec in self:
            rec.state = 'received_gafi'
            rec.gafi_received_date = fields.Date.today()

            if rec.insurance:
                insurance_amount = rec.insurance

                if rec.temporary_bank_guarantee:
                    self.env['managing.bank.line'].create({
                        'bank_id': rec.temporary_bank_guarantee.id,
                        'freight_number': rec.freight_id.name,
                        'amount': -insurance_amount,
                    })

    def action_received_final_declaration(self):
        for rec in self:
            rec.state = 'received_final_declaration'

    def action_revision(self):
        """Creating custom revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Received/Delivered',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'custom.clearance.revision',
            'context': {
                'default_custom_id': self.id
            }
        }

    def action_get_revision(self):
        """Getting details of custom revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Revision',
            'view_mode': 'list,form',
            'res_model': 'custom.clearance.revision',
            'domain': [('custom_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # def action_create_one_thousand_tax_invoice(self):
    #     """Create invoice only for 1/1000 tax and register managing bank line"""
    #     self.ensure_one()
    #
    #     if not self.one_thousand:
    #         raise UserError("1/1000 tax is 0. Cannot create invoice.")
    #
    #     # Create managing bank line for 1/1000 if applicable
    #     if self.one_thousand and self.one_thousand_bank:
    #         self.env['managing.bank.line'].create({
    #             'bank_id': self.one_thousand_bank.id,
    #             'freight_number': self.freight_id.name,
    #             'amount': self.one_thousand,
    #         })
    #
    #     lines = [(0, 0, {
    #         'name': '1/1000 Tax',
    #         'price_unit': self.one_thousand,
    #         'quantity': 1.0,
    #     })]
    #
    #     invoice_vals = {
    #         'move_type': 'in_invoice',
    #         'partner_id': self.consignee_id.id,
    #         'invoice_user_id': self.env.user.id,
    #         'invoice_origin': self.name,
    #         'ref': f"{self.name} - 1/1000 Tax",
    #         'invoice_line_ids': lines,
    #     }
    #
    #     inv = self.env['account.move'].create(invoice_vals)
    #
    #     return {
    #         'name': '1/1000 Tax Invoice',
    #         'type': 'ir.actions.act_window',
    #         'views': [[False, 'form']],
    #         'target': 'current',
    #         'res_id': inv.id,
    #         'res_model': 'account.move',
    #     }

    def action_create_one_thousand_tax_invoice(self):
        """Create invoice only for 1/1000 tax and register managing bank line"""
        self.ensure_one()

        if not self.one_thousand:
            raise ValidationError("1/1000 tax is 0. Cannot create invoice.")

        # Create managing bank line for 1/1000 if applicable
        if self.one_thousand and self.one_thousand_bank:
            self.env['managing.bank.line'].create({
                'bank_id': self.one_thousand_bank.id,
                'freight_number': self.freight_id.name,
                'amount': self.one_thousand,
            })

        # 👇 Find partner "GENERAL AUTHORITY FOR INVESTMENT AND FREE ZONES"
        authority_partner = self.env['res.partner'].search([
            ('name', '=', 'GENERAL AUTHORITY FOR INVESTMENT AND FREE ZONES')
        ], limit=1)
        if not authority_partner:
            raise ValidationError(
                "Partner 'GENERAL AUTHORITY FOR INVESTMENT AND FREE ZONES' not found. Please create it in Contacts.")

        # 👇 Find product "GAFI"
        gafi_product = self.env['product.product'].search([
            ('name', '=', '1/1000 GAFI Charge ')
        ], limit=1)
        if not gafi_product:
            raise ValidationError("Product '1/1000 GAFI Charge ' not found. Please create it in Products.")

        # 👇 Use product in invoice line
        lines = [(0, 0, {
            'product_id': gafi_product.id,
            'name': f"{gafi_product.name} - 1/1000",
            'price_unit': self.one_thousand,
            'quantity': 1.0,
            'account_id': gafi_product.property_account_expense_id.id
                          or gafi_product.categ_id.property_account_expense_categ_id.id,
            'tax_ids': [(6, 0, gafi_product.taxes_id.ids)],
        })]

        invoice_vals = {
            'move_type': 'in_invoice',
            'partner_id': authority_partner.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'ref': f"{self.name} - 1/1000 Tax",
            'invoice_line_ids': lines,
        }

        inv = self.env['account.move'].create(invoice_vals)

        return {
            'name': '1/1000 Tax Bill',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': inv.id,
            'res_model': 'account.move',
        }

    def action_view_one_thousand_invoices(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('ref', '=', f"{self.name} - 1/1000 Tax")
        ])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', invoices.ids)]
        action['context'] = {'create': False}
        return action

    @api.depends('name')
    def _compute_one_thousand_invoice_count(self):
        for rec in self:
            rec.one_thousand_invoice_count = self.env['account.move'].search_count([
                ('ref', '=', f"{rec.name} - 1/1000 Tax")
            ])


class CustomClearanceLine(models.Model):
    """Uploading the documents for custom clearance"""
    _name = 'custom.clearance.line'
    _description = 'Custom Clearance Line'

    name = fields.Char(string='Document Name',
                       help='Name of the document attaching')
    document = fields.Binary(string="Documents", store=True, attachment=True,
                             help='Upload the document')
    clearance_id = fields.Many2one('custom.clearance',
                                   string='Custom Clearance',
                                   help='Relation from custom clearance')
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)
