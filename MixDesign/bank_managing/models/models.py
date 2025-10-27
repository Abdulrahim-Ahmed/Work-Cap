# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ManagingBank(models.Model):
    _name = 'managing.bank'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Bank'

    name = fields.Many2one('account.journal', string="Name", tracking=True, required=True)
    account_id = fields.Many2one('account.account', string="Account", tracking=True, required=False)
    bank_limit = fields.Float(string="Limit", tracking=True, required=True)
    balance = fields.Float(string="Balance", compute='_compute_balance', readonly=True)
    line_ids = fields.One2many('managing.bank.line', 'bank_id', string="Bank Lines")
    total_price = fields.Float(string='Total',
                               compute='_compute_total_price',
                               help='Total Lines Price')

    @api.depends('line_ids.amount')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = sum(rec.line_ids.mapped('amount'))

    @api.depends('bank_limit', 'total_price')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.bank_limit - rec.total_price


class ManagingBankLine(models.Model):
    _name = 'managing.bank.line'
    _description = 'Managing Bank Line'

    bank_id = fields.Many2one('managing.bank', string="Lines", required=True, ondelete='cascade')
    freight_number = fields.Char(string="Freight Number", required=True)
    amount = fields.Float(string="Amount", required=True)
