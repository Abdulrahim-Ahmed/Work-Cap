# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, exceptions, api, _
from datetime import datetime
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm_inherit(self):
        context = dict(self._context or {})
        data_obj = self.env['ir.model.data']

        return {
            'name': "Select Confirmation Date",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'confirmation.wizard',
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
        }


class ConfirmDateWizard(models.TransientModel):
    _name = 'confirmation.wizard'
    _description = 'Confirmation Date Wizard'

    confirmation_date = fields.Datetime(string='Confirm Date', index=True,
                                              help="Date on which the sales order is confirmed.", copy=False)

    def action_confirm(self):
        context = dict(self._context) or {}
        if context.get('active_id', False):
            sale_obj = self.env['sale.order'].browse(context.get('active_id'))
            sale_obj.action_confirm()
            if self.confirmation_date:
                sale_obj.date_order = self.confirmation_date
            picking = self.env['stock.picking'].search([('sale_id', '=', sale_obj.id), ('state', 'not in', ['cancel'])])
            if not sale_obj.commitment_date:
                for pic in picking:
                    if self.confirmation_date:
                        picking.scheduled_date = self.confirmation_date

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
