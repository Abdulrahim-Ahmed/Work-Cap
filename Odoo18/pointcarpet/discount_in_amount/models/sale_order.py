# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_before_discount = fields.Float(
        string='Total Before Discount',
        compute='_compute_total_before_discount',
        store=True
    )
    discount_total = fields.Float(
        string="Total Discount",
        compute='_compute_total_discount_amount',
        store=True
    )

    @api.depends('order_line.before_discount')
    def _compute_total_before_discount(self):
        for order in self:
            order.total_before_discount = sum(line.before_discount for line in order.order_line)

    @api.depends('order_line.discount_amount')
    def _compute_total_discount_amount(self):
        for order in self:
            order.discount_total = sum(line.discount_amount for line in order.order_line)

    def _create_invoices(self, grouped=False, final=False):
        """Extend invoice creation to propagate custom fields to the invoice."""
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        for order in self:
            for invoice in order.invoice_ids:
                # Copy totals to the invoice
                invoice.total_before_discount = order.total_before_discount
                invoice.discount_total = order.discount_total

                # Map order lines to invoice lines
                for line in order.order_line:
                    invoice_lines = invoice.invoice_line_ids.filtered(lambda l: line.id in l.sale_line_ids.ids)
                    for inv_line in invoice_lines:
                        inv_line.before_discount = line.before_discount
                        inv_line.discount_amount = line.discount_amount
                        inv_line.discount = line.discount
        return invoices


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_amount = fields.Float(string="Discount Amount", default=0.0)
    before_discount = fields.Float(
        string="Before Discount",
        compute="_compute_before_discount",
        store=True
    )
    discount = fields.Float(
        string="Discount (%)",
        digits=(16, 4),
        compute='_compute_discount_percentage',
        store=True,
        readonly=False,
    )

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_before_discount(self):
        for line in self:
            line.before_discount = line.price_unit * line.product_uom_qty

    @api.depends('discount_amount', 'price_unit', 'product_uom_qty')
    def _compute_discount_percentage(self):
        for line in self:
            total_price = line.price_unit * line.product_uom_qty
            line.discount = (line.discount_amount / total_price * 100) if total_price else 0.0

    @api.onchange('discount', 'price_unit', 'product_uom_qty')
    def _onchange_discount_percentage(self):
        for line in self:
            total_price = line.price_unit * line.product_uom_qty
            line.discount_amount = (line.discount / 100 * total_price) if total_price else 0.0


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    before_discount = fields.Float(string="Before Discount")
    discount_amount = fields.Float(string="Discount Amount")
    discount = fields.Float(
        string='Discount (%)',
        digits=(16, 4),
        default=0.0,
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_before_discount = fields.Float(
        string='Total Before Discount',
        compute='_compute_total_before_discount',
        store=True
    )
    discount_total = fields.Float(
        string="Total Discount",
        compute='_compute_total_discount_amount',
        store=True
    )

    @api.depends('invoice_line_ids.before_discount')
    def _compute_total_before_discount(self):
        for invoice in self:
            invoice.total_before_discount = sum(line.before_discount for line in invoice.invoice_line_ids)

    @api.depends('invoice_line_ids.discount_amount')
    def _compute_total_discount_amount(self):
        for invoice in self:
            invoice.discount_total = sum(line.discount_amount for line in invoice.invoice_line_ids)
