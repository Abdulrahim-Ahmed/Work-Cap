# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderCustom(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrderCustom, self).button_confirm()

        # Create delivery for each confirmed purchase order
        for order in self:
            if order.picking_ids:
                for picking in order.picking_ids:
                    # Use move_ids_without_package instead of move_lines
                    for move in picking.move_ids_without_package:
                        # Check if the move is related to the purchase line
                        if move.purchase_line_id:
                            # Set demand as the ordered quantity
                            move.product_uom_qty = move.purchase_line_id.product_qty
                            # Set done quantity to 0 by default
                            move.quantity = 0

        return res


class DeliveryOrderCustom(models.Model):
    _inherit = 'stock.picking'

    total_ordered = fields.Integer(string="Total Ordered", store=True,
                                   compute='_compute_total_ordered')
    total_received = fields.Integer(string="Total Received", compute='_compute_total_received', store=True)

    @api.depends('move_ids_without_package.product_uom_qty')
    def _compute_total_ordered(self):
        for picking in self:
            total = sum(picking.move_ids_without_package.mapped('product_uom_qty'))
            picking.total_ordered = total

    @api.depends('move_ids_without_package.quantity')
    def _compute_total_received(self):
        for picking in self:
            total = sum(picking.move_ids_without_package.mapped('quantity'))
            picking.total_received = total
