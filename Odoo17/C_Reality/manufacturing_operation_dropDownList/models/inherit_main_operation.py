# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OperationName(models.Model):
    _inherit = 'mrp.routing.workcenter'

    name_new_opp = fields.Many2one('mrp.operation.name', string="Operation Name")

    @api.onchange('name_new_opp')
    def onchange_name_new_opp(self):
        self.name = self.name_new_opp.name_new_opp
