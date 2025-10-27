# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    blanket_order_id = fields.Many2one("blanket.order", string="Blanket order",
                                       related="order_line.blanket_order_line.order_id", )

    @api.model
    def _check_exchausted_blanket_order(self):
        return any(
            line.blanket_order_line.remaining_qty < 0.0 for line in self.order_line
        )

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if order._check_exchausted_blanket_order():
                raise ValidationError(
                    _("Cannot confirm order %s as one of the lines refers " "to a blanket order that has no remaining quantity.") % order.name)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    blanket_order_line = fields.Many2one("blanket.order.line", string="BO Product",
                                         domain="[('order_id', '=', blanket_order_id), ('remaining_uom_qty', '>', 0)]",
                                         copy=False)
    blanket_order_ref = fields.Char(
        string="BO Number",
        related="blanket_order_line.order_id.name",
        store=True,
        readonly=True
    )
    blanket_order_id = fields.Many2one(
        "blanket.order",
        string="Blanket Order",
        domain="[('partner_id', '=', order_partner_id), ('state', '=', 'confirm'), "
               "('order_line.remaining_uom_qty', '>', 0)]"
    )

    blanket_order_remaining = fields.Float(related="blanket_order_line.remaining_uom_qty", store=False,
                                           string="BO Remaining Qty")

    @api.onchange('blanket_order_line')
    def _onchange_blanket_order_line(self):
        if self.blanket_order_line:
            self.product_id = self.blanket_order_line.product_id
            self.product_uom_qty = self.blanket_order_line.remaining_uom_qty
            self.product_uom = self.blanket_order_line.product_uom
            self.price_unit = self.blanket_order_line.price_unit
            self.discount = self.blanket_order_line.discount
            self.tax_id = self.blanket_order_line.tax_ids
            # self.blanket_order_remaining = self.blanket_order_line.remaining_uom_qty
            # self.remaining_uom_qty = self.blanket_order_line.remaining_uom_qty

    @api.constrains('product_uom_qty', 'blanket_order_line')
    def _check_blanket_order_qty(self):
        for line in self:
            if line.blanket_order_line:
                # Calculate remaining qty excluding current line to avoid circular dependency
                blanket_line = line.blanket_order_line
                other_sale_lines = blanket_line.sale_lines.filtered(lambda sl: sl.id != line.id)
                ordered_qty = sum(
                    sl.product_uom._compute_quantity(sl.product_uom_qty, blanket_line.product_uom)
                    for sl in other_sale_lines
                    if sl.order_id.state not in ('cancel', 'draft') and sl.product_id == blanket_line.product_id
                )
                remaining_qty = blanket_line.product_uom_qty - ordered_qty

                if line.product_uom_qty > remaining_qty:
                    raise ValidationError(_(
                        "The ordered quantity (%.2f) for product '%s' "
                        "exceeds the BO Remaining Qty (%.2f)."
                    ) % (line.product_uom_qty, line.product_id.display_name, remaining_qty))

    # @api.constrains('product_uom_qty', 'blanket_order_remaining')
    # def _check_blanket_order_qty(self):
    #     for line in self:
    #         if (
    #                 line.blanket_order_line
    #                 and line.product_uom_qty > line.blanket_order_remaining
    #         ):
    #             raise ValidationError(_(
    #                 "The ordered quantity (%.2f) for product '%s' "
    #                 "exceeds the BO Remaining Qty (%.2f)."
    #             ) % (line.product_uom_qty, line.product_id.display_name, line.blanket_order_remaining))

    @api.constrains("product_id")
    def check_product_id(self):
        for line in self:
            if (line.blanket_order_line and line.product_id != line.blanket_order_line.product_id):
                raise ValidationError(_("The product in the blanket order and in the "))

    @api.constrains("currency_id")
    def check_currency(self):
        for line in self:
            if line.blanket_order_line:
                if line.blanket_order_line and line.currency_id != line.blanket_order_line.order_id.currency_id:
                    raise ValidationError(_("The currency of the blanket order must match with."))

    # def get_assigned_line(self, bo_lines):
    #     assigned_bo_line = None
    #     date_planned = date.today()
    #     date_delta = timedelta(days=365)
    #
    #     for line in bo_lines:
    #         if line.date_schedule:
    #             date_schedule = line.date_schedule
    #             if abs(date_schedule - date_planned) < date_delta:
    #                 assigned_bo_line = line
    #                 date_delta = abs(date_schedule - date_planned)
    #
    #     if assigned_bo_line is not None:
    #         return assigned_bo_line
    #
    #     non_date_bo_lines = [line for line in bo_lines if not line.date_schedule]
    #
    #     if non_date_bo_lines:
    #         return non_date_bo_lines[0]

    # def _get_eligible_bo_lines_domain(self, base_qty):
    #     bo_id = [
    #         ("product_id", "=", self.product_id.id),
    #         ("remaining_qty", ">=", base_qty),
    #         ("currency_id", "=", self.order_id.currency_id.id),
    #         ("order_id.state", "=", "open"),
    #     ]
    #     if self.order_id.partner_id:
    #         bo_id.append(("partner_id", "=", self.order_id.partner_id.id))
    #     return bo_id

    # def _get_eligible_bo_lines(self):
    #     base_qty = self.product_uom._compute_quantity(
    #         self.product_uom_qty, self.product_id.uom_id
    #     )
    #     bo_id = self._get_eligible_bo_lines_domain(base_qty)
    #     return self.env["blanket.order.line"].search(bo_id)

    # def get_assigned_bo_line(self):
    #     self.ensure_one()
    #     eligible_bo_lines = self._get_eligible_bo_lines()
    #     # if eligible_bo_lines:
    #     #     if (
    #     #             not self.blanket_order_line
    #     #             or self.blanket_order_line not in eligible_bo_lines
    #     #     ):
    #     #         self.blanket_order_line = self._get_assigned_bo_line(eligible_bo_lines)
    #     # else:
    #     #     self.blanket_order_line = False
    #     # self.onchange_blanket_order_line()
    #     return {"domain": {"blanket_order_line": [("id", "in", eligible_bo_lines.ids)]}}

    # @api.onchange("product_id", "order_partner_id")
    # def onchange_product(self):
    #     if self.product_id:
    #         return self.get_assigned_bo_line()
    #     return

    # @api.onchange("blanket_order_line")
    # def onchange_blanket_order_line(self):
    #     bol = self.blanket_order_line
    #     if bol:
    #         self.product_id = bol.product_id
    #         if bol.product_uom != self.product_uom:
    #             price_unit = bol.product_uom._compute_price(
    #                 bol.price_unit, self.product_uom
    #             )
    #         else:
    #             price_unit = bol.price_unit
    #         self.price_unit = price_unit
    #         if bol.tax_ids:
    #             self.tax_id = bol.tax_ids
    #     else:
    #         if not self.tax_id:
    #             self._compute_tax_id()
    #         self.with_context(skip_blanket_find=True)
