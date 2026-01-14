# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime
from collections import defaultdict


class ReportOperations(models.AbstractModel):
    _name = 'report.custom_operations_report.operations_report_template'
    _description = 'Comprehensive Operations Report PDF'

    def _get_report_values(self, docids, data=None):
        report_data = []
        summary_data = {}

        # Initialize summary counters
        summary_data = {
            'total_sales_amount': 0.0,
            'total_purchase_amount': 0.0,
            'total_cost': 0.0,
            'total_profit': 0.0,
            'total_invoiced': 0.0,
            'total_paid': 0.0,
            'total_qty_sold': 0.0,
            'total_qty_purchased': 0.0,
            'total_stock_moves': 0,
            'currency_symbol': self.env.company.currency_id.symbol,
        }

        # Initialize data containers
        sales_data = {
            'summary': {'total_cost': 0.0, 'total_profit': 0.0, 'total_amount': 0.0, 'total_qty': 0.0, 'count': 0}}
        purchase_data = {'summary': {'total_amount': 0.0, 'total_qty': 0.0, 'count': 0}}

        # Sales Orders Analysis
        if data.get('include_sales', True):
            sales_data = self._get_sales_data(data)
            report_data.extend(sales_data['orders'])
            summary_data.update({
                'total_sales_amount': sales_data['summary']['total_amount'],
                'total_qty_sold': sales_data['summary']['total_qty'],
                'sales_count': sales_data['summary']['count'],
            })

        # Purchase Orders Analysis
        if data.get('include_purchases', True):
            purchase_data = self._get_purchase_data(data)
            report_data.extend(purchase_data['orders'])
            summary_data.update({
                'total_purchase_amount': purchase_data['summary']['total_amount'],
                'total_qty_purchased': purchase_data['summary']['total_qty'],
                'purchase_count': purchase_data['summary']['count'],
            })

        # Invoice Analysis
        if data.get('include_invoices', True):
            invoice_data = self._get_invoice_data(data)
            summary_data.update({
                'total_invoiced': invoice_data['total_invoiced'],
                'total_paid': invoice_data['total_paid'],
                'invoice_count': invoice_data['count'],
            })

        # Stock Movement Analysis
        if data.get('include_stock_moves', True):
            stock_data = self._get_stock_data(data)
            summary_data.update({
                'total_stock_moves': stock_data['total_moves'],
                'stock_in': stock_data['stock_in'],
                'stock_out': stock_data['stock_out'],
            })

        # Calculate final totals for profit calculation
        summary_data['total_cost'] = sales_data.get('summary', {}).get('total_cost', 0.0) if data.get('include_sales',
                                                                                                      True) else 0.0
        summary_data['total_profit'] = sales_data.get('summary', {}).get('total_profit', 0.0) if data.get(
            'include_sales', True) else 0.0

        # Calculate profit margins
        if summary_data['total_sales_amount'] > 0:
            summary_data['profit_margin'] = (summary_data['total_profit'] / summary_data['total_sales_amount']) * 100
        else:
            summary_data['profit_margin'] = 0.0

        return {
            'docs': report_data,
            'report_data': report_data,
            'summary': summary_data,
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'filters': data,
            'company': self.env.company,
            'o': self.env.company,
        }

    def _get_sales_data(self, data):
        SaleOrder = self.env['sale.order']

        # Build domain for sales orders
        domain = [
            ('date_order', '>=', data['date_from']),
            ('date_order', '<=', data['date_to']),
            ('company_id', '=', data['company_id'])
        ]

        # Add filters
        if data.get('partner_id'):
            domain.append(('partner_id', '=', data['partner_id']))
        if data.get('salesperson_id'):
            domain.append(('user_id', '=', data['salesperson_id']))
        if data.get('sale_states'):
            domain.append(('state', '=', data['sale_states']))
        else:
            domain.append(('state', 'in', ['sale', 'done']))
        if data.get('warehouse_id'):
            domain.append(('warehouse_id', '=', data['warehouse_id']))

        orders = SaleOrder.search(domain)

        report_orders = []
        total_amount = total_qty = total_cost = total_profit = 0.0

        for order in orders:
            order_total_cost = order_total_profit = 0.0
            lines_data = []

            for line in order.order_line:
                # Apply product filters if specified
                if data.get('product_id') and line.product_id.id != data['product_id']:
                    continue
                if data.get('product_category_id') and line.product_id.categ_id.id != data['product_category_id']:
                    continue

                # Calculate costs and profits
                standard_cost = line.product_id.standard_price
                line_cost = standard_cost * line.qty_delivered
                line_profit = line.price_subtotal - line_cost

                order_total_cost += line_cost
                order_total_profit += line_profit

                lines_data.append({
                    'type': 'sale',
                    'product_name': line.product_id.display_name,
                    'product_code': line.product_id.default_code or '',
                    'product_category': line.product_id.categ_id.name,
                    'ordered_qty': line.product_uom_qty,
                    'delivered_qty': line.qty_delivered,
                    'invoiced_qty': line.qty_invoiced,
                    'unit_price': line.price_unit,
                    'subtotal': line.price_subtotal,
                    'discount': line.discount,
                    'cost': line_cost,
                    'profit': line_profit,
                    'profit_margin': (line_profit / line.price_subtotal * 100) if line.price_subtotal > 0 else 0,
                    'uom': line.product_uom.name,
                    'tax_amount': sum(line.tax_id.mapped('amount')),
                })

            total_amount += order.amount_total
            total_qty += sum(order.order_line.mapped('product_uom_qty'))
            total_cost += order_total_cost
            total_profit += order_total_profit

            report_orders.append({
                'type': 'sale',
                'order': order,
                'lines': lines_data,
                'total_cost': order_total_cost,
                'total_profit': order_total_profit,
                'profit_margin': (order_total_profit / order.amount_total * 100) if order.amount_total > 0 else 0,
                'partner_name': order.partner_id.name,
                'partner_phone': order.partner_id.phone or '',
                'partner_email': order.partner_id.email or '',
                'salesperson': order.user_id.name,
                'payment_terms': order.payment_term_id.name if order.payment_term_id else '',
                'delivery_status': order.delivery_status if hasattr(order, 'delivery_status') else '',
                'invoice_status': order.invoice_status,
                'reference': order.client_order_ref or '',
                'warehouse': order.warehouse_id.name if order.warehouse_id else '',
            })

        return {
            'orders': report_orders,
            'summary': {
                'total_amount': total_amount,
                'total_qty': total_qty,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'count': len(orders)
            }
        }

    def _get_purchase_data(self, data):
        PurchaseOrder = self.env['purchase.order']

        domain = [
            ('date_order', '>=', data['date_from']),
            ('date_order', '<=', data['date_to']),
            ('company_id', '=', data['company_id'])
        ]

        if data.get('vendor_id'):
            domain.append(('partner_id', '=', data['vendor_id']))
        if data.get('purchase_states'):
            domain.append(('state', '=', data['purchase_states']))
        else:
            domain.append(('state', 'in', ['purchase', 'done']))

        orders = PurchaseOrder.search(domain)

        report_orders = []
        total_amount = total_qty = 0.0

        for order in orders:
            lines_data = []

            for line in order.order_line:
                if data.get('product_id') and line.product_id.id != data['product_id']:
                    continue
                if data.get('product_category_id') and line.product_id.categ_id.id != data['product_category_id']:
                    continue

                lines_data.append({
                    'type': 'purchase',
                    'product_name': line.product_id.display_name,
                    'product_code': line.product_id.default_code or '',
                    'product_category': line.product_id.categ_id.name,
                    'ordered_qty': line.product_qty,
                    'received_qty': line.qty_received,
                    'invoiced_qty': line.qty_invoiced,
                    'unit_price': line.price_unit,
                    'subtotal': line.price_subtotal,
                    'uom': line.product_uom.name,
                })

            total_amount += order.amount_total
            total_qty += sum(order.order_line.mapped('product_qty'))

            report_orders.append({
                'type': 'purchase',
                'order': order,
                'lines': lines_data,
                'partner_name': order.partner_id.name,
                'partner_phone': order.partner_id.phone or '',
                'partner_email': order.partner_id.email or '',
                'reference': order.partner_ref or '',
                'payment_terms': order.payment_term_id.name if order.payment_term_id else '',
                'invoice_status': order.invoice_status,
            })

        return {
            'orders': report_orders,
            'summary': {
                'total_amount': total_amount,
                'total_qty': total_qty,
                'count': len(orders)
            }
        }

    def _get_invoice_data(self, data):
        AccountMove = self.env['account.move']

        domain = [
            ('invoice_date', '>=', data['date_from']),
            ('invoice_date', '<=', data['date_to']),
            ('company_id', '=', data['company_id']),
            ('move_type', 'in', ['out_invoice', 'in_invoice']),
            ('state', '=', 'posted')
        ]

        if data.get('partner_id'):
            domain.append(('partner_id', '=', data['partner_id']))

        invoices = AccountMove.search(domain)

        total_invoiced = sum(invoices.mapped('amount_total'))
        total_paid = sum(invoices.filtered(lambda inv: inv.payment_state == 'paid').mapped('amount_total'))

        return {
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'count': len(invoices)
        }

    def _get_stock_data(self, data):
        StockMove = self.env['stock.move']

        domain = [
            ('date', '>=', data['date_from']),
            ('date', '<=', data['date_to']),
            ('company_id', '=', data['company_id']),
            ('state', '=', 'done')
        ]

        if data.get('product_id'):
            domain.append(('product_id', '=', data['product_id']))
        if data.get('warehouse_id'):
            warehouse = self.env['stock.warehouse'].browse(data['warehouse_id'])
            location_ids = warehouse.view_location_id.child_ids.ids + [warehouse.view_location_id.id]
            domain.append(('|'))
            domain.append(('location_id', 'in', location_ids))
            domain.append(('location_dest_id', 'in', location_ids))

        moves = StockMove.search(domain)

        stock_in = sum(moves.filtered(lambda m: m.location_dest_id.usage == 'internal').mapped('product_qty'))
        stock_out = sum(moves.filtered(lambda m: m.location_id.usage == 'internal').mapped('product_qty'))

        return {
            'total_moves': len(moves),
            'stock_in': stock_in,
            'stock_out': stock_out
        }
