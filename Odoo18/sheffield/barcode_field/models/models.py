from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    barcode_product = fields.Char(string="Barcode", related='product_id.barcode')


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking.line"

    barcode_product = fields.Char(string="Barcode", related='product_id.barcode')
