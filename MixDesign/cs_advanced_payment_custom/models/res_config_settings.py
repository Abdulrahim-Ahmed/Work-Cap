# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vendor_debit_account_id = fields.Many2one(
        'account.account',
        string='Vendor Debit Account',
        related='company_id.vendor_debit_account_id',
        readonly=False,
        domain="[('deprecated', '=', False)]",
        check_company=True,
        help="Account used for vendor advanced payment debit entries"
    )
    
    customer_credit_account_id = fields.Many2one(
        'account.account',
        string='Customer Credit Account',
        related='company_id.customer_credit_account_id',
        readonly=False,
        domain="[('deprecated', '=', False)]",
        check_company=True,
        help="Account used for customer advanced payment credit entries"
    )