from odoo import models, fields, api


class FreightCycleLine(models.Model):
    _name = 'freight.management.line'
    _description = 'Freight Management Line'

    name = fields.Char(string='Name', required=True)
    assignees = fields.Many2one('res.users', string='Assignees', required=True, ondelete='cascade')
    freight_id = fields.Many2one('freight.management', string='Freight', ondelete='cascade')
    stage_id = fields.Many2one('project.task.type', string='Stage', required=True,
                               help='The stage where this task will be placed in the project')
