# -*- coding: utf-8 -*-
from odoo import models, api
from collections import defaultdict


class PosSessionSalesDetailsReport(models.AbstractModel):
    _name = 'report.point_of_sale.report_saledetails'
    _inherit = 'report.point_of_sale.report_saledetails'
    _description = 'Point of Sale Sales Details Report with Salesperson'

    def _get_salesperson_data(self, sessions):
        """
        Get salesperson statistics for the given sessions
        Returns: dict with salesperson info and their orders/totals
        """
        if not sessions:
            return {}

        # Get all orders for these sessions
        orders = self.env['pos.order'].search([
            ('session_id', 'in', sessions.ids),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])

        if not orders:
            return {}

        # Group orders by salesperson
        salesperson_data = defaultdict(lambda: {
            'name': '',
            'employee_id': False,
            'orders': [],
            'total_amount': 0.0,
            'total_qty': 0.0,
            'order_count': 0,
        })

        for order in orders:
            # Determine salesperson - prioritize different sources
            salesperson = None
            salesperson_name = ''

            # 1. Check order level salesperson_id first
            if hasattr(order, 'salesperson_id') and order.salesperson_id:
                salesperson = order.salesperson_id.id
                salesperson_name = order.salesperson_id.name
            else:
                # 2. Check if any order line has an employee_id
                for line in order.lines:
                    if hasattr(line, 'employee_id') and line.employee_id:
                        salesperson = line.employee_id.id
                        salesperson_name = line.employee_id.name
                        break

                # 3. Fallback to session user's linked employee
                if not salesperson and order.session_id.user_id:
                    user_employee = self.env['hr.employee'].search([
                        ('user_id', '=', order.session_id.user_id.id)
                    ], limit=1)
                    if user_employee:
                        salesperson = user_employee.id
                        salesperson_name = user_employee.name

                # 4. Final fallback: use session user name
                if not salesperson:
                    salesperson = f"user_{order.session_id.user_id.id}"
                    salesperson_name = order.session_id.user_id.name or 'Unknown User'

            # Add order data to salesperson
            sp_data = salesperson_data[salesperson]
            sp_data['name'] = salesperson_name
            sp_data['employee_id'] = salesperson if isinstance(salesperson, int) else False
            sp_data['orders'].append({
                'name': order.name,
                'date': order.date_order,
                'amount_total': order.amount_total,
                'amount_paid': order.amount_paid,
                'lines_count': len(order.lines),
            })
            sp_data['total_amount'] += order.amount_total
            sp_data['total_qty'] += sum(line.qty for line in order.lines)
            sp_data['order_count'] += 1

        # Convert to list and sort by total amount (descending)
        salesperson_list = []
        total_orders = 0
        total_amount = 0.0

        for sp_id, sp_data in salesperson_data.items():
            salesperson_list.append({
                'salesperson_id': sp_data['employee_id'],
                'name': sp_data['name'],
                'orders': sp_data['orders'],
                'total_amount': sp_data['total_amount'],
                'total_qty': sp_data['total_qty'],
                'order_count': sp_data['order_count'],
            })
            total_orders += sp_data['order_count']
            total_amount += sp_data['total_amount']

        # Sort by total amount descending
        salesperson_list.sort(key=lambda x: x['total_amount'], reverse=True)

        return {
            'salespeople': salesperson_list,
            'total_orders': total_orders,
            'total_amount': total_amount,
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        # Get parent report values
        result = super()._get_report_values(docids, data)

        # Get sessions
        sessions = self.env['pos.session']
        if docids:
            sessions = sessions.browse(docids)
        elif data and data.get('date_start') and data.get('date_stop'):
            # Get sessions based on date range
            domain = [
                ('start_at', '>=', data['date_start']),
                ('start_at', '<=', data['date_stop']),
                ('state', 'in', ['opened', 'closing_control', 'closed']),
            ]
            if data.get('config_ids'):
                domain.append(('config_id', 'in', data['config_ids']))
            sessions = self.env['pos.session'].search(domain)

        # Add salesperson data to the result
        if sessions:
            salesperson_data = self._get_salesperson_data(sessions)
            result.update({
                'salesperson_data': salesperson_data,
                'has_salesperson_data': bool(salesperson_data.get('salespeople')),
            })
        else:
            # Even if no sessions, set empty data to avoid template errors
            result.update({
                'salesperson_data': {'salespeople': [], 'total_orders': 0, 'total_amount': 0.0},
                'has_salesperson_data': False,
            })

        return result