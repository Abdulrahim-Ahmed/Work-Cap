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
    _name = 'report.mcgl_xlsx'
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
            report = self.env['report.mcgl_pdf']
            result = report._get_report_values([], data)
            _logger.info("Successfully retrieved report data")
            return result
        except Exception as e:
            _logger.error("Error getting report data: %s\n%s", str(e), traceback.format_exc())
            # Return minimal data in case of error
            return {
                'docs': self.env['account.account'].browse(form.get('account_ids', [])),
                'currencies': self.env['res.currency'].browse(form.get('currency_ids', [])),
                'journals': self.env['account.journal'].browse(form.get('journal_ids', [])),
                'results': {},
                'form': form,
                'company': self.env['res.company'].browse(form.get('company_id', self.env.company.id)),
            }
    
    def _create_formats(self, workbook):
        """Create formats for the report"""
        # Initialize all format variables as instance attributes
        self.date_format = None
        self.header_format = None
        self.subheader_format = None
        self.account_info_format = None
        self.account_info_label_format = None
        self.number_format = None
        self.total_format = None
        self.cell_format = None
        
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
        
        # Assign formats to instance attributes for better accessibility
        self.date_format = formats['date']
        self.header_format = formats['header']
        self.subheader_format = formats['subheader']
        self.account_info_format = formats['account_info']
        self.account_info_label_format = formats['account_info_label']
        self.number_format = formats['number']
        self.total_format = formats['total']
        self.cell_format = formats['cell']
        
        return formats
    
    def _set_column_widths(self, sheet):
        """Set column widths"""
        sheet.set_column('A:A', 12)  # Date
        sheet.set_column('B:B', 20)  # Journal Entry
        sheet.set_column('C:C', 15)  # Journal
        sheet.set_column('D:D', 30)  # Description
        sheet.set_column('E:E', 20)  # Partner
        sheet.set_column('F:H', 15)  # Debit, Credit, Balance
    
    def _write_report_header(self, sheet, form, report_data, formats):
        """Write report header"""
        company = report_data.get('company')
        
        # Report title
        sheet.merge_range('A1:H1', 'General Ledger', formats['header'])
        
        # Report parameters
        sheet.write('A3', 'Company:', formats['subheader'])
        sheet.write('B3', company.name if company else '', formats['cell'])
        
        if form.get('date_from'):
            sheet.write('A4', 'From:', formats['subheader'])
            date_from_value = form['date_from']
            if isinstance(date_from_value, str):
                try:
                    date_from_value = datetime.strptime(date_from_value, '%Y-%m-%d').date()
                except ValueError as e:
                    _logger.error("Error converting date_from: %s", e)
                    # If there's an error converting, use the string as is
            sheet.write('B4', date_from_value, formats['date'])
        
        if form.get('date_to'):
            sheet.write('A5', 'To:', formats['subheader'])
            date_to_value = form['date_to']
            if isinstance(date_to_value, str):
                try:
                    date_to_value = datetime.strptime(date_to_value, '%Y-%m-%d').date()
                except ValueError as e:
                    _logger.error("Error converting date_to: %s", e)
                    # If there's an error converting, use the string as is
            sheet.write('B5', date_to_value, formats['date'])
        
        sheet.write('A6', 'Target Moves:', formats['subheader'])
        target_move_text = 'All Posted Entries' if form.get('target_move') == 'posted' else 'All Entries'
        sheet.write('B6', target_move_text, formats['cell'])
        
        sheet.write('A7', 'Display Accounts:', formats['subheader'])
        display_account = form.get('display_account', 'all')
        display_account_text = {
            'all': 'All',
            'movement': 'With movements',
            'not_zero': 'With balance not equal to zero'
        }.get(display_account, 'All')
        sheet.write('B7', display_account_text, formats['cell'])
    
    def _write_account_data(self, sheet, report_data, form, formats):
        """Write account data"""
        accounts = report_data.get('docs', [])
        currencies = report_data.get('currencies', [])
        results = report_data.get('results', {})
        
        # Initialize row counter
        row = 8
        
        # Check if there is data
        if not accounts or not currencies or not results:
            sheet.merge_range(f'A{row}:H{row}', 'No data available for the selected criteria', formats['cell'])
            return
        
        # For each account
        for account in accounts:
            account_id = account.id
            
            # Skip if no data for this account
            if account_id not in results:
                _logger.info("Skipping account %s: no data in results", account.name)
                continue
            
            # Check if account has data in any currency
            has_data = False
            for currency in currencies:
                currency_id = currency.id
                if (currency_id in results[account_id] and 
                    (results[account_id][currency_id].get('lines') or 
                     results[account_id][currency_id].get('init_balance', 0) != 0)):
                    has_data = True
                    break
            
            # Skip accounts based on display_account setting
            if form.get('display_account') == 'movement' and not has_data:
                _logger.info("Skipping account %s: no movement data", account.name)
                continue
            
            if form.get('display_account') == 'not_zero':
                has_balance = False
                for currency in currencies:
                    currency_id = currency.id
                    if (currency_id in results[account_id] and 
                        (results[account_id][currency_id].get('balance', 0) != 0 or 
                         results[account_id][currency_id].get('init_balance', 0) != 0)):
                        has_balance = True
                        break
                if not has_balance:
                    _logger.info("Skipping account %s: zero balance", account.name)
                    continue
            
            # Write account header
            sheet.merge_range(f'A{row}:H{row}', f"{account.code} - {account.name}", formats['header'])
            row += 1
            
            # Write account details
            sheet.write(row, 0, 'Account Type:', formats['account_info_label'])
            sheet.write(row, 1, account.account_type, formats['account_info'])
            row += 1
            
            # Add an empty row after account details
            row += 1
            
            # For each currency that has data for this account
            for currency in currencies:
                currency_id = currency.id
                # Skip if no data for this currency
                if currency_id not in results[account_id]:
                    continue
                    
                account_data = results[account_id][currency_id]
                
                # Skip if no lines and no initial balance
                if (not account_data.get('lines') and 
                    account_data.get('init_balance', 0) == 0):
                    continue
                
                # Skip if nothing to show according to configuration
                if (form.get('display_account') == 'movement' and 
                    not account_data.get('lines')):
                    continue
                
                if (form.get('display_account') == 'not_zero' and 
                    account_data.get('balance', 0) == 0 and 
                    account_data.get('init_balance', 0) == 0):
                    continue
                
                # Write currency header
                sheet.merge_range(f'A{row}:H{row}', currency.name + ' (' + currency.symbol + ')', formats['subheader'])
                row += 1
                
                # Write column headers
                headers = ['Date', 'Journal Entry', 'Journal', 'Description', 'Partner',
                          f'Debit ({currency.symbol})', f'Credit ({currency.symbol})', 
                          f'Balance ({currency.symbol})']
                sheet.write_row(row, 0, headers, formats['header'])
                row += 1
                
                # Write initial balance if enabled
                running_balance = 0
                if form.get('show_init_balance') and form.get('date_from'):
                    init_balance = account_data.get('init_balance', 0)
                    running_balance = init_balance
                    
                    date_from = form.get('date_from')
                    if isinstance(date_from, str):
                        try:
                            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                        except ValueError as e:
                            _logger.error("Error converting date_from in account data: %s", e)
                            # If there's an error converting, use the string as is
                    
                    sheet.write(row, 0, date_from, formats['date'])
                    sheet.write(row, 1, '', formats['cell'])
                    sheet.write(row, 2, '', formats['cell'])
                    sheet.write(row, 3, 'Initial Balance', formats['cell'])
                    sheet.write(row, 4, '', formats['cell'])
                    sheet.write(row, 5, '', formats['cell'])
                    sheet.write(row, 6, '', formats['cell'])
                    sheet.write(row, 7, init_balance, formats['number'])
                    row += 1
                
                # Write movement lines
                lines = account_data.get('lines', [])
                for line in lines:
                    balance = line.get('balance', 0)
                    running_balance += balance
                    
                    line_date = line.get('date')
                    if isinstance(line_date, str):
                        try:
                            line_date = datetime.strptime(line_date, '%Y-%m-%d').date()
                        except ValueError as e:
                            _logger.error("Error converting line date: %s", e)
                            # If there's an error converting, use the string as is
                    
                    sheet.write(row, 0, line_date, formats['date'])
                    sheet.write(row, 1, line.get('move_name', ''), formats['cell'])
                    sheet.write(row, 2, line.get('journal_name', ''), formats['cell'])
                    sheet.write(row, 3, line.get('name', ''), formats['cell'])
                    sheet.write(row, 4, line.get('partner_name', ''), formats['cell'])
                    sheet.write(row, 5, line.get('debit', 0), formats['number'])
                    sheet.write(row, 6, line.get('credit', 0), formats['number'])
                    sheet.write(row, 7, running_balance, formats['number'])
                    row += 1
                
                # Write account totals
                sheet.write(row, 3, 'Total', formats['total'])
                sheet.write(row, 5, account_data.get('debit', 0), formats['total'])
                sheet.write(row, 6, account_data.get('credit', 0), formats['total'])
                sheet.write(row, 7, account_data.get('balance', 0) + account_data.get('init_balance', 0), formats['total'])
                row += 2  # Add space between currencies
            
            row += 1  # Add extra space between accounts
