# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'


    def action_confirm(self):
        if self.env.context.get('wizard_confirmed'):
            # If the wizard has already confirmed the order, proceed with the standard process
            return super(SaleOrderInherit, self).action_confirm()

        date_order_date = fields.Date.from_string(self.date_order) if self.date_order else None
        if not date_order_date or date_order_date <= fields.Date.today():
            view = self.env.ref('last_date_sale_order.view_sale_order_date_wizard_form')
            return {
                'name': 'Change Order Date',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.date.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': {'default_sale_order_id': self.id},
            }
        else:
            return super(SaleOrderInherit, self).action_confirm()

    def _prepare_confirmation_values(self):
        confirmation_values = super(SaleOrderInherit, self)._prepare_confirmation_values()
        if self.date_order:
            confirmation_values['date_order'] = self.date_order
        return confirmation_values