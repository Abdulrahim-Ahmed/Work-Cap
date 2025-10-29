# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OperationName(models.Model):
    _name = 'mrp.operation.name'
    _description = 'Operation Name'
    _rec_name = 'name_new_opp'

    name_new_opp = fields.Char(string="Operation Name")
    name = fields.Char(string='Operation Old')
