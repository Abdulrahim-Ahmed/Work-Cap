# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    vendor_debit_account_id = fields.Many2one(
        'account.account',
        string='Vendor Debit Account',
        domain="[('deprecated', '=', False)]",
        check_company=True,
        help="Account used for vendor advanced payment debit entries"
    )
    
    customer_credit_account_id = fields.Many2one(
        'account.account',
        string='Customer Credit Account',
        domain="[('deprecated', '=', False)]",
        check_company=True,
        help="Account used for customer advanced payment credit entries"
    )