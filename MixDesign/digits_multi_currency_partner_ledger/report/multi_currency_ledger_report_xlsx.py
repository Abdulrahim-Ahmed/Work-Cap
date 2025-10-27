# -*- coding: utf-8 -*-
###############################################################################
#
#    Digital Integrated Transformation Solutions (DigitsCode)
#    Copyright (C) 2025-TODAY Digital Integrated Transformation Solutions (<https://www.digitscode.com>).
#    Author: Digital Integrated Transformation Solutions (<https://www.digitscode.com>)
#
###############################################################################

from odoo import models
import datetime
import logging
import traceback
import json
from datetime import datetime

_logger = logging.getLogger(__name__)


class MultiCurrencyLedgerXlsx(models.AbstractModel):
    _name = 'report.digits_multi_currency_partner_ledger.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Multi Currency Partner Ledger XLSX Report'

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
            
            # Get report data
            form = data.get('form', {}) if data else {}
            
            # Get main report data
            report_data = self._get_report_data(form)
            
            # Create worksheet
            sheet = workbook.add_worksheet('Partner Ledger')
            
            # Create formats
            formats = self._create_formats(workbook)
            
            # Set column widths
            self._set_column_widths(sheet)
            
            # Write report header
            self._write_report_header(sheet, form, report_data, formats)
            
            # Write partner data
            self._write_partner_data(sheet, report_data, form, formats)
            
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
            report = self.env['report.digits_multi_currency_partner_ledger.report_template']
            result = report._get_report_values([], data)
            _logger.info("Successfully retrieved report data")
            return result
        except Exception as e:
            _logger.error("Error getting report data: %s\n%s", str(e), traceback.format_exc())
            # Return minimal data in case of error
            return {
                'docs': self.env['res.partner'].browse(form.get('partner_ids', [])),
                'currencies': self.env['res.currency'].browse(form.get('currency_ids', [])),
                'results': {},
                'form': form,
                'company': self.env['res.company'].browse(form.get('company_id', self.env.company.id)),
            }
    
    def _create_formats(self, workbook):
        """Create formats for the report"""
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
            
            'partner_info': workbook.add_format({
                'italic': True,
                'text_wrap': True,
            }),
            
            'partner_info_label': workbook.add_format({
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
        """Set column widths"""
        sheet.set_column('A:A', 12)  # Date
        sheet.set_column('B:B', 20)  # Journal Entry
        sheet.set_column('C:C', 20)  # Vendor Bill Number
        sheet.set_column('D:D', 30)  # Description
        sheet.set_column('E:G', 15)  # Debit, Credit, Balance
    
    def _write_report_header(self, sheet, form, report_data, formats):
        """Write report header"""
        company = report_data.get('company')
        
        # Report title
        sheet.merge_range('A1:G1', 'Partner Ledger', formats['header'])
        
        # Report parameters
        sheet.write('A3', 'Company:', formats['subheader'])
        sheet.write('B3', company.name if company else '', formats['cell'])
        
        if form.get('date_from'):
            sheet.write('A4', 'From:', formats['subheader'])
            date_from_value = form['date_from']
            if isinstance(date_from_value, str):
                try:
                    date_from_value = datetime.strptime(date_from_value, '%Y-%m-%d').date()
                except ValueError:
                    # If there's an error converting, use the string as is
                    pass
            sheet.write('B4', date_from_value, formats['date'])
        
        if form.get('date_to'):
            sheet.write('A5', 'To:', formats['subheader'])
            date_to_value = form['date_to']
            if isinstance(date_to_value, str):
                try:
                    date_to_value = datetime.strptime(date_to_value, '%Y-%m-%d').date()
                except ValueError:
                    # If there's an error converting, use the string as is
                    pass
            sheet.write('B5', date_to_value, formats['date'])
        
        sheet.write('A6', 'Target Moves:', formats['subheader'])
        target_move_text = 'All Posted Entries' if form.get('target_move') == 'posted' else 'All Entries'
        sheet.write('B6', target_move_text, formats['cell'])
    
    def _write_partner_data(self, sheet, report_data, form, formats):
        """Write partner data"""
        partners = report_data.get('docs', [])
        currencies = report_data.get('currencies', [])
        results = report_data.get('results', {})
        
        # Initialize row counter
        row = 8
        
        # Check if there is data
        if not partners or not currencies or not results:
            sheet.merge_range(f'A{row}:G{row}', 'No data available for the selected criteria', formats['cell'])
            return
        
        # For each partner
        for partner in partners:
            partner_id = partner.id
            
            # Skip if no data for this partner
            if partner_id not in results:
                _logger.info("Skipping partner %s: no data in results", partner.name)
                continue
            
            # Check if partner has data in any currency
            has_data = False
            for currency in currencies:
                currency_id = currency.id
                if (currency_id in results[partner_id] and 
                    (results[partner_id][currency_id].get('lines') or 
                     results[partner_id][currency_id].get('init_balance', 0) != 0)):
                    has_data = True
                    break
            
            if not has_data:
                _logger.info("Skipping partner %s: no movement data", partner.name)
                continue
            
            # Write partner header
            sheet.merge_range(f'A{row}:G{row}', partner.name, formats['header'])
            row += 1
            
            # Write partner details
            # Address
            address_parts = []
            if hasattr(partner, 'street') and partner.street:
                address_parts.append(partner.street)
            if hasattr(partner, 'street2') and partner.street2:
                address_parts.append(partner.street2)
            
            city_state_zip = []
            if hasattr(partner, 'city') and partner.city:
                city_state_zip.append(partner.city)
            if hasattr(partner, 'state_id') and partner.state_id:
                city_state_zip.append(partner.state_id.name)
            if hasattr(partner, 'zip') and partner.zip:
                city_state_zip.append(partner.zip)
            
            if city_state_zip:
                address_parts.append(', '.join(city_state_zip))
            
            if hasattr(partner, 'country_id') and partner.country_id:
                address_parts.append(partner.country_id.name)
            
            if address_parts:
                sheet.write(row, 0, 'Address:', formats['partner_info_label'])
                sheet.merge_range(f'B{row}:G{row}', '\n'.join(address_parts), formats['partner_info'])
                row += 1
            
            # Tax ID
            if hasattr(partner, 'vat') and partner.vat:
                sheet.write(row, 0, 'Tax ID:', formats['partner_info_label'])
                sheet.merge_range(f'B{row}:G{row}', partner.vat, formats['partner_info'])
                row += 1
            
            # Company Registry - check if attribute exists
            if hasattr(partner, 'company_registry') and partner.company_registry:
                sheet.write(row, 0, 'Company Registry:', formats['partner_info_label'])
                sheet.merge_range(f'B{row}:G{row}', partner.company_registry, formats['partner_info'])
                row += 1
            
            # Add an empty row after partner details
            row += 1
            
            # For each currency that has data for this partner
            for currency in currencies:
                currency_id = currency.id
                # Skip if no data for this currency
                if currency_id not in results[partner_id]:
                    continue
                    
                partner_data = results[partner_id][currency_id]
                
                # Skip if no lines and no initial balance
                if (not partner_data.get('lines') and 
                    partner_data.get('init_balance', 0) == 0):
                    continue
                
                # Skip if nothing to show according to configuration
                if (form.get('display_account') == 'movement' and 
                    not partner_data.get('lines') and 
                    partner_data.get('init_balance', 0) == 0):
                    continue
                
                # Write currency header
                sheet.merge_range(f'A{row}:G{row}', currency.name + ' (' + currency.symbol + ')', formats['subheader'])
                row += 1
                
                # Write column headers
                headers = ['Date', 'Journal Entry', 'Vendor Bill Number', 'Description', 
                          f'Debit ({currency.symbol})', f'Credit ({currency.symbol})', 
                          f'Balance ({currency.symbol})']
                sheet.write_row(row, 0, headers, formats['header'])
                row += 1
                
                # Write initial balance if enabled
                running_balance = 0
                if form.get('show_init_balance') and form.get('date_from'):
                    init_balance = partner_data.get('init_balance', 0)
                    running_balance = init_balance
                    
                    date_from = form.get('date_from')
                    if isinstance(date_from, str):
                        try:
                            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                        except ValueError:
                            # If there's an error converting, use the string as is
                            pass
                    
                    sheet.write(row, 0, date_from, formats['date'])
                    sheet.write(row, 1, '', formats['cell'])
                    sheet.write(row, 2, '', formats['cell'])
                    sheet.write(row, 3, 'Initial Balance', formats['cell'])
                    sheet.write(row, 4, '', formats['cell'])
                    sheet.write(row, 5, '', formats['cell'])
                    sheet.write(row, 6, init_balance, formats['number'])
                    row += 1
                
                # Write movement lines
                lines = partner_data.get('lines', [])
                for line in lines:
                    balance = line.get('balance', 0)
                    running_balance += balance
                    
                    line_date = line.get('date')
                    if isinstance(line_date, str):
                        try:
                            line_date = datetime.strptime(line_date, '%Y-%m-%d').date()
                        except ValueError:
                            # If there's an error converting, use the string as is
                            pass
                    
                    sheet.write(row, 0, line_date, formats['date'])
                    sheet.write(row, 1, line.get('move_name', ''), formats['cell'])
                    sheet.write(row, 2, line.get('ref', ''), formats['cell'])
                    sheet.write(row, 3, line.get('name', ''), formats['cell'])
                    sheet.write(row, 4, line.get('debit', 0), formats['number'])
                    sheet.write(row, 5, line.get('credit', 0), formats['number'])
                    sheet.write(row, 6, running_balance, formats['number'])
                    row += 1
                
                # Write partner totals
                sheet.write(row, 3, 'Total', formats['total'])
                sheet.write(row, 4, partner_data.get('debit', 0), formats['total'])
                sheet.write(row, 5, partner_data.get('credit', 0), formats['total'])
                sheet.write(row, 6, partner_data.get('balance', 0) + partner_data.get('init_balance', 0), formats['total'])
                row += 2  # Add space between currencies
            
            row += 1  # Add extra space between partners
