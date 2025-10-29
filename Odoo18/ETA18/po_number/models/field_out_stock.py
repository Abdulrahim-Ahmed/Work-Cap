from odoo import models, fields, api


class PoNumbere(models.Model):
    _inherit = 'sale.order.line'
    _description = "po number"

    po_number = fields.Char(string="RFQ Number")
    pro_code = fields.Char(string="Product Code")

    available = fields.Float('On Hand', related='product_id.qty_available', depends=['product_id'])
    stock_in_available = fields.Float(string="Available", readonly=False,
                                      compute='_compute_available',store=True)
    out_stock_test = fields.Float(string="Out Stock", required=False, compute='_compute_available_number')
    line_number = fields.Integer(string='Line Number', compute='_compute_line_number', store=True)

    @api.depends('order_id.order_line')
    def _compute_line_number(self):
        for record in self:
            for index, line in enumerate(record.order_id.order_line, start=1):
                line.line_number = index

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id: depends = ['product_id']
        self.available = self.product_id.qty_available
        self.stock_in_available = self.product_id.qty_available


    @api.depends('product_id.qty_available', 'product_uom_qty')
    def _compute_available_number(self):
        for line in self:
            if line.product_uom_qty >= line.available:
                print('a')
                line.out_stock_test = line.product_uom_qty - line.available

            else:
                print('b')
                line.out_stock_test = 0

    @api.depends('product_id.qty_available', 'product_uom_qty')
    def _compute_available(self):
        for line in self:
            if line.product_uom_qty >= line.available:
                print('c')
                line.stock_in_available = line.available

            else:
                print('d')
                line.stock_in_available = line.product_uom_qty
