from odoo import models, fields
from odoo.exceptions import ValidationError
import base64
import io
import xlsxwriter


class OperationsReportWizard(models.TransientModel):
    _name = 'operations.report.wizard'
    _description = 'Operations Report Wizard'

    # Date filters
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    
    # Partner filters
    partner_id = fields.Many2one('res.partner', string='Customer')
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)])
    
    # Product filters
    product_id = fields.Many2one('product.product', string='Product')
    product_category_id = fields.Many2one('product.category', string='Product Category')
    
    # Transaction type filters
    include_sales = fields.Boolean(string='Include Sales Orders', default=True)
    include_purchases = fields.Boolean(string='Include Purchase Orders', default=True)
    include_invoices = fields.Boolean(string='Include Invoices', default=True)
    include_stock_moves = fields.Boolean(string='Include Stock Movements', default=True)
    
    # Status filters
    sale_states = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Sale Order State')
    
    purchase_states = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Purchase Order State')
    
    # Company and other filters
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    
    # Report options
    group_by_partner = fields.Boolean(string='Group by Partner', default=False)
    group_by_product = fields.Boolean(string='Group by Product', default=False)
    group_by_category = fields.Boolean(string='Group by Category', default=False)
    show_cost_analysis = fields.Boolean(string='Show Cost Analysis', default=True)
    show_profit_analysis = fields.Boolean(string='Show Profit Analysis', default=True)
    print_type = fields.Selection(
        [('pdf', 'PDF'), ('xlsx', 'Excel')],
        string='Print Type',
        default='xlsx',
        required=True,
    )
    show_sales_section = fields.Boolean(string='تقرير المبيعات', default=True)
    show_delivery_to_carrier_section = fields.Boolean(string='ما تم تسليمه لشركة الشحن', default=True)
    show_returns_section = fields.Boolean(string='القطع التي تم استرجاعها', default=True)
    show_delivery_to_customer_section = fields.Boolean(string='ما تم تسليمه للعملاء', default=True)
    show_daily_quotes_section = fields.Boolean(string='الطلبات الجديده (يومي)', default=True)

    def action_print_report(self):
        if not (
            self.show_sales_section
            or self.show_delivery_to_carrier_section
            or self.show_returns_section
            or self.show_delivery_to_customer_section
            or self.show_daily_quotes_section
        ):
            raise ValidationError('Please select at least one section to print.')
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'vendor_id': self.vendor_id.id if self.vendor_id else False,
            'product_id': self.product_id.id if self.product_id else False,
            'product_category_id': self.product_category_id.id if self.product_category_id else False,
            'company_id': self.company_id.id,
            'warehouse_id': self.warehouse_id.id if self.warehouse_id else False,
            'salesperson_id': self.salesperson_id.id if self.salesperson_id else False,
            'include_sales': self.include_sales,
            'include_purchases': self.include_purchases,
            'include_invoices': self.include_invoices,
            'include_stock_moves': self.include_stock_moves,
            'sale_states': self.sale_states,
            'purchase_states': self.purchase_states,
            'group_by_partner': self.group_by_partner,
            'group_by_product': self.group_by_product,
            'group_by_category': self.group_by_category,
            'show_cost_analysis': self.show_cost_analysis,
            'show_profit_analysis': self.show_profit_analysis,
        }
        return self.env.ref(
            'custom_operations_report.action_operations_report'
        ).report_action(self, data=data)

    def action_print_xlsx(self):
        self.ensure_one()
        if not (
            self.show_sales_section
            or self.show_delivery_to_carrier_section
            or self.show_returns_section
            or self.show_delivery_to_customer_section
            or self.show_daily_quotes_section
        ):
            raise ValidationError('Please select at least one section to print.')
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'vendor_id': self.vendor_id.id if self.vendor_id else False,
            'product_id': self.product_id.id if self.product_id else False,
            'product_category_id': self.product_category_id.id if self.product_category_id else False,
            'company_id': self.company_id.id,
            'warehouse_id': self.warehouse_id.id if self.warehouse_id else False,
            'salesperson_id': self.salesperson_id.id if self.salesperson_id else False,
            'include_sales': self.include_sales,
            'include_purchases': self.include_purchases,
            'include_invoices': self.include_invoices,
            'include_stock_moves': self.include_stock_moves,
            'sale_states': self.sale_states,
            'purchase_states': self.purchase_states,
            'group_by_partner': self.group_by_partner,
            'group_by_product': self.group_by_product,
            'group_by_category': self.group_by_category,
            'show_cost_analysis': self.show_cost_analysis,
            'show_profit_analysis': self.show_profit_analysis,
        }

        report_model = self.env['report.custom_operations_report.operations_report_template']
        sales_data = report_model._get_sales_data(data) if data.get('include_sales') else {'orders': []}

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Operations Report')

        header_format = workbook.add_format({'bold': True, 'border': 1})
        cell_format = workbook.add_format({'border': 1})
        num_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        percent_format = workbook.add_format({'border': 1, 'num_format': '0.0'})

        row = 0
        if self.show_sales_section:
            sheet.write(row, 0, 'تقرير المبيعات', header_format)
            row += 1
            headers = [
                'تاريخ الطلب',
                'رقم الاوردر',
                'عدد القطع',
                'قيمة الاوردر',
                'تكلفة القطع في الاوردر',
                'ربح المنتج',
                'هامش الربح %',
            ]
            for col, title in enumerate(headers):
                sheet.write(row, col, title, header_format)
            row += 1

            for entry in sales_data.get('orders', []):
                order = entry['order']
                non_service_lines = order.order_line.filtered(
                    lambda l: not l.display_type and l.product_id and l.product_id.type != 'service'
                )
                qty = sum(non_service_lines.mapped('product_uom_qty'))
                total = order.amount_total
                cost = 0.0
                for line in non_service_lines:
                    unit_cost = line.purchase_price if hasattr(line, 'purchase_price') else line.product_id.standard_price
                    cost += unit_cost * line.product_uom_qty
                margin = total - cost
                margin_pct = (margin / total * 100) if total else 0.0

                order_date = order.date_order or order.create_date
                sheet.write(row, 0, fields.Datetime.to_string(order_date) if order_date else '', cell_format)
                sheet.write(row, 1, order.name, cell_format)
                sheet.write_number(row, 2, qty, num_format)
                sheet.write_number(row, 3, total, num_format)
                sheet.write_number(row, 4, cost, num_format)
                sheet.write_number(row, 5, margin, num_format)
                sheet.write_number(row, 6, margin_pct, percent_format)
                row += 1

            row += 2

        if self.show_delivery_to_carrier_section:
            sheet.write(row, 0, 'ما تم تسليمه لشركة الشحن', header_format)
            row += 1
            headers = [
                'تاريخ التسليم',
                'رقم الاوردر',
                'عدد القطع',
                'اسم المنتج',
                'قيمة القطع',
                'حالة التسليم',
                'تكلفة المنتج في الاوردر',
                'ربح المنتج',
                'هامش الربح %',
            ]
            for col, title in enumerate(headers):
                sheet.write(row, col, title, header_format)
            row += 1

            for entry in sales_data.get('orders', []):
                order = entry['order']
                pickings = order.picking_ids.sorted('scheduled_date')
                if not pickings:
                    continue

                first_picking = pickings[:1]
                delivered_to_customer = pickings.filtered(
                    lambda p: p.state == 'done' and p.location_dest_id.usage == 'customer'
                )
                delivery_status = 'تم التسليم' if delivered_to_customer else 'لم يتم التسليم'
                delivery_date = first_picking.scheduled_date or first_picking.date_done

                non_service_lines = order.order_line.filtered(
                    lambda l: not l.display_type and l.product_id and l.product_id.type != 'service'
                )
                for line in non_service_lines:
                    moves = first_picking.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id)
                    qty = 0.0
                    if moves:
                        if 'quantity_done' in moves._fields:
                            qty = sum(moves.mapped('quantity_done'))
                        else:
                            qty = sum(moves.mapped('product_uom_qty'))
                    if not qty:
                        qty = line.product_uom_qty

                    value = line.price_subtotal
                    unit_cost = line.purchase_price if hasattr(line, 'purchase_price') else line.product_id.standard_price
                    cost = unit_cost * qty
                    # margin = value - cost
                    # margin_pct = (margin / value * 100) if value else 0.0
                    margin = line.margin
                    margin_pct = line.margin_percent * 100

                    sheet.write(row, 0, fields.Datetime.to_string(delivery_date) if delivery_date else '', cell_format)
                    sheet.write(row, 1, order.name, cell_format)
                    sheet.write_number(row, 2, qty, num_format)
                    sheet.write(row, 3, line.product_id.display_name, cell_format)
                    sheet.write_number(row, 4, value, num_format)
                    sheet.write(row, 5, delivery_status, cell_format)
                    sheet.write_number(row, 6, cost, num_format)
                    sheet.write_number(row, 7, margin, num_format)
                    sheet.write_number(row, 8, margin_pct, percent_format)
                    row += 1

            row += 2

        if self.show_returns_section:
            sheet.write(row, 0, 'القطع التي تم استرجاعها', header_format)
            row += 1
            headers = [
                'تاريخ الاستلام',
                'تاريخ الارجاع',
                'رقم الاوردر',
                'اسم المنتج',
                'عدد القطع',
                'قيمة القطع',
            ]
            for col, title in enumerate(headers):
                sheet.write(row, col, title, header_format)
            row += 1

            for entry in sales_data.get('orders', []):
                order = entry['order']
                return_pickings = order.picking_ids.filtered(
                    lambda p: p.location_id.usage == 'customer'
                    and p.location_dest_id.usage == 'internal'
                )
                if not return_pickings:
                    continue

                non_service_lines = order.order_line.filtered(
                    lambda l: not l.display_type and l.product_id and l.product_id.type != 'service'
                )
                for picking in return_pickings:
                    receipt_date = picking.scheduled_date
                    return_date = picking.date_done or picking.scheduled_date
                    for line in non_service_lines:
                        moves = picking.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id)
                        qty = 0.0
                        if moves:
                            if 'quantity_done' in moves._fields:
                                qty = sum(moves.mapped('quantity_done'))
                            else:
                                qty = sum(moves.mapped('product_uom_qty'))
                        if not qty:
                            continue

                        unit_price = (line.price_subtotal / line.product_uom_qty) if line.product_uom_qty else 0.0
                        value = unit_price * qty

                        sheet.write(row, 0, fields.Datetime.to_string(receipt_date) if receipt_date else '', cell_format)
                        sheet.write(row, 1, fields.Datetime.to_string(return_date) if return_date else '', cell_format)
                        sheet.write(row, 2, order.name, cell_format)
                        sheet.write(row, 3, line.product_id.display_name, cell_format)
                        sheet.write_number(row, 4, qty, num_format)
                        sheet.write_number(row, 5, value, num_format)
                        row += 1

            row += 2

        if self.show_delivery_to_customer_section:
            sheet.write(row, 0, 'ما تم تسليمه للعملاء', header_format)
            row += 1
            headers = [
                'تاريخ التسليم',
                'رقم الاوردر',
                'عدد القطع',
                'اسم المنتج',
                'قيمة القطع',
                'قيمة الشحن',
                'حالة التسليم',
            ]
            for col, title in enumerate(headers):
                sheet.write(row, col, title, header_format)
            row += 1

            for entry in sales_data.get('orders', []):
                order = entry['order']
                customer_pickings = order.picking_ids.filtered(
                    lambda p: p.location_dest_id.usage == 'customer' and p.state == 'done'
                ).sorted('scheduled_date')
                if not customer_pickings:
                    continue

                non_service_lines = order.order_line.filtered(
                    lambda l: not l.display_type and l.product_id and l.product_id.type != 'service'
                )
                for picking in customer_pickings:
                    delivery_status = 'تم التسليم' if picking.state == 'done' else 'لم يتم التسليم'
                    delivery_date = picking.scheduled_date or picking.date_done
                    delivery_lines = order.order_line.filtered(
                        lambda l: not l.display_type and getattr(l, 'is_delivery', False)
                    )
                    shipping_cost = sum(delivery_lines.mapped('price_total')) or 0.0

                    for line in non_service_lines:
                        moves = picking.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id)
                        qty = 0.0
                        if moves:
                            if 'quantity_done' in moves._fields:
                                qty = sum(moves.mapped('quantity_done'))
                            else:
                                qty = sum(moves.mapped('product_uom_qty'))
                        if not qty:
                            continue

                        unit_price = (line.price_subtotal / line.product_uom_qty) if line.product_uom_qty else 0.0
                        value = unit_price * qty

                        sheet.write(row, 0, fields.Datetime.to_string(delivery_date) if delivery_date else '', cell_format)
                        sheet.write(row, 1, order.name, cell_format)
                        sheet.write_number(row, 2, qty, num_format)
                        sheet.write(row, 3, line.product_id.display_name, cell_format)
                        sheet.write_number(row, 4, value, num_format)
                        sheet.write_number(row, 5, shipping_cost, num_format)
                    sheet.write(row, 6, delivery_status, cell_format)
                    row += 1

            row += 2

        if self.show_daily_quotes_section:
            sheet.write(row, 0, 'الطلبات الجديده (يومي)', header_format)
            row += 1
            headers = [
                'تاريخ الاوردر',
                'اسم العميل',
                'اسم المنتج',
                'عدد القطع',
                'عدد القطع المطلوبه',
                'العدد في محزن الاونلاين',
                'القطع المتاحه',
            ]
            for col, title in enumerate(headers):
                sheet.write(row, col, title, header_format)
            row += 1

            quotation_domain = [
                ('date_order', '>=', data['date_from']),
                ('date_order', '<=', data['date_to']),
                ('company_id', '=', data['company_id']),
                ('state', 'in', ['draft', 'sent']),
            ]
            if data.get('partner_id'):
                quotation_domain.append(('partner_id', '=', data['partner_id']))
            if data.get('salesperson_id'):
                quotation_domain.append(('user_id', '=', data['salesperson_id']))
            if data.get('warehouse_id'):
                quotation_domain.append(('warehouse_id', '=', data['warehouse_id']))

            quotations = self.env['sale.order'].search(quotation_domain)
            for order in quotations:
                location = order.warehouse_id.lot_stock_id if order.warehouse_id else False
                order_lines = order.order_line.filtered(
                    lambda l: not l.display_type and l.product_id and l.product_id.type != 'service'
                )
                if data.get('product_id'):
                    order_lines = order_lines.filtered(lambda l: l.product_id.id == data['product_id'])
                if data.get('product_category_id'):
                    order_lines = order_lines.filtered(
                        lambda l: l.product_id.categ_id.id == data['product_category_id']
                    )

                for line in order_lines:
                    product = line.product_id
                    stock_in_location = (
                        product.with_context(location=location.id).qty_available if location else product.qty_available
                    )
                    available_qty = (
                        product.with_context(warehouse=order.warehouse_id.id).qty_available
                        if order.warehouse_id
                        else product.qty_available
                    )

                    sheet.write(row, 0, fields.Datetime.to_string(order.date_order) if order.date_order else '', cell_format)
                    sheet.write(row, 1, order.partner_id.name or '', cell_format)
                    sheet.write(row, 2, product.display_name, cell_format)
                    sheet.write_number(row, 3, line.product_uom_qty, num_format)
                    sheet.write_number(row, 4, getattr(line, 'demand_qty', 0.0) or 0.0, num_format)
                    sheet.write_number(row, 5, stock_in_location, num_format)
                    sheet.write_number(row, 6, available_qty, num_format)
                    row += 1

            row += 2

        workbook.close()
        output.seek(0)
        file_content = base64.b64encode(output.read())

        attachment = self.env['ir.attachment'].create({
            'name': 'operations_report.xlsx',
            'type': 'binary',
            'datas': file_content,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
