# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CompanyInerit(models.Model):
    _inherit = 'res.company'

    bank_name = fields.Char('Name of Bank', required=False)
    account_number = fields.Char('Account Number', required=False)
    iban = fields.Char('IBAN Number', required=False)


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    total_qty = fields.Float(compute='_compute_total_qty', string='Total Quantity')

    @api.depends('invoice_line_ids.quantity')
    def _compute_total_qty(self):
        for record in self:
            record.total_qty = sum(line.quantity for line in record.invoice_line_ids)
