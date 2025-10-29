# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one('hr.employee', string='Salesperson')

    @api.model
    def _order_fields(self, ui_order):
        """Process order fields from UI, including salesperson data"""
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        
        # Handle salesperson_id from frontend
        if 'salesperson_id' in ui_order and ui_order['salesperson_id']:
            if isinstance(ui_order['salesperson_id'], dict) and 'id' in ui_order['salesperson_id']:
                order_fields['salesperson_id'] = ui_order['salesperson_id']['id']
            elif isinstance(ui_order['salesperson_id'], int):
                order_fields['salesperson_id'] = ui_order['salesperson_id']
        else:
            # If no salesperson is set from frontend, try to get from order lines
            # or fallback to session user's employee
            salesperson_from_lines = False
            if 'lines' in ui_order:
                for line_data in ui_order['lines']:
                    if len(line_data) >= 3 and isinstance(line_data[2], dict) and line_data[2].get('employee_id'):
                        salesperson_from_lines = line_data[2]['employee_id']
                        break
                        
            if salesperson_from_lines:
                order_fields['salesperson_id'] = salesperson_from_lines
            else:
                # Fallback to session user's employee
                session = self.env['pos.session'].browse(ui_order.get('pos_session_id'))
                if session and session.user_id:
                    employee = self.env['hr.employee'].search([('user_id', '=', session.user_id.id)], limit=1)
                    if employee:
                        order_fields['salesperson_id'] = employee.id
        
        return order_fields

    def _get_fields_for_order_line(self):
        """Include employee_id field for order line synchronization"""
        fields = super(PosOrder, self)._get_fields_for_order_line()
        fields.extend(['employee_id'])
        return fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    employee_id = fields.Many2one('hr.employee', string='Salesperson')

    def _export_for_ui(self, orderline):
        result = super(PosOrderLine, self)._export_for_ui(orderline)
        result['employee_id'] = orderline.employee_id.id if orderline.employee_id else False
        return result
