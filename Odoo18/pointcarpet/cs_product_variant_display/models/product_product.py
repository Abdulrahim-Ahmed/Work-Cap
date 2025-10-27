# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    variant_display_name = fields.Char(
        string='Variant Display Name',
        compute='_compute_variant_display_name',
        store=True
    )

    @api.depends('name', 'default_code', 'product_template_variant_value_ids.name')
    def _compute_variant_display_name(self):
        """Compute variant display name with attributes"""
        for product in self:
            name = product.name or ''
            if product.default_code:
                name = f"[{product.default_code}] {name}"
            
            # Add variant attributes if any
            if product.product_template_variant_value_ids:
                variant_attrs = ', '.join([
                    value.name for value in product.product_template_variant_value_ids
                ])
                name = f"{name} ({variant_attrs})"
            
            product.variant_display_name = name