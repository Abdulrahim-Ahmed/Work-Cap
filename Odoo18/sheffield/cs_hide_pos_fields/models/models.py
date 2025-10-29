# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_minimal_view_action(self):
        """Get the action for minimal sales orders view - for POS integration"""
        try:
            # Get the view ID safely
            view = self.env.ref('cs_hide_pos_fields.view_sale_order_tree_minimal', raise_if_not_found=False)
            if not view:
                raise UserError("Minimal view not found")

            return {
                'name': 'Sales Orders (Minimal)',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'list,form',
                'views': [(view.id, 'list'), (False, 'form')],
                'target': 'current',
                'context': {},
                'domain': [],
            }
        except Exception as e:
            # Return standard action as fallback
            return {
                'name': 'Sales Orders',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'list,form',
                'target': 'current',
            }
        



class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_view_sale_orders_minimal(self):
        """
        Action to view sales orders in minimal format, filtered by customer if available
        """
        action = self.env['sale.order'].action_pos_minimal_orders()
        
        # Filter by customer if this POS order has one
        if self.partner_id:
            action['domain'] = [('partner_id', '=', self.partner_id.id)]
            action['context'] = dict(action.get('context', {}), default_partner_id=self.partner_id.id)
        
        return action
