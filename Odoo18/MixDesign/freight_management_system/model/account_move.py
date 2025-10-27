# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_account_id = fields.Many2one(
        'account.account',
        string='Bank Account',
        domain="[('account_type', 'in', ['asset_cash'])]",
        help="Select the bank or cash account for this invoice"
    )
