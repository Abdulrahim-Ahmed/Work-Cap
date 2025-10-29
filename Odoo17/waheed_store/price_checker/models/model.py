from odoo import models, fields, api


class price_checker(models.Model):
    _name = "price.checker"
    _description = "Price Checker"

    product_id = fields.Many2one('product.product')
    product_price = fields.Float(related='product_id.lst_price')


# class pos_order_line_Checker(models.Model):
#     _inherit = 'pos.order.line'
#
#     price_checker_pos = fields.Many2one('pos.order.line', string='Check Price')