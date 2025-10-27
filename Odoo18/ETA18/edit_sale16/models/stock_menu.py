from odoo import models, fields, api, _


class CustomStock(models.Model):
    _inherit = 'stock.picking'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_user(self):
        return self.env.uid

    user_id = fields.Many2one('res.users', string='Salesperson', default=_default_user)
