# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockRules(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=lambda self: self._domain_product_id(),
        ondelete='cascade', required=False,
        check_company=True)
    product_category_id = fields.Many2one('product.category', name='Product Category', related='product_id.categ_id',
                                          store=True, readonly=False)
