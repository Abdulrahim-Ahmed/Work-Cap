# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WeightToSalesInherit(models.Model):
    _inherit = 'product.template'

    weight = fields.Float(
        'Gross Weight', compute='_compute_weight', digits='Stock Weight',
        inverse='_set_weight', store=True)
    net_weight = fields.Float('Net Weight', store=True, digits='Stock Weight')

    @api.depends('product_variant_ids.weight')
    def _compute_weight(self):
        self._compute_template_field_from_variant_field('weight')

    def _set_weight(self):
        self._set_product_variant_field('weight')
