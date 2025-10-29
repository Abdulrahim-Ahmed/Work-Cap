# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PriceListAddingFields(models.Model):
    _inherit = 'product.pricelist.item'

    barcode = fields.Char('Barcode', related='product_tmpl_id.barcode')
    list_price = fields.Float(
        'Sales Price', digits='Product Price', related='product_tmpl_id.list_price',
        help="Price at which the product is sold to customers.")
