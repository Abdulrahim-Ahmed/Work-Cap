# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from datetime import datetime


class PosOrderController(http.Controller):

    @http.route('/api/pos/payments', auth='public', methods=['GET'], type='http')
    def get_pos_orders(self, **kwargs):
        """
        API endpoint to fetch POS orders based on date range and config_id from query parameters (GET).
        Query Parameters: date_from, date_to, config_id
        Returns: JSON response with order details
        """
        try:
            # Extract parameters from query string
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            config_id = kwargs.get('config_id')

            # Validate required parameters
            if not all([date_from, date_to, config_id]):
                return self._error_response(
                    'Missing required parameters: date_from, date_to, and config_id are required.',
                    status=400
                )

            # Convert date strings to datetime objects
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                return self._error_response(
                    'Invalid date format. Use YYYY-MM-DD.',
                    status=400
                )

            # Ensure config_id is an integer
            try:
                config_id = int(config_id)
            except (ValueError, TypeError):
                return self._error_response(
                    'config_id must be an integer.',
                    status=400
                )

            # Build domain for search
            domain = [
                ('date_order', '>=', date_from),
                ('date_order', '<=', date_to),
                ('config_id', '=', config_id)
            ]

            # Search pos.order records
            pos_orders = request.env['pos.order'].sudo().search(domain)

            if not pos_orders:
                return self._success_response(
                    message='No orders found for the given criteria',
                    data=[]
                )

            # Prepare response data
            orders_data = [
                {
                    'order_ref': order.name,
                    'date': order.date_order.strftime('%Y-%m-%d %H:%M:%S'),
                    'total': order.amount_total,
                    'config_name': order.config_id.name
                }
                for order in pos_orders
            ]

            # Return successful response
            return self._success_response(
                message='Orders retrieved successfully',
                data=orders_data
            )

        except Exception as e:
            # Handle unexpected errors
            return self._error_response(
                f'An unexpected error occurred: {str(e)}',
                status=500
            )

    def _success_response(self, message, data):
        """Helper method to format a successful JSON response."""
        return request.make_response(
            json.dumps({
                'status': 'success',
                'message': message,
                'data': data
            }),
            headers={'Content-Type': 'application/json'}
        )

    def _error_response(self, message, status=400):
        """Helper method to format an error JSON response."""
        return request.make_response(
            json.dumps({
                'status': 'error',
                'message': message
            }),
            headers={'Content-Type': 'application/json'},
            status=status
        )
