from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # def open_custom_statement(self):
    #     # Replace this with your custom logic or action
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Custom Statement',
    #         'res_model': 'res.partner',
    #         'view_mode': 'tree,form',
    #         'target': 'current',
    #         'domain': [('partner_id', '=', self.id)],
    #     }
