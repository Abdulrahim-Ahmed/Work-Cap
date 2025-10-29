# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    move_raw_components = fields.Char(
        string='Component Names',
        compute='_compute_move_raw_components',
        store=True
    )

    @api.depends('move_raw_ids.product_id')
    def _compute_move_raw_components(self):
        for production in self:
            component_names = production.move_raw_ids.mapped('product_id.name')
            production.move_raw_components = ', '.join(component_names)
