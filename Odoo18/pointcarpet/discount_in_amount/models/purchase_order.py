from odoo import models, fields, api


class PurchaseOrderTotalBeforeDiscount(models.Model):
    _inherit = 'purchase.order'

    total_before_discount = fields.Float(
        string='Total Before Discount',
        compute='_compute_total_before_discount',
        store=True
    )
    discount_total = fields.Float(
        string="Discount",
        compute='_compute_total_discount_amount',
        store=True
    )
    discount_amount = fields.Float(string="Discount Amount")
    before_discount = fields.Float(string="before discount")

    @api.depends('order_line.before_discount')
    def _compute_total_before_discount(self):
        for order in self:
            order.total_before_discount = sum(order.order_line.mapped('before_discount'))

    @api.depends('order_line.discount_amount')
    def _compute_total_discount_amount(self):
        for order in self:
            order.discount_total = sum(order.order_line.mapped('discount_amount'))

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Extend invoice creation to propagate custom fields to the invoice."""
        # Call the super method to generate the invoice
        invoice_vals = super()._create_invoices(grouped=grouped, final=final, date=date)

        for order in self:
            for invoice in order.invoice_ids:
                # Copy the totals to the invoice
                invoice.total_before_discount = order.total_before_discount
                invoice.discount_total = order.discount_total

                # Map order lines to corresponding invoice lines
                for line in order.order_line:
                    # Use product matching or other criteria to find corresponding invoice line
                    invoice_line = invoice.invoice_line_ids.filtered(
                        lambda l: l.purchase_line_id == line
                    )
                    for inv_line in invoice_line:
                        inv_line.before_discount = line.before_discount
                        inv_line.discount_amount = line.discount_amount

        return invoice_vals


class PurchaseDiscountInAmount(models.Model):
    _inherit = 'purchase.order.line'

    discount_amount = fields.Float(string="Discount In Amount", default=0.0)
    before_discount = fields.Float(
        string="Before Discount",
        compute="_compute_before_discount",
        store=True
    )
    discount = fields.Float(
        string="Discount (%)",
        compute='_compute_discount',
        digits=(16, 4),
        store=True,
        readonly=False,
    )

    @api.depends('price_unit', 'product_qty')
    def _compute_before_discount(self):
        for line in self:
            line.before_discount = line.price_unit * line.product_qty

    @api.depends('discount_amount', 'price_unit', 'product_qty')
    def _compute_discount(self):
        """Calculate the discount percentage based on the discount amount."""
        for line in self:
            if line.price_unit > 0 and line.product_qty > 0:
                total_price = line.price_unit * line.product_qty
                line.discount = (line.discount_amount / total_price) * 100 if total_price > 0 else 0.0
            else:
                line.discount = 0.0

    @api.onchange('discount', 'price_unit', 'product_qty')
    def _onchange_discount_percentage(self):
        """Calculate the discount amount based on the discount percentage."""
        for line in self:
            if line.price_unit > 0 and line.product_qty > 0:
                total_price = line.price_unit * line.product_qty
                line.discount_amount = (line.discount / 100) * total_price if total_price > 0 else 0.0
            else:
                line.discount_amount = 0.0


class AccountMoveLineDiscount(models.Model):
    _inherit = "account.move.line"

    before_discount = fields.Float(string="Before Discount")
    discount_amount = fields.Float(string="Discount In Amount")
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
        string="Discount",
        compute='_compute_discount_total',
        store=True
    )
    before_discount = fields.Float(string="before discount", default=0.0)
    discount_amount = fields.Float(string="discount amount", default=0.0)
    @api.depends('invoice_line_ids.before_discount')
    def _compute_total_before_discount(self):
        for invoice in self:
            invoice.total_before_discount = sum(invoice.invoice_line_ids.mapped('before_discount'))

    @api.depends('invoice_line_ids.discount_amount')
    def _compute_discount_total(self):
        for invoice in self:
            invoice.discount_total = sum(invoice.invoice_line_ids.mapped('discount_amount'))
