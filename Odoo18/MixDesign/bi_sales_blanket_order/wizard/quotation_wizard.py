# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class QuotationWizard(models.TransientModel):
    _name = "quotation.wizard"
    _description = "Quotation wizard"
    _rec_name = 'blanket_id'

    @api.model
    def _default_order(self):
        if not self.env.context.get("active_id"):
            return False
        blanket_order = self.env["blanket.order"].search([("id", "=", self.env.context["active_id"])], limit=1)
        if blanket_order.state == "expired":
            raise UserError(_("You can't create a sale order from " "an expired blanket order!"))
        return blanket_order

    @api.model
    def _check_blanket_order_line(self, bo_lines):
        precision = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        company_id = False

        if all(float_is_zero(line.remaining_uom_qty, precision_digits=precision) for line in bo_lines):
            raise UserError(_("The sale order has already been created."))

        for line in bo_lines:
            if line.order_id.state != "confirm":
                raise UserError(_("Sale Blanket Order %s is not open") % line.order_id.name)
            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise UserError(_("You have to select lines " "from the same company."))
            else:
                company_id = line_company_id

    # @api.model
    # def _default_values(self):
    #     blanket_order_line_id = self.env["blanket.order.line"]
    #     blanket_order_line_ids = self.env.context.get("active_ids", False)
    #     active_model = self.env.context.get("active_model", False)
    #
    #     if active_model == "blanket.order":
    #         bo_lines = self._default_order().order_line
    #     else:
    #         bo_lines = blanket_order_line_obj.browse(blanket_order_line_ids)
    #
    #     self._check_blanket_order_line(bo_lines)
    #     lines = [(0,0,{
    #                 "blanket_line_id": bol.id,
    #                 "product_id": bol.product_id.id,
    #                 "date_schedule": bol.date_schedule,
    #                 "remaining_uom_qty": bol.remaining_uom_qty,
    #                 "price_unit": bol.price_unit,
    #                 "product_uom": bol.product_uom,
    #                 "new_quatation_quantity": bol.remaining_uom_qty,
    #                 "partner_id": bol.partner_id,
    #             },
    #         )
    #         for bol in bo_lines.filtered(lambda l: not l.display_type and l.remaining_uom_qty != 0.0)]
    #     return lines

    @api.model
    def _default_values(self):
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model", "")

        if active_model == "blanket.order" and active_ids:
            blanket_orders = self.env["blanket.order"].browse(active_ids)
            bo_lines = blanket_orders.mapped("order_line")
        else:
            bo_lines = self.env["blanket.order.line"].browse(active_ids)

        self._check_blanket_order_line(bo_lines)

        lines = [
            (0, 0, {
                "blanket_line_id": bol.id,
                "product_id": bol.product_id.id,
                "date_schedule": bol.date_schedule,
                "remaining_uom_qty": bol.remaining_uom_qty,
                "price_unit": bol.price_unit,
                "product_uom": bol.product_uom.id,
                "new_quatation_quantity": bol.remaining_uom_qty,
                "partner_id": bol.partner_id.id,
            })
            for bol in bo_lines.filtered(lambda l: not l.display_type and l.remaining_uom_qty > 0)
        ]
        return lines

    blanket_id = fields.Many2one('blanket.order')
    order_id = fields.Many2one("sale.order", string="sale Order", domain=[("state", "=", "draft")])
    wizard_lines = fields.One2many("quotation.wizard.line", "quotation_wizard_id", string="Lines",
                                   default=_default_values)

    def _prepare_line_vals(self, line):
        return {
            "product_id": line.product_id.id,
            "name": line.product_id.name,
            "product_uom": line.product_uom.id,
            "sequence": line.blanket_line_id.sequence,
            "price_unit": line.blanket_line_id.price_unit,
            "blanket_order_id": line.blanket_line_id.order_id.id,
            "blanket_order_line": line.blanket_line_id.id,
            "product_uom_qty": line.new_quatation_quantity,
            "discount": line.discount,
            "tax_id": [(6, 0, line.taxes_id.ids)],
        }

    def _prepare_so_vals(
            self,
            customer,
            user_id,
            currency_id,
            pricelist_id,
            payment_term_id,
            order_lines_by_customer,
    ):
        return {
            "partner_id": customer,
            "origin": self.blanket_id.name,
            "user_id": user_id,
            "currency_id": currency_id,
            "pricelist_id": pricelist_id,
            "payment_term_id": payment_term_id,
            "order_line": order_lines_by_customer[customer],
        }

    def create_quotation(self):
        order_lines_by_customer = defaultdict(list)
        currency_id, pricelist_id, user_id, payment_term_id = 0, 0, 0, 0

        for line in self.wizard_lines.filtered(lambda l: l.new_quatation_quantity != 0.0):
            if line.new_quatation_quantity > line.remaining_uom_qty:
                raise UserError(_("You can't order %s qunatity of %s because the Remaining quantity is %s") % (
                line.new_quatation_quantity, line.product_id.name, line.remaining_uom_qty))

            vals = self._prepare_line_vals(line)
            order_lines_by_customer[line.partner_id.id].append((0, 0, vals))

            currency_id = currency_id or line.blanket_line_id.order_id.currency_id.id
            pricelist_id = pricelist_id or line.blanket_line_id.pricelist_id.id
            user_id = user_id or line.blanket_line_id.user_id.id
            payment_term_id = payment_term_id or line.blanket_line_id.payment_term_id.id

            if currency_id != line.blanket_line_id.order_id.currency_id.id:
                currency_id = False

            if pricelist_id != line.blanket_line_id.pricelist_id.id:
                pricelist_id = False

            if user_id != line.blanket_line_id.user_id.id:
                user_id = False

            if payment_term_id != line.blanket_line_id.payment_term_id.id:
                payment_term_id = False

        if not order_lines_by_customer:
            raise UserError(_("An order can't be empty"))

        if not currency_id:
            raise UserError(_("Cannot create Sale Order from Blanket"))

        res = []
        for customer in order_lines_by_customer:
            order_vals = self._prepare_so_vals(
                customer,
                user_id,
                currency_id,
                pricelist_id,
                payment_term_id,
                order_lines_by_customer,
            )
            sale_order = self.env["sale.order"].create(order_vals)
            res.append(sale_order.id)

        return {
            "domain": [("id", "in", res)],
            "name": _("Sales Orders"),
            "view_type": "form",
            "view_mode": "list,form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
        }


class QuotationWizardLine(models.TransientModel):
    _name = "quotation.wizard.line"
    _description = "Quotation Wizard Line"

    quotation_wizard_id = fields.Many2one("quotation.wizard")
    blanket_line_id = fields.Many2one("blanket.order.line")
    product_id = fields.Many2one("product.product", related="blanket_line_id.product_id", string="Product")
    product_uom = fields.Many2one("uom.uom", related="blanket_line_id.product_uom", string="Unit of Measure")
    partner_id = fields.Many2one("res.partner", string="Customer")
    remaining_uom_qty = fields.Float(related="blanket_line_id.remaining_uom_qty")
    date_schedule = fields.Date(string="Scheduled Date")
    new_quatation_quantity = fields.Float(string="New Quotation Quantity", required=True)
    remaining_uom_qty = fields.Float(related="blanket_line_id.remaining_uom_qty")
    price_unit = fields.Float(related="blanket_line_id.price_unit")
    currency_id = fields.Many2one("res.currency", related="blanket_line_id.currency_id")
    taxes_id = fields.Many2many("account.tax", related="blanket_line_id.tax_ids")
    discount = fields.Float(string='Discount (%)', related="blanket_line_id.discount")
