# -*- coding: utf-8 -*-

from odoo import fields, models

class PosOrder(models.Model):
    """ The class PosOrder is used to inherit pos.order.line """
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one('hr.employee', string='Salesperson',
                              help="You can see salesperson here")

    def _order_fields(self, ui_order):
        result = super()._order_fields(ui_order)
        result['salesperson_id'] = ui_order.get('salesperson_id')
        return result