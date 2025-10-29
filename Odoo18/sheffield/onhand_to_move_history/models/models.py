# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MoveHistoryOnHand(models.Model):
    _inherit = 'stock.move.line'

    onhand_qty = fields.Float(string='On Hand', store=True)

    @api.model
    def create(self, vals):
        # Get the product's current on-hand quantity and set it in the `onhand_qty` field
        product = self.env['product.product'].browse(vals.get('product_id'))
        vals['onhand_qty'] = product.qty_available
        return super(MoveHistoryOnHand, self).create(vals)

