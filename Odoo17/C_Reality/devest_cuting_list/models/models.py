# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpProductionCutting(models.Model):
    _inherit = 'mrp.bom'
    cutting_list_ids = fields.One2many('cutting.list', 'prp_bom_id', string="Cutting List", copy=True)

class MrpCutting(models.Model):
    _inherit = 'mrp.production'

    cutting_mrp_ids = fields.One2many(
        'cutting.list', 'mrp_production_id', string="Cutting List",
        compute='_compute_cutting_list', store=True, copy=True)

    @api.depends('bom_id.cutting_list_ids')
    def _compute_cutting_list(self):
        for production in self:
            production.cutting_mrp_ids = production.bom_id.cutting_list_ids
            for line in production.cutting_mrp_ids:
                line.total = production.product_qty * line.per_piece


class CuttingList(models.Model):
    _name = 'cutting.list'

    prp_bom_id = fields.Many2one('mrp.bom')
    mrp_production_id = fields.Many2one('mrp.production')
    per_piece = fields.Integer(string="Per Piece", required=False)
    height_cut = fields.Integer(string="Height Cut", required=False)
    width_cut = fields.Integer(string="Width Cut", required=False)
    width_final = fields.Integer(string="Height Final", required=False)
    height_final = fields.Integer(string="Width Final", required=False)
    letter = fields.Integer(string="Curve", required=False)
    quora = fields.Integer(string="Quora", required=False)
    thickness = fields.Integer(string="Thickness.C", required=False)
    thickness_2 = fields.Integer(string="Thickness.F", required=False)
    thickness_3 = fields.Integer(string="Thickness.T", required=False)
    item_name = fields.Char(string="Item Name", required=False)
    material = fields.Char(string="Material", required=False)
    material_wood = fields.Char(string="Wood Material", required=False)
    total = fields.Integer(string="Total", required=False, compute='_compute_line_total', store=True)
    notes = fields.Char(string="Notes", required=False)

    @api.depends('mrp_production_id.product_qty', 'per_piece')
    def _compute_line_total(self):
        for line in self:
            if line.mrp_production_id:
                line.total = line.mrp_production_id.product_qty * line.per_piece
