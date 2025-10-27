from odoo import models
from collections import defaultdict

class ProductLocationReportXlsx(models.AbstractModel):
    _name = 'report.report_location_qty.product_location_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Product Location Report in XLSX'

    def generate_xlsx_report(self, workbook, data, wizard):
        # Fetch all products and warehouses once
        products = self.env['product.product'].search([('type', 'in', ['product', 'consu'])])
        warehouses = self.env['stock.warehouse'].search([])

        # Fetch all relevant stock quantities in a single query
        quant_domain = [
            ('product_id', 'in', products.ids),
            ('location_id.usage', '=', 'internal')
        ]
        quants = self.env['stock.quant'].search(quant_domain)

        # Aggregate quantities by product and warehouse
        quant_dict = defaultdict(float)
        for quant in quants:
            warehouse = self.env['stock.warehouse'].search([
                ('lot_stock_id', 'parent_of', quant.location_id.id)
            ], limit=1)
            if warehouse:
                key = (quant.product_id.id, warehouse.id)
                quant_dict[key] += quant.quantity

        # Prepare warehouse headers dynamically
        warehouse_headers = [wh.name for wh in warehouses]
        headers = ['Barcode', 'Reference', 'Product', 'Category'] + warehouse_headers + ['Total']

        # Create a worksheet
        sheet = workbook.add_worksheet('Product Location Qty')

        # Define formats
        bold_large = workbook.add_format({
            'bold': True,
            'bg_color': '#00008B',
            'color': '#FFFFFF',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_size': 17
        })
        bold = workbook.add_format({
            'bold': True,
            'bg_color': '#00008B',
            'color': '#FFFFFF',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_size': 13
        })
        center_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_size': 13
        })

        # Set the height for the header row
        sheet.set_row(0, 40)

        # Write headers
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, bold_large)

        # Write data
        row = 1
        for product in products:
            # Get product details
            barcode = product.barcode or ''
            reference = product.default_code or ''  # Internal Reference
            product_name = product.name
            category = product.categ_id.name or ''

            # Write product details
            sheet.write(row, 0, barcode, center_format)  # Barcode
            sheet.write(row, 1, reference, center_format)  # Reference (Internal Reference)
            sheet.write(row, 2, product_name, center_format)  # Product Name
            sheet.write(row, 3, category, center_format)  # Category

            # Calculate quantities per warehouse
            col = 4  # Start from the column after 'Category'
            total_qty = 0
            for warehouse in warehouses:
                key = (product.id, warehouse.id)
                qty = quant_dict.get(key, 0)
                sheet.write(row, col, qty, center_format)
                total_qty += qty
                col += 1

            # Write total quantity
            sheet.write(row, col, total_qty, center_format)
            row += 1

        # Adjust column widths dynamically based on header length
        for col_num in range(len(headers)):
            max_length = max(len(str(headers[col_num])), 20)
            sheet.set_column(col_num, col_num, max_length + 5)

        # Set row height for better readability
        for i in range(1, row + 1):
            sheet.set_row(i, 25)