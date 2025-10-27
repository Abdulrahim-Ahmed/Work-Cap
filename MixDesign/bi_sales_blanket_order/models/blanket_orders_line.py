# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date
from collections import defaultdict


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    discount_policy = fields.Selection(selection=[
        ('with_discount', "Discount included in the price"),
        ('without_discount', "Show public price & discount to the customer"),
    ],
        default='with_discount',
        required=True,
        tracking=15,
    )


class BlanketOrderLine(models.Model):
    _name = "blanket.order.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Blanket Order Line"

    order_id = fields.Many2one('blanket.order', string='Order Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    remaining_uom_qty = fields.Float(
        string="Remaining quantity", compute="_compute_quantities", store=True
    )
    ordered_uom_qty = fields.Float(string="Ordered quantity", compute="_compute_quantities", store=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                  domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    price_unit = fields.Float('Unit Price', digits='Product Price', compute='_compute_price_unit', store=True,
                              readonly=False, required=True, precompute=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes',
                               domain=["|", ("active", "=", False), ("active", "=", True)], compute='_compute_tax_id',
                               store=True, readonly=False, precompute=True, check_company=True)
    date_schedule = fields.Date(string="Scheduled Date")
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    company_id = fields.Many2one(
        "res.company", related="order_id.company_id", store=True, index=True, precompute=True
    )
    currency_id = fields.Many2one("res.currency", related="order_id.currency_id")
    partner_id = fields.Many2one(related="order_id.partner_id", string="Customer")
    user_id = fields.Many2one(related="order_id.user_id", string="Responsible")

    payment_term_id = fields.Many2one(
        related="order_id.payment_term_id", string="Payment Terms"
    )
    pricelist_id = fields.Many2one(related="order_id.pricelist_id", string="Pricelist")
    price_subtotal = fields.Monetary(
        compute="_compute_amount", string="Subtotal", store=True
    )
    price_total = fields.Monetary(compute="_compute_amount", string="Total", store=True)
    price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    remaining_qty = fields.Float(
        string="Remaining quantity in base UoM",
        compute="_compute_quantities",
        store=True,
    )

    state = fields.Selection(
        related='order_id.state', string='Order Status', copy=False, store=True)

    remaining_uom_qty = fields.Float(
        string="Remaining quantity", compute="_compute_quantities", store=True
    )
    sale_lines = fields.One2many(
        "sale.order.line",
        "blanket_order_line",
        string="Sale order lines",
        readonly=True,
        copy=False,
    )

    product_uom_readonly = fields.Boolean(
        compute='_compute_product_uom_readonly')

    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id')

    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True, readonly=False, precompute=True, ondelete='restrict')
    delivered_qty = fields.Float(
        string='Delivered Quantity',
        compute='_compute_delivered_qty',
        store=True,
        help='The quantity delivered for this blanket order line'
    )

    @api.depends('sale_lines.qty_delivered')
    def _compute_delivered_qty(self):
        for line in self:
            # Calculate the delivered quantity by summing the delivered quantities from related sale order lines
            line.delivered_qty = sum(sl.qty_delivered for sl in line.sale_lines if sl.order_id.state != 'cancel')

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        lines_by_company = defaultdict(lambda: self.env['blanket.order.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = None
                if line.product_id:
                    taxes = line.product_id.taxes_id._filter_taxes_by_company(company)
                if not line.product_id or not taxes:
                    line.tax_ids = False
                    continue
                fiscal_position = line.order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                cache_key += line._get_custom_compute_tax_cache_key()
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                line.tax_ids = result

    def _get_custom_compute_tax_cache_key(self):
        """Hook method to be able to set/get cached taxes while computing them"""
        return tuple()

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                             product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or line.display_type or not line.order_id.pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )

    @api.depends('product_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            if not line.product_uom or not line.product_id:

                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price(self.product_id)
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )

    @api.depends('state')
    def _compute_product_uom_readonly(self):
        for line in self:
            line.product_uom_readonly = line.ids and line.state in ['expired']

    @api.depends('order_id', 'product_id')
    def _compute_display_name(self):
        result = []
        if self.env.context.get("from_sale_order"):
            for record in self:
                res = "[%s]" % record.order_id.name
                if record.date_schedule:
                    formatted_date = format_date(record.env, record.date_schedule)
                    res += " - {}: {}".format(_("Date Scheduled"), formatted_date)
                res += " ({}: {} {})".format(
                    _("remaining"),
                    record.remaining_uom_qty,
                    record.product_uom.name,
                )
                result.append((record.id, res))
            return result
        return super()._compute_display_name()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    _price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(
                        product, qty, self.order_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id,
                                                              self.company_id or self.env.company,
                                                              self.order_id.date_order or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    def _get_display_price(self, product):
        self.ensure_one()

        pricelist_price = self._get_pricelist_price()

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price

        if not self.pricelist_item_id:
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        return max(base_price, pricelist_price)

    def _get_pricelist_price_before_discount(self):
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self.pricelist_item_id
        order_date = self.order_id.date_order or fields.Date.today()
        product = self.product_id.with_context(**self._get_product_price_context())
        qty = self.product_uom_qty or 1.0
        uom = self.product_uom

        if pricelist_rule:
            pricelist_item = pricelist_rule
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                        product, qty, uom=uom, date=order_date)
                    pricelist_item = self.env['product.pricelist.item'].browse(rule_id)

            pricelist_rule = pricelist_item

        price = pricelist_rule._compute_base_price(
            product,
            qty,
            uom,
            order_date,
            target_currency=self.currency_id,
        )

        return price

    def _get_pricelist_price(self):
        """Compute the price given by the pricelist for the given line information.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self.pricelist_item_id
        order_date = self.order_id.date_order or fields.Date.today()
        product = self.product_id.with_context(**self._get_product_price_context())
        qty = self.product_uom_qty or 1.0
        uom = self.product_uom or self.product_id.uom_id

        price = pricelist_rule._compute_price(
            product, qty, uom, order_date, currency=self.currency_id)

        return price

    def _get_product_price_context(self):
        """Gives the context for product price computation.

        :return: additional context to consider extra prices from attributes in the base product price.
        :rtype: dict
        """
        self.ensure_one()
        res = {}

        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                ptav.price_extra and
                ptav not in self.product_id.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            res['no_variant_attributes_price_extra'] = tuple(no_variant_attributes_price_extra)

        return res

    @api.depends(
        "sale_lines.order_id.state",
        "sale_lines.blanket_order_line",
        "sale_lines.product_uom_qty",
        "sale_lines.product_uom",
        "sale_lines.qty_delivered",
        "sale_lines.qty_invoiced",
        "product_uom_qty",
        "product_uom",
    )
    def _compute_quantities(self):
        for line in self:
            sale_lines = line.sale_lines
            line.ordered_uom_qty = sum(
                sl.product_uom._compute_quantity(sl.product_uom_qty, line.product_uom)
                for sl in sale_lines
                if sl.order_id.state != "cancel" and sl.product_id == line.product_id
            )
            line.remaining_uom_qty = line.product_uom_qty - line.ordered_uom_qty
            line.remaining_qty = line.product_uom._compute_quantity(
                line.remaining_uom_qty, line.product_id.uom_id
            )

    @api.onchange('product_id', 'product_uom_qty')
    def onchange_product(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if self.product_id:
            name = self.product_id.name
            if not self.product_uom:
                self.product_uom = self.product_id.uom_id.id
            if self.order_id.partner_id and float_is_zero(
                    self.price_unit, precision_digits=precision
            ):
                self.price_unit = self._get_display_price(self.product_id)
            if self.product_id.code:
                name = "[{}] {}".format(name, self.product_id.code)
            if self.product_id.description_sale:
                name += "\n" + self.product_id.description_sale
            self.name = name

            fpos = self.order_id.fiscal_position_id

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get(
                    "display_type", self.default_get(["display_type"])["display_type"]
            ):
                values.update(product_id=False, price_unit=0, product_uom=False)

        return super().create(vals_list)

    def write(self, values):
        if "display_type" in values and self.filtered(
                lambda line: line.display_type != values.get("display_type")
        ):
            raise UserError(
                _(
                    """
                    You cannot change the type of a sale order line.
                    Instead you should delete the current line and create a new line
                    of the proper type.
                    """
                )
            )
        return super(BlanketOrderLine, self).write(values)

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     blanket_order_line = fields.Many2one('blanket.order.line', string="Blanket Order Line")
#
#     @api.onchange('order_id.partner_id')
#     def _onchange_partner_id(self):
#         if self.order_id.partner_id:
#             blanket_lines = self.env['blanket.order.line'].search([
#                 ('order_id.partner_id', '=', self.order_id.partner_id.id),
#                 ('order_id.state', '=', 'confirm'),
#             ])
#             product_ids = blanket_lines.mapped('product_id').ids
#             return {
#                 'domain': {
#                     'product_id': [('id', 'in', product_ids)]
#                 }
#             }
#         return {}
