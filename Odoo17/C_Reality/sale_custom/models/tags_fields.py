# -*- coding: utf-8 -*-
from random import randint

from odoo import api, fields, models
from odoo.osv import expression


class ProductColor(models.Model):
    _name = 'product.color'
    _description = 'Product Color'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Color Name', required=True, translate=True)
    product_template_ids = fields.Many2many('product.template', 'product_color_product_template_rel', string='Products')
    product_product_ids = fields.Many2many('product.product', 'product_color_product_product_rel',
                                           string='All Product Variants using this Color')
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Color name already exists !"),
    ]

    @api.depends('product_template_ids', 'product_product_ids')
    def _compute_product_ids(self):
        for color in self:
            color.product_product_ids = color.product_template_ids.product_variant_ids

    def _search_product_ids(self, operator, operand):
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return [('product_template_ids.product_variant_ids', operator, operand),
                    ('product_product_ids', operator, operand)]
        return ['|', ('product_template_ids.product_variant_ids', operator, operand),
                ('product_product_ids', operator, operand)]


class ProductFabric(models.Model):
    _name = 'product.fabric'
    _description = 'Product Fabric'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Fabric Name', required=True, translate=True)
    product_template_ids = fields.Many2many('product.template', 'product_fabric_product_template_rel',
                                            string='Products related to this Fabric')
    product_product_ids = fields.Many2many('product.product', 'product_fabric_product_product_rel',
                                           string='All Product Variants using this Fabric')
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Fabric name already exists !"),
    ]

    @api.depends('product_template_ids', 'product_product_ids')
    def _compute_product_ids(self):
        for fabric in self:
            fabric.product_product_ids = fabric.product_template_ids.product_variant_ids

    def _search_product_ids(self, operator, operand):
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return [('product_template_ids.product_variant_ids', operator, operand),
                    ('product_product_ids', operator, operand)]
        return ['|', ('product_template_ids.product_variant_ids', operator, operand),
                ('product_product_ids', operator, operand)]


# Adjusting the ProductGlass model
class ProductGlass(models.Model):
    _name = 'product.glass'
    _description = 'Product Glass'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Glass Type', required=True, translate=True)
    product_template_ids = fields.Many2many('product.template', 'product_glass_product_template_rel',
                                            string='Products related to this Glass')
    product_product_ids = fields.Many2many('product.product', 'product_glass_product_product_rel',
                                           string='All Product Variants using this Glass')
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Glass type already exists !"),
    ]

    @api.depends('product_template_ids', 'product_product_ids')
    def _compute_product_ids(self):
        for glass in self:
            glass.product_product_ids = glass.product_template_ids.product_variant_ids

    def _search_product_ids(self, operator, operand):
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return [('product_template_ids.product_variant_ids', operator, operand),
                    ('product_product_ids', operator, operand)]
        return ['|', ('product_template_ids.product_variant_ids', operator, operand),
                ('product_product_ids', operator, operand)]


class MaterialFinish(models.Model):
    _name = 'product.material'
    _description = 'Material Finish'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Material', required=True, translate=True)
    product_template_ids = fields.Many2many('product.template', 'product_material_product_template_rel',
                                            string='Products related to this Glass')
    product_product_ids = fields.Many2many('product.product', 'product_material_product_product_rel',
                                           string='All Product Variants using this Glass')
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Material type already exists !"),
    ]

    @api.depends('product_template_ids', 'product_product_ids')
    def _compute_product_ids(self):
        for material in self:
            material.product_product_ids = material.product_template_ids.product_variant_ids

    def _search_product_ids(self, operator, operand):
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return [('product_template_ids.product_variant_ids', operator, operand),
                    ('product_product_ids', operator, operand)]
        return ['|', ('product_template_ids.product_variant_ids', operator, operand),
                ('product_product_ids', operator, operand)]


class MrpProductionTag(models.Model):
    _name = 'mrp.production.tag'
    _description = 'MRP Production Tag'

    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class ProductMetalTag(models.Model):
    _name = 'product.metal.tag'
    _description = 'Product Metal Tag'

    name = fields.Char('Material', required=True, translate=True)
    color = fields.Integer('Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Metal tag name already exists!"),
    ]
