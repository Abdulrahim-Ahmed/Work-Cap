# models/sale_order_line.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    minimum_sales_price = fields.Float(
        string="Minimum Sales Price",
        related="product_id.product_tmpl_id.minimum_sales_price",
        store=True,
        readonly=True
    )

    @api.constrains('price_unit', 'product_id')
    def _check_minimum_sales_price(self):
        """Block saving order lines below min price unless user has override group."""
        for line in self:
            if not line.product_id:
                continue

            user = self.env.user
            # Only enforce if user does NOT have override group
            if not user.has_group('minimum_sale_price.group_min_price_enforcement'):
                if line.price_unit < line.minimum_sales_price:
                    raise ValidationError(
                        f"The Unit Price ({line.price_unit}) for product '{line.product_id.display_name}' "
                        f"is below the Minimum Sales Price ({line.minimum_sales_price})."
                    )

    @api.onchange('price_unit', 'product_id')
    def _check_can_sale_minimum_sales_price(self):
        """Warn on onchange if below min price (but don’t block override users)."""
        if self.product_id and self.price_unit:
            user = self.env.user
            if user.has_group('minimum_sale_price.group_min_price_enforcement_sale_order') \
                    and not user.has_group('minimum_sale_price.group_min_price_enforcement'):

                min_price = self.product_id.minimum_sales_price
                if self.price_unit < min_price:
                    raise UserError(
                        f"The price ({self.price_unit}) is below the minimum allowed sales price ({min_price}) for this product.")
