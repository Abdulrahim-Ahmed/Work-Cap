# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleAllAvailable(models.Model):
    _inherit = 'sale.order'

    all_available = fields.Boolean('All Available?', compute='_compute_all_available', store=True)

    @api.depends(
        'order_line.product_id',
        'order_line.product_uom_qty',
        'order_line.product_id.qty_available',
        'order_line.product_id.stock_quant_ids.quantity'
    )
    def _compute_all_available(self):
        for order in self:
            if not order.order_line:
                order.all_available = False
                continue

            # Warehouse-specific context
            all_ok = True
            for line in order.order_line:
                if not line.product_id:
                    continue

                product = line.product_id.with_context(
                    warehouse=order.warehouse_id.id
                )

                if product.qty_available < line.product_uom_qty:
                    all_ok = False
                    break

            order.all_available = all_ok

    # @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    # def _compute_all_available(self):
    #     for order in self:
    #         if not order.order_line:
    #             order.all_available = False
    #             continue
    #
    #         # Check if ALL order lines are available
    #         all_ok = all(
    #             line.product_id.qty_available >= line.product_uom_qty
    #             for line in order.order_line
    #             if line.product_id
    #         )
    #
    #         order.all_available = all_ok
