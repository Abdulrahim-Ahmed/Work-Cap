# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductFormViewCustom(models.Model):
    _inherit = 'product.template'

    factory = fields.Many2one(comodel_name="factory.add", string="Factory Name", required=False)
    new_price = fields.Float('New Price')


class FactoryAdding(models.Model):
    _name = 'factory.add'

    name = fields.Char(string="Factory Name", required=False)


class PurchaseTreeViewCustom(models.Model):
    _inherit = 'purchase.order.line'

    custom_ref = fields.Char(string="Internal Reference", related='product_id.default_code',
                             optional="show", required=False, readonly=False)
    barcode_custom = fields.Char(string="Barcode", related='product_id.barcode',
                                 optional="show", required=False, readonly=False)
    factory = fields.Many2one(comodel_name="factory.add", string="Factory Name", required=False,
                              related='product_id.product_tmpl_id.factory', readonly=False)
    sales_pr = fields.Float(string="Sales Price",
                            optional="show", required=False, readonly=False,
                            related='product_id.product_tmpl_id.new_price')
    category_id = fields.Many2one(comodel_name="product.category", string="Product Category",
                                  related='product_id.categ_id', readonly=False)


class StockPickingInhereted(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPickingInhereted, self).button_validate()
        for picking in self:
            for move in picking.move_ids_without_package:
                if move.product_id.product_tmpl_id.new_price > 0:
                    move.product_id.product_tmpl_id.list_price = move.product_id.product_tmpl_id.new_price
                    move.product_id.product_tmpl_id.new_price = 0
        return res

class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    sales_pr = fields.Float(string="Sales Price",
                            optional="show", required=False, readonly=False,
                            related='product_id.product_tmpl_id.new_price')