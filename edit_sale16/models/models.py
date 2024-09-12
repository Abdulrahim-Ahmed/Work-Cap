from odoo import models, fields, api, _


class EditSale(models.Model):
    _inherit = 'sale.order.line'
    _description = 'add_cost'

    total2 = fields.Float(string="total", compute="_compute_total2", readonly=False, store=True)
    list_price_copy = fields.Float(string="List Price Copy", related="product_id.list_price", readonly=True)
    price_unit_without_tax = fields.Float(string="Price without Tax", store=True, readonly=True,
                                          compute="_compute_price_unit_without_tax")

    cost = fields.Float(string="Cost", compute="_compute_cost", store=True, readonly=True)
    sale_max = fields.Integer(string="Max Price", related="company_id.sale_max_co", readonly=False)
    total_quotation_qty = fields.Float(string="T-Q", related="product_id.total_quotation_qty", readonly=True)
    #related="product_id.standard_price",

    @api.depends('product_id.standard_price')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.product_id.standard_price

    @api.constrains('price_unit', 'sale_max', 'sale_min')
    @api.onchange('price_unit')
    def _constrains_price_unit_er(self):
        for rec in self:
            if not rec.product_id or not rec.cost or not rec.sale_max:
                continue

            max_threshold = rec.cost * (1 + (rec.sale_max / 100))
            if rec.price_unit >= max_threshold:
                return {
                    'warning': {
                        'title': rec.company_id.warning_title or _("خطا فى سعر البيع ", ),
                        'message': rec.company_id.warning_message or _(
                            "برجاء الرجوع إلي سعر بيع المنتج  %s " % rec.product_template_id.name)
                    }
                }
            elif rec.price_unit <= rec.cost:
                return {
                    'warning': {
                        'title': rec.company_id.low_warning_title or _("خطا فى سعر البيع ", ),
                        'message': rec.company_id.low_warning_message or _(
                            "برجاء الرجوع إلي مشتريات سعر المنتج   %s " % rec.product_template_id.name)
                    }
                }

    @api.depends('price_unit', 'tax_id', 'product_uom_qty')
    def _compute_total2(self):
        for rec in self:
            tax_percentage = sum(tax.amount for tax in rec.tax_id)
            rec.total2 = rec.price_unit + (rec.price_unit * tax_percentage / 100)

    @api.depends('product_id', 'list_price_copy')
    def _compute_price_unit_without_tax(self):
        for rec in self:
            rec.price_unit_without_tax = rec.list_price_copy

    @api.onchange('total2')
    def _onchange_total2(self):
        tax_percentage = sum(tax.amount for tax in self.tax_id)
        self.price_unit = self.total2 / (1 + tax_percentage / 100)


# __________________________________________________________________________

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    num_quotations = fields.Integer(compute='_compute_num_quotations', string='Number of Quotations')
    total_quotation_qty = fields.Float(compute='_compute_total_quotation_qty', string='Total Quotation Quantity')
    responsible_id = fields.Many2one('res.users', string='Responsible', )

    def _compute_num_quotations(self):
        for product in self:
            num_quotations = self.env['sale.order'].search_count([('state', 'in', ('draft', 'sent')),
                                                                  ('order_line.product_id', '=',
                                                                   product.product_variant_id.id)])
            product.num_quotations = num_quotations

    def _compute_total_quotation_qty(self):
        for product in self:
            total_qty = 0.0
            quotations = self.env['sale.order'].search([('state', 'in', ('draft', 'sent')),
                                                        ('order_line.product_id', '=', product.product_variant_id.id)])
            for quotation in quotations:
                total_qty += sum(
                    quotation.order_line.filtered(lambda line: line.product_id == product.product_variant_id).mapped(
                        'product_uom_qty'))
            product.total_quotation_qty = total_qty
