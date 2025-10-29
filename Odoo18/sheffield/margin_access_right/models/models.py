# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DiscountDigitsInherit(models.Model):
    _inherit = 'pos.order.line'

    discount = fields.Float(string='Discount (%)', digits=(16, 6), default=0.0)
