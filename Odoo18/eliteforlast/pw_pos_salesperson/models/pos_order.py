# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one('hr.employee', string='Salesperson')

    @api.model
    def _order_fields(self, ui_order):
        """Process order fields from UI, including salesperson data"""
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        
        # Check if any orderlines have individual assigned employees
        has_individual_employees = False
        all_same_employee = True
        first_employee_id = None
        
        if 'lines' in ui_order:
            employee_ids = set()
            for line_data in ui_order['lines']:
                if len(line_data) >= 3 and isinstance(line_data[2], dict):
                    line_employee_id = line_data[2].get('employee_id')
                    if line_employee_id:
                        has_individual_employees = True
                        employee_ids.add(line_employee_id)
                        if first_employee_id is None:
                            first_employee_id = line_employee_id
            
            # Check if all lines have the same employee
            all_same_employee = len(employee_ids) <= 1
        
        # Logic for setting salesperson_id on order level
        if has_individual_employees and all_same_employee and first_employee_id:
            # All lines have the same employee - set it on order level
            order_fields['salesperson_id'] = first_employee_id
        elif 'salesperson_id' in ui_order and ui_order['salesperson_id']:
            # Handle salesperson_id from frontend (old behavior)
            if isinstance(ui_order['salesperson_id'], dict) and 'id' in ui_order['salesperson_id']:
                order_fields['salesperson_id'] = ui_order['salesperson_id']['id']
            elif isinstance(ui_order['salesperson_id'], int):
                order_fields['salesperson_id'] = ui_order['salesperson_id']
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

    @api.model
    def create_from_ui(self, orders, draft=False):
        """Override to ensure employee data is properly processed"""
        # Process each order to ensure employee data is handled
        for order_data in orders:
            if 'data' in order_data and 'lines' in order_data['data']:
                for line_data in order_data['data']['lines']:
                    if isinstance(line_data, list) and len(line_data) >= 3:
                        line_vals = line_data[2]
                        if isinstance(line_vals, dict) and 'employee_id' in line_vals:
                            # Ensure employee_id is properly set
                            line_vals['employee_id'] = line_vals.get('employee_id')
        
        return super(PosOrder, self).create_from_ui(orders, draft)

    @api.depends('lines.employee_id')
    def _compute_has_mixed_employees(self):
        """Compute whether order has mixed employees across lines"""
        for order in self:
            employee_ids = order.lines.mapped('employee_id.id')
            # Remove False/None values
            employee_ids = [emp_id for emp_id in employee_ids if emp_id]
            
            # Has mixed employees if more than one unique employee
            order.has_mixed_employees = len(set(employee_ids)) > 1

    has_mixed_employees = fields.Boolean(
        string='Has Mixed Employees',
        compute='_compute_has_mixed_employees',
        store=True,
        help="True if different order lines have different assigned employees"
    )


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    employee_id = fields.Many2one('hr.employee', string='Salesperson')

    @api.model
    def _order_line_fields(self, line):
        """Override to ensure employee_id is saved"""
        result = super(PosOrderLine, self)._order_line_fields(line)
        
        # Debug logging
        print(f"=== POS SALESPERSON DEBUG: Processing line data: {line}")
        
        # Handle employee_id from UI
        if isinstance(line, list) and len(line) >= 3:
            line_data = line[2]
            if isinstance(line_data, dict) and 'employee_id' in line_data:
                result['employee_id'] = line_data['employee_id']
                print(f"=== POS SALESPERSON DEBUG: Set employee_id from list: {line_data['employee_id']}")
        elif isinstance(line, dict) and 'employee_id' in line:
            result['employee_id'] = line['employee_id']
            print(f"=== POS SALESPERSON DEBUG: Set employee_id from dict: {line['employee_id']}")
            
        print(f"=== POS SALESPERSON DEBUG: Final line fields: {result}")
        return result

    def _export_for_ui(self, orderline):
        result = super(PosOrderLine, self)._export_for_ui(orderline)
        result['employee_id'] = orderline.employee_id.id if orderline.employee_id else False
        result['employee_name'] = orderline.employee_id.name if orderline.employee_id else False
        return result
