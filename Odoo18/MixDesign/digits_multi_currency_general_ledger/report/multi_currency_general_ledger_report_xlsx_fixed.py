# -*- coding: utf-8 -*-
###############################################################################
#
#    Digital Integrated Transformation Solutions (DigitsCode)
#    Copyright (C) 2025-TODAY Digital Integrated Transformation Solutions (<https://www.digitscode.com>).
#    Author: Digital Integrated Transformation Solutions (<https://www.digitscode.com>)
#
###############################################################################

from odoo import models
import logging
import traceback
import json
from datetime import datetime

_logger = logging.getLogger(__name__)


class MultiCurrencyGeneralLedgerXlsx(models.AbstractModel):
    _name = 'report.digits_multi_currency_general_ledger.mcgl_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Multi Currency General Ledger XLSX Report'

    def generate_xlsx_report(self, workbook, data, objects):
        """Generate Excel report with basic error handling"""
        _logger.info("Starting XLSX report generation with data: %s", data)
        
        try:
            # Extract data from js_data format if exists
            if data and 'js_data' in data:
                try:
                    data = json.loads(data['js_data'])
                    _logger.info("Successfully parsed js_data")
                except Exception as e:
                    _logger.error("Error parsing js_data: %s", e)
                    data = {}
            
            # Get report data
            form = data.get('form', {}) if data else {}
            
            # Get main report data
            report_data = self._get_report_data(form)
            
            # Create worksheet
            sheet = workbook.add_worksheet('General Ledger')
            
            # Create formats
            formats = self._create_formats(workbook)
            
            # Set column widths
            self._set_column_widths(sheet)
            
            # Write report header
            self._write_report_header(sheet, form, report_data, formats)
            
            # Write account data
            self._write_account_data(sheet, report_data, form, formats)
            
            _logger.info("XLSX report generated successfully")
            
        except Exception as e:
            _logger.error("Error generating XLSX report: %s\n%s", str(e), traceback.format_exc())
            # Create an error sheet
            sheet = workbook.add_worksheet('Error')
            sheet.write(0, 0, 'An error occurred while generating the report:')
            sheet.write(1, 0, str(e))
            sheet.write(3, 0, 'Please contact support with the following technical details:')
            sheet.write(4, 0, traceback.format_exc())
    
    def _get_report_data(self, form):
        """Get report data using the same method as the PDF report"""
        _logger.info("Getting report data for XLSX report")
        try:
            # Convert dates from string to datetime if needed
            if isinstance(form.get('date_from'), str):
                try:
                    form['date_from'] = datetime.strptime(form['date_from'], '%Y-%m-%d').date()
                except ValueError as e:
                    _logger.error("Error converting date_from: %s", e)
                    
            if isinstance(form.get('date_to'), str):
                try:
                    form['date_to'] = datetime.strptime(form['date_to'], '%Y-%m-%d').date()
                except ValueError as e:
                    _logger.error("Error converting date_to: %s", e)
                
            # Create data for the report
            data = {'form': form}
            
            # Get data from the report model
            report = self.env['report.digits_multi_currency_general_ledger.mcgl_pdf']
            result = report._get_report_values([], data)
            _logger.info("Successfully retrieved report data")
            return result
        except Exception as e:
            _logger.error("Error getting report data: %s\n%s", str(e), traceback.format_exc())
            # Return minimal data in case of error
            return {
                'docs': self.env['account.account'].browse(form.get('account_ids', [])),
                'currencies': self.env['res.currency'].browse(form.get('currency_ids', [])),
                'results': {},
                'form': form,
                'company': self.env['res.company'].browse(form.get('company_id', self.env.company.id)),
            }
    
    def _create_formats(self, workbook):
        """Create formats for the report"""
        # Create and assign formats
        formats = {
            'date': workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'border': 1,
            }),
            
            'header': workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#D3D3D3',
                'border': 1,
            }),
            
            'subheader': workbook.add_format({
                'bold': True,
                'bg_color': '#E6E6E6',
                'border': 1,
            }),
            
            'account_info': workbook.add_format({
                'italic': True,
                'text_wrap': True,
            }),
            
            'account_info_label': workbook.add_format({
                'bold': True,
                'italic': True,
            }),
            
            'number': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
            }),
            
            'total': workbook.add_format({
                'bold': True,
                'num_format': '#,##0.00',
                'border': 1,
                'bg_color': '#F2F2F2',
            }),
            
            'cell': workbook.add_format({
                'border': 1,
            }),
        }
        
        return formats
    
    def _set_column_widths(self, sheet):
        """Set column widths for the report"""
        sheet.set_column(0, 0, 12)  # Date
        sheet.set_column(1, 1, 15)  # Journal
        sheet.set_column(2, 2, 15)  # Partner
        sheet.set_column(3, 3, 30)  # Description
        sheet.set_column(4, 4, 15)  # Debit
        sheet.set_column(5, 5, 15)  # Credit
        sheet.set_column(6, 6, 15)  # Balance
        sheet.set_column(7, 7, 15)  # Currency
        sheet.set_column(8, 8, 15)  # Amount Currency
    
    def _write_report_header(self, sheet, form, report_data, formats):
        """Write the report header"""
        company = report_data.get('company')
        
        # Company name
        sheet.merge_range('A1:I1', company.name, formats['header'])
        
        # Report title
        sheet.merge_range('A2:I2', 'Multi Currency General Ledger', formats['header'])
        
        # Date range
        date_from = form.get('date_from')
        date_to = form.get('date_to')
        
        if date_from and date_to:
            if isinstance(date_from, str):
                try:
                    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                except ValueError:
                    date_from = None
                    
            if isinstance(date_to, str):
                try:
                    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                except ValueError:
                    date_to = None
                    
            if date_from and date_to:
                date_range = f"From {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}"
                sheet.merge_range('A3:I3', date_range, formats['subheader'])
        
        # Header row
        row = 5
        sheet.write(row, 0, 'Date', formats['header'])
        sheet.write(row, 1, 'Journal', formats['header'])
        sheet.write(row, 2, 'Partner', formats['header'])
        sheet.write(row, 3, 'Description', formats['header'])
        sheet.write(row, 4, 'Debit', formats['header'])
        sheet.write(row, 5, 'Credit', formats['header'])
        sheet.write(row, 6, 'Balance', formats['header'])
        sheet.write(row, 7, 'Currency', formats['header'])
        sheet.write(row, 8, 'Amount Currency', formats['header'])
    
    def _write_account_data(self, sheet, report_data, form, formats):
        """Write account data to the sheet"""
        row = 6
        results = report_data.get('results', {})
        show_init_balance = form.get('show_init_balance', False)
        
        for account_id, account_data in results.items():
            account = account_data.get('account')
            if not account:
                continue
                
            # Account header
            row += 1
            sheet.merge_range(f'A{row+1}:I{row+1}', f"{account.code} - {account.name}", formats['subheader'])
            row += 1
            
            # Currency data
            for currency_id, currency_data in account_data.get('currencies', {}).items():
                currency = currency_data.get('currency')
                if not currency:
                    continue
                    
                # Currency header
                row += 1
                sheet.merge_range(f'A{row+1}:I{row+1}', f"Currency: {currency.name}", formats['account_info'])
                row += 1
                
                # Initial balance
                if show_init_balance:
                    init_balance = currency_data.get('init_balance', 0.0)
                    sheet.write(row, 0, 'Initial Balance', formats['cell'])
                    sheet.merge_range(f'B{row+1}:F{row+1}', '', formats['cell'])
                    sheet.write(row, 6, init_balance, formats['number'])
                    sheet.write(row, 7, currency.name, formats['cell'])
                    sheet.write(row, 8, currency_data.get('init_balance_currency', 0.0), formats['number'])
                    row += 1
                
                # Move lines
                for line in currency_data.get('lines', []):
                    date = line.get('date')
                    if isinstance(date, str):
                        try:
                            date = datetime.strptime(date, '%Y-%m-%d').date()
                        except ValueError:
                            date = None
                    
                    sheet.write(row, 0, date.strftime('%Y-%m-%d') if date else '', formats['date'])
                    sheet.write(row, 1, line.get('journal_name', ''), formats['cell'])
                    sheet.write(row, 2, line.get('partner_name', ''), formats['cell'])
                    sheet.write(row, 3, line.get('name', ''), formats['cell'])
                    sheet.write(row, 4, line.get('debit', 0.0), formats['number'])
                    sheet.write(row, 5, line.get('credit', 0.0), formats['number'])
                    sheet.write(row, 6, line.get('balance', 0.0), formats['number'])
                    sheet.write(row, 7, currency.name, formats['cell'])
                    sheet.write(row, 8, line.get('amount_currency', 0.0), formats['number'])
                    row += 1
                
                # Currency total
                sheet.write(row, 0, 'Total', formats['total'])
                sheet.merge_range(f'B{row+1}:C{row+1}', '', formats['total'])
                sheet.write(row, 3, '', formats['total'])
                sheet.write(row, 4, currency_data.get('total_debit', 0.0), formats['total'])
                sheet.write(row, 5, currency_data.get('total_credit', 0.0), formats['total'])
                sheet.write(row, 6, currency_data.get('total_balance', 0.0), formats['total'])
                sheet.write(row, 7, currency.name, formats['total'])
                sheet.write(row, 8, currency_data.get('total_amount_currency', 0.0), formats['total'])
                row += 1
