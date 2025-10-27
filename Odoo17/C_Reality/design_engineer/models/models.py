# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    engineer = fields.Char(string="Design Engineer", required=False, )