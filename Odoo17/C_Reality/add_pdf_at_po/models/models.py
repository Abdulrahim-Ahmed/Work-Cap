from odoo import models, fields, api


class AddPdfAtProductTemplate(models.Model):
    _inherit = 'product.template'

    product_attachment_template = fields.Binary(string="Product Attachment")
    product_attachment_template_name = fields.Char(string="Template Attachment Name")


class AddPdfAtProductProduct(models.Model):
    _inherit = 'product.product'

    product_attachment_product = fields.Binary(string="Product Attachment")
    product_attachment_product_name = fields.Char(string="Variant Attachment Name")


class AddPdfAtPurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    product_attachment = fields.Binary(string="Product Attachment")
    product_attachment_name = fields.Char(string="Attachment Name")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """When the product is selected, update the attachment from product or template"""
        if self.product_id:
            product_variant = self.product_id
            product_template = product_variant.product_tmpl_id

            # Check if the product variant has an attachment
            if product_variant.product_attachment_product:
                self.product_attachment = product_variant.product_attachment_product
                self.product_attachment_name = product_variant.product_attachment_product_name
            # Fallback to product template attachment if the variant has no attachment
            elif product_template.product_attachment_template:
                self.product_attachment = product_template.product_attachment_template
                self.product_attachment_name = product_template.product_attachment_template_name
            else:
                # Clear the attachment if neither product nor template has an attachment
                self.product_attachment = False
                self.product_attachment_name = ''
    #
    # @api.model
    # def create(self, vals):
    #     if 'product_attachment' in vals:
    #         vals.pop('product_attachment')  # Remove attachment upload capability
    #     return super(AddPdfAtPurchaseOrder, self).create(vals)
    #
    # def write(self, vals):
    #     if 'product_attachment' in vals:
    #         vals.pop('product_attachment')  # Remove attachment upload capability
    #     return super(AddPdfAtPurchaseOrder, self).write(vals)
