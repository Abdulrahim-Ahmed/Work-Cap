# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingInherited(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')


