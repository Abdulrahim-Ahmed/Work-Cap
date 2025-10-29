# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    custom_company_id = fields.Many2many(
        'res.company',
        string='Company',
        index=True,
        help="Indicates the company this category belongs to."
    )


class PosCategory(models.Model):
    _inherit = 'pos.category'

    custom_company_id = fields.Many2many(
        'res.company',
        'pos_category_company_rel',
        'pos_category_id',
        'company_id',
        string='Company',
        index=True,
        help="Indicates the company this POS category belongs to."
    )


class ProductTemplateExtended(models.Model):
    _inherit = 'product.template'

    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, default=False, group_expand='_read_group_categ_id',
        required=True)
