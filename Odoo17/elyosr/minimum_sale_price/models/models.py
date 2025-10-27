from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    minimum_sales_price = fields.Float(string="Minimum Sales Price")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    minimum_sales_price = fields.Float(string="Minimum Sales Price")
