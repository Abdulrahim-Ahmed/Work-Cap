# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ShippingCompany(models.Model):
    _name = 'shipping.company'

    name = fields.Char(string="Company Name", required=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shopify_order_number = fields.Char(string="Shopify Order Number")
    cancel_reason = fields.Selection([
        ('changed_his_mind', 'Changed his mind'),
        ('merge', 'Merge'),
        ('unreachable', 'Unreachable'),
        ('bought_from_branch ', 'Bought From Branch'),
        ('out_of_stock', 'Out of stock')
    ], string="Cancel Reason")

    order_status = fields.Selection([
        ('new', 'New'),
        ('hold', 'Hold'),
        ('readyToShip', 'Ready To Ship'),
        ('readyToPack', 'Ready To Pack'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceledAfterShipping', 'Canceled After Shipping'),
        ('canceledBeforeShipping', 'Canceled Before Shipping')
    ], string="Order Status")

    shipping_company_id = fields.Many2one('shipping.company', string="Shipping Company")

    def cash_fees_button(self):
        """Button action to add the Cash Fees product to order lines."""
        product = self.env['product.template'].search([('name', '=', 'Cash fees')], limit=1)

        if product:
            self.order_line = [(0, 0, {
                'order_id': self.id,
                'product_id': product.id,  # Link to the specific Cash Fees product
                'name': product.name,  # Product description
                'product_uom_qty': 1,  # Default quantity
                'price_unit': product.list_price,  # Default price
            })]

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    barcode_product_sale = fields.Char(string="Barcode",related='product_id.barcode')