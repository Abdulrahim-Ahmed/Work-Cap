    # -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_edit = fields.Boolean(compute="_compute_can_edit")

    @api.depends()
    def _compute_can_edit(self):
        user = self.env.user
        for rec in self:
            rec.can_edit = user.has_group('extra_rights.group_edit_product_price')


class SaleOrderShowCostAndMargins(models.Model):
    _inherit = 'sale.order'

    can_view_margin = fields.Boolean(compute="_compute_can_view_margin")

    @api.depends("user_id")
    def _compute_can_view_margin(self):
        if self.env.user.has_group('extra_rights.group_show_costs_margins'):
            self.can_view_margin = True
        else:
            self.can_view_margin = False


class SaleOrderLineShowCostAndMargins(models.Model):
    _inherit = 'sale.order.line'

    can_view_margin = fields.Boolean(related="order_id.can_view_margin")

