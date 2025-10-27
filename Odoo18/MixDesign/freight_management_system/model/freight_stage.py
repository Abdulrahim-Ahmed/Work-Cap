from odoo import models, fields


class FreightOrderStage(models.Model):
    _name = 'freight.order.stage'
    _description = 'Freight Order Stage'
    # _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(string="Folded in Kanban")
    is_won = fields.Boolean(string="Won Stage")
    is_lost = fields.Boolean(string="Lost Stage")
