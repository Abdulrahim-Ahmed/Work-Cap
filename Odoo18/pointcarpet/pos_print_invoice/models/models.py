from odoo import models, api

#
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     @api.model
#     def create(self, vals_list):
#         """Override create to sync variant prices after creation"""
#         templates = super().create(vals_list)
#         for template in templates:
#             template.product_variant_ids._compute_variant_price_sync()
#         return templates
#
#     def write(self, vals):
#         """Override write to sync variant prices when template price changes"""
#         result = super().write(vals)
#         if 'list_price' in vals:
#             for template in self:
#                 template.product_variant_ids._compute_variant_price_sync()
#         return result
#
#
# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     # Make variant price always equal to template price
#     lst_price = models.fields.Float(
#         related='product_tmpl_id.list_price',
#         string='Sales Price',
#         readonly=False,
#         store=True
#     )
#
#     @api.depends('product_tmpl_id.list_price')
#     def _compute_variant_price_sync(self):
#         for product in self:
#             if product.product_tmpl_id:
#                 product.lst_price = product.product_tmpl_id.list_price

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoice_payment_widget(self):
        res = super()._get_invoice_payment_widget()
        if not res:
            return res

        content = res.get('content', [])
        for line in content:
            payment_id = line.get('payment_id')
            if payment_id:
                payment = self.env['account.payment'].browse(payment_id)

                # Default to journal name
                method_name = payment.journal_id.name if payment.journal_id else 'Unknown'

                # Try to find POS payment that created this account.payment
                pos_payment = self.env['pos.payment'].search([
                    ('amount', '=', payment.amount),
                    ('payment_date', '=', payment.date),
                    ('pos_order_id.account_move.id', '=', self.id)
                ], limit=1)

                if pos_payment and pos_payment.payment_method_id:
                    method_name = pos_payment.payment_method_id.name

                line['payment_method_name'] = method_name

        return res
