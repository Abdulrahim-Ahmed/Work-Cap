# -*- coding: utf-8 -*-
from odoo.tools.float_utils import float_is_zero
from odoo import models, fields, api


class StockQuantInherited(models.Model):
    _inherit = 'stock.quant'

    cost = fields.Float(string="Cost", related="product_id.standard_price")
    total_reserved_cost = fields.Float(string="Total Reserved", compute="_compute_total_reserved_cost", store=True)

    @api.depends('inventory_quantity_auto_apply', 'cost')
    def _compute_total_reserved_cost(self):
        for quant in self:
            quant.total_reserved_cost = quant.inventory_quantity_auto_apply * quant.cost

    # @api.depends('company_id', 'location_id', 'owner_id', 'product_id', 'quantity')
    # def _compute_value(self):
    #     """
    #     (Product.value_svl / Product.quantity_svl) * quant.quantity, i.e. average unit cost * on hand qty
    #     """
    #     for quant in self:
    #         quant.currency_id = quant.company_id.currency_id
    #
    #         # Check if inventory_quantity_auto_apply exists on product
    #         if hasattr(quant.product_id, 'inventory_quantity_auto_apply'):
    #             quant.value = quant.product_id.standard_price * quant.product_id.inventory_quantity_auto_apply
    #             continue
    #
    #         if not quant.location_id or not quant.product_id or \
    #                 not quant.location_id._should_be_valued() or \
    #                 (quant.owner_id and quant.owner_id != quant.company_id.partner_id) or \
    #                 float_is_zero(quant.quantity, precision_rounding=quant.product_id.uom_id.rounding):
    #             quant.value = 0
    #             continue
    #         quantity = quant.product_id.with_company(quant.company_id).quantity_svl
    #         if float_is_zero(quantity, precision_rounding=quant.product_id.uom_id.rounding):
    #             quant.value = 0.0
    #             continue
    #         quant.value = quant.quantity * quant.product_id.with_company(quant.company_id).value_svl / quantity

