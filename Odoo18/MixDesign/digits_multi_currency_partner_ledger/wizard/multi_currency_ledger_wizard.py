# -*- coding: utf-8 -*-
###############################################################################
#
#    Digital Integrated Transformation Solutions (DigitsCode)
#    Copyright (C) 2025-TODAY Digital Integrated Transformation Solutions (<https://www.digitscode.com>).
#    Author: Digital Integrated Transformation Solutions (<https://www.digitscode.com>)
#
###############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date
import json
import logging
import base64
import io
from collections import defaultdict
import xlsxwriter

_logger = logging.getLogger(__name__)


class MultiCurrencyLedgerWizard(models.TransientModel):
    _name = 'multi.currency.ledger.wizard'
    _description = 'Multi Currency Partner Ledger Wizard'

    def _default_date_from(self):
        """Set default start date to beginning of current year"""
        today = date.today()
        return date(today.year, 1, 1)

    def _default_date_to(self):
        """Set default end date to today"""
        return date.today()

    company_id = fields.Many2one(
        'res.company', string='Company', 
        default=lambda self: self.env.company,
        required=True
    )
    date_from = fields.Date(string='Start Date', default=_default_date_from)
    date_to = fields.Date(string='End Date', default=_default_date_to)
    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries'),
    ], string='Target Moves', required=True, default='posted')
    display_account = fields.Selection([
        ('all', 'All'),
        ('movement', 'With movements'),
    ], string='Display Accounts', required=True, default='movement')
    partner_ids = fields.Many2many(
        'res.partner', string='Partners',
        domain=[('parent_id', '=', False)],
        help="Leave empty to get all partners"
    )
    currency_ids = fields.Many2many(
        'res.currency', string='Currencies',
        help="Leave empty to get all currencies"
    )
    account_type_receivable = fields.Boolean(string='Receivable', default=True)
    account_type_non_trade_receivable = fields.Boolean(string='Non Trade Receivable', default=False)
    account_type_payable = fields.Boolean(string='Payable', default=True)
    account_type_non_trade_payable = fields.Boolean(string='Non Trade Payable', default=False)
    show_init_balance = fields.Boolean(
        string='Show Initial Balance', default=True
    )
    partner_tags = fields.Many2many(
        'res.partner.category', string='Partner Tags',
        help="Filter partners by tags"
    )
    
    @api.onchange('partner_tags')
    def _onchange_partner_tags(self):
        """Filter partners based on selected tags"""
        if self.partner_tags:
            domain = [('category_id', 'in', self.partner_tags.ids)]
            partners = self.env['res.partner'].search(domain)
            return {'domain': {'partner_ids': [('id', 'in', partners.ids)]}}
        return {'domain': {'partner_ids': []}}
    
    @api.onchange('account_type_receivable', 'account_type_non_trade_receivable', 
                  'account_type_payable', 'account_type_non_trade_payable')
    def _onchange_account_types(self):
        """Ensure at least one account type is selected"""
        if not any([self.account_type_receivable, self.account_type_non_trade_receivable, 
                   self.account_type_payable, self.account_type_non_trade_payable]):
            # If no type is selected, default to all types
            self.account_type_receivable = True
            self.account_type_payable = True
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Check if start date is before end date"""
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise UserError(_("Start date must be less than or equal to end date."))
    
    def action_print_pdf(self):
        """Print the report as PDF"""
        self.ensure_one()
        data = self._prepare_report_data()
        return self.env.ref(
            'digits_multi_currency_partner_ledger.action_report_multi_currency_ledger_pdf'
        ).report_action(self, data=data)
    
    def action_print_excel(self):
        """Export the report as Excel using xlsxwriter directly"""
        import base64
        import io
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("The xlsxwriter library is not installed. Please install it using 'pip install xlsxwriter'."))
        
        self.ensure_one()
        _logger.info("Starting direct XLSX Export for Multi Currency Partner Ledger")
        
        # Create in-memory Excel file
        output = io.BytesIO()
        workbook = None
        
        try:
            # Create workbook with simpler approach
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sheet = workbook.add_worksheet('Partner Ledger')
            
            # Create formats
            formats = {
                'title': workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'}),
                'header': workbook.add_format({'bold': True, 'bg_color': '#EEEEEE', 'border': 1}),
                'text': workbook.add_format({'border': 1}),
                'number': workbook.add_format({'num_format': '#,##0.00', 'border': 1}),
                'date': workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1}),
                'partner_header': workbook.add_format({'bold': True, 'bg_color': '#DDDDDD', 'border': 1}),
                'currency_header': workbook.add_format({'bold': True, 'bg_color': '#E6F2FF', 'border': 1}),
                'total': workbook.add_format({'bold': True, 'num_format': '#,##0.00', 'border': 1, 'bg_color': '#EEEEEE'})
            }
            
            # Set column widths
            sheet.set_column(0, 0, 12)  # Date
            sheet.set_column(1, 1, 15)  # Journal
            sheet.set_column(2, 2, 15)  # Account
            sheet.set_column(3, 3, 40)  # Description
            sheet.set_column(4, 4, 15)  # Debit
            sheet.set_column(5, 5, 15)  # Credit
            sheet.set_column(6, 6, 15)  # Balance
            
            # Report title
            company_name = self.company_id.name
            report_title = "Multi Currency Partner Ledger"
            date_str = ""
            if self.date_from:
                date_str += "From: " + self.date_from.strftime('%Y-%m-%d') + " "
            if self.date_to:
                date_str += "To: " + self.date_to.strftime('%Y-%m-%d')
                
            row = 0
            sheet.write(row, 0, company_name, formats['title']); row += 1
            sheet.write(row, 0, report_title, formats['title']); row += 1
            sheet.write(row, 0, date_str, formats['title']); row += 2
            
            # Filter information
            sheet.write(row, 0, "Filters:", formats['header'])
            sheet.write(row, 1, "Target Moves:", formats['text'])
            sheet.write(row, 2, "All Posted Entries" if self.target_move == 'posted' else "All Entries", formats['text'])
            row += 1
            
            # Headers
            row += 1
            headers = ['Date', 'Journal', 'Account', 'Description', 'Debit', 'Credit', 'Balance']
            for col, header in enumerate(headers):
                sheet.write(row, col, header, formats['header'])
            row += 1
            
            # Prepare parameters for getting data
            params = {
                'company_id': self.company_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'target_move': self.target_move,
                'display_account': self.display_account,
                'partner_ids': self.partner_ids.ids if self.partner_ids else [],
                'currency_ids': self.currency_ids.ids if self.currency_ids else [],
                'account_type_receivable': self.account_type_receivable,
                'account_type_non_trade_receivable': self.account_type_non_trade_receivable,
                'account_type_payable': self.account_type_payable,
                'account_type_non_trade_payable': self.account_type_non_trade_payable,
                'show_init_balance': self.show_init_balance,
                'partner_tags': self.partner_tags.ids if self.partner_tags else [],
            }
            
            # Get partners
            partners = self._get_partners(params)
            
            # Get currencies
            currencies = self._get_currencies(params)
            
            # Get account types
            account_types = []
            if self.account_type_receivable:
                account_types.append('asset_receivable')
            if self.account_type_non_trade_receivable:
                account_types.append('asset_receivable_non_trade')
            if self.account_type_payable:
                account_types.append('liability_payable')
            if self.account_type_non_trade_payable:
                account_types.append('liability_payable_non_trade')
                
            # Process each partner
            for partner in partners:
                _logger.info("Processing partner: %s", partner.name)
                
                # Check if partner has data
                has_data = False
                
                # Write partner header
                sheet.merge_range(row, 0, row, 6, "Partner: " + partner.name, formats['partner_header'])
                row += 1
                
                # Process each currency for this partner
                for currency in currencies:
                    # Get data for this currency
                    lines = self._get_partner_move_lines(
                        partner.id, 
                        currency.id, 
                        params.get('date_from'), 
                        params.get('date_to'), 
                        params.get('target_move'),
                        account_types,
                        params.get('company_id')
                    )
                    
                    initial_balance = 0.0
                    if params.get('show_init_balance') and params.get('date_from'):
                        initial_balance = self._get_initial_balance(
                            partner.id,
                            currency.id,
                            params.get('date_from'),
                            params.get('target_move'),
                            account_types,
                            params.get('company_id')
                        )
                    
                    # Skip currency if no data
                    if not lines and initial_balance == 0 and params.get('display_account') != 'all':
                        continue
                        
                    has_data = True
                    
                    # Write currency header
                    sheet.merge_range(row, 0, row, 6, "Currency: " + currency.name + " (" + currency.symbol + ")", formats['currency_header'])
                    row += 1
                    
                    # Write initial balance if applicable
                    if params.get('show_init_balance'):
                        sheet.write(row, 0, "Initial Balance", formats['text'])
                        sheet.merge_range(row, 1, row, 5, "", formats['text'])
                        sheet.write(row, 6, float(initial_balance), formats['number'])
                        row += 1
                    
                    # Track running balance
                    balance = initial_balance
                    total_debit = 0.0
                    total_credit = 0.0
                    
                    # Write lines
                    for line in lines:
                        # Calculate balance
                        balance += line['balance']
                        total_debit += line['debit']
                        total_credit += line['credit']
                        
                        # Write line data
                        date_val = line['date']
                        if isinstance(date_val, (datetime, date)):
                            date_val = date_val.strftime('%Y-%m-%d')
                            
                        sheet.write(row, 0, date_val, formats['date'])
                        sheet.write(row, 1, str(line['journal_name']), formats['text'])
                        sheet.write(row, 2, str(line['account_name']), formats['text'])
                        sheet.write(row, 3, str(line['ref'] or line['name'] or ''), formats['text'])
                        sheet.write(row, 4, float(line['debit']), formats['number'])
                        sheet.write(row, 5, float(line['credit']), formats['number'])
                        sheet.write(row, 6, float(balance), formats['number'])
                        row += 1
                    
                    # Write currency totals
                    sheet.write(row, 0, "Total " + currency.name, formats['total'])
                    sheet.merge_range(row, 1, row, 3, "", formats['total'])
                    sheet.write(row, 4, float(total_debit), formats['total'])
                    sheet.write(row, 5, float(total_credit), formats['total'])
                    sheet.write(row, 6, float(balance), formats['total'])
                    row += 2
                
                # Skip row if partner had no data
                if not has_data and params.get('display_account') != 'all':
                    row -= 1  # Remove partner header row
                else:
                    row += 1  # Extra space between partners
            
            # Close workbook
            workbook.close()
            
            # Create attachment for download
            excel_data = output.getvalue()
            filename = 'Partner_Ledger_%s.xlsx' % datetime.now().strftime('%Y%m%d_%H%M%S')
            
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.b64encode(excel_data),
                'res_model': self._name,
                'res_id': self.id,
                'type': 'binary',
            })
            
            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'self',
            }
            
        except Exception as e:
            _logger.error("Error generating Excel report: %s", e)
            import traceback
            _logger.error(traceback.format_exc())
            raise UserError(_("Error generating Excel report: %s") % e)
            
        finally:
            if workbook:
                try:
                    workbook.close()
                except:
                    pass
            output.close()
    
    def _create_xlsx_formats(self, workbook):
        """Create cell formats for the Excel report"""
        formats = {
            'title': workbook.add_format({
                'bold': True,
                'font_size': 14,
                'align': 'center',
                'valign': 'vcenter',
            }),
            'header': workbook.add_format({
                'bold': True,
                'bg_color': '#EEEEEE',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
            }),
            'date': workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'border': 1,
            }),
            'number': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
            }),
            'text': workbook.add_format({
                'border': 1,
            }),
            'total': workbook.add_format({
                'bold': True,
                'num_format': '#,##0.00',
                'border': 1,
                'bg_color': '#EEEEEE',
            }),
            'partner_header': workbook.add_format({
                'bold': True,
                'bg_color': '#DDDDDD',
                'border': 1,
            }),
            'currency_header': workbook.add_format({
                'bold': True,
                'bg_color': '#E6F2FF',
                'border': 1,
            }),
            'debit': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
                'bg_color': '#FFCCCC',
            }),
            'credit': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
                'bg_color': '#CCFFCC',
            }),
            'balance': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
                'bg_color': '#E6F2FF',
            }),
            'currency_total': workbook.add_format({
                'bold': True,
                'num_format': '#,##0.00',
                'border': 1,
                'bg_color': '#E6F2FF',
            }),
        }
        return formats
    
    def _get_report_data_for_xlsx(self, form):
        """Get report data for Excel report"""
        _logger.info("Starting _get_report_data_for_xlsx")
        # Get company object
        company_id = form.get('company_id', False)
        company = self.env['res.company'].browse(company_id)
        
        # Get partners based on filter
        partners = self._get_partners(form)
        _logger.info("Found %s partners", len(partners))
        
        # Get currencies based on filter
        currencies = self._get_currencies(form)
        _logger.info("Found %s currencies", len(currencies))
        
        # Get account types to include
        account_type_list = []
        if form.get('account_type_receivable'):
            account_type_list.append('asset_receivable')
        if form.get('account_type_non_trade_receivable'):
            account_type_list.append('asset_receivable_non_trade')
        if form.get('account_type_payable'):
            account_type_list.append('liability_payable')
        if form.get('account_type_non_trade_payable'):
            account_type_list.append('liability_payable_non_trade')
        
        _logger.info("Using account types: %s", account_type_list)
        
        # Build the query parameters
        params = {
            'company_id': company_id,
            'date_from': form.get('date_from'),
            'date_to': form.get('date_to'),
            'target_move': form.get('target_move'),
            'partner_ids': form.get('partner_ids', []),
            'account_types': account_type_list,
            'display_account': form.get('display_account', 'movement'),
            'show_init_balance': form.get('show_init_balance', True),
        }
        
        # Get partner ledger data
        result = {}
        for partner in partners:
            _logger.info("Processing partner: %s (ID: %s)", partner.name, partner.id)
            partner_data = {
                'id': partner.id,
                'name': partner.name,
                'currencies': {},
            }
            
            # Process each currency
            for currency in currencies:
                _logger.info("Processing currency: %s (ID: %s) for partner %s", currency.name, currency.id, partner.name)
                currency_data = self._get_partner_currency_data(partner, currency, params)
                
                # Only include currency data if there are movements or balances
                if currency_data['lines'] or currency_data['initial_balance'] != 0:
                    partner_data['currencies'][currency.id] = {
                        'id': currency.id,
                        'name': currency.name,
                        'symbol': currency.symbol,
                        'initial_balance': currency_data['initial_balance'],
                        'final_balance': currency_data['final_balance'],
                        'total_debit': currency_data['total_debit'],
                        'total_credit': currency_data['total_credit'],
                        'lines': currency_data['lines'],
                    }
            
            # Only include partners with data
            if partner_data['currencies'] and (params['display_account'] == 'all' or 
                                              any(c['lines'] for c in partner_data['currencies'].values())):
                result[partner.id] = partner_data
        
        _logger.info("Final result contains %s partners with data", len(result))
        return result
    
    def _get_partners(self, form):
        """Get partners based on filter criteria"""
        partner_ids = form.get('partner_ids', [])
        if partner_ids:
            return self.env['res.partner'].browse(partner_ids)
        
        # Build domain for partners
        domain = [('parent_id', '=', False)]
        
        # Add partner tags filter if specified
        if form.get('partner_tags', []):
            domain.append(('category_id', 'in', form['partner_tags']))
        
        # Get account types to filter partners
        account_type_list = []
        if form.get('account_type_receivable'):
            account_type_list.append('asset_receivable')
        if form.get('account_type_non_trade_receivable'):
            account_type_list.append('asset_receivable_non_trade')
        if form.get('account_type_payable'):
            account_type_list.append('liability_payable')
        if form.get('account_type_non_trade_payable'):
            account_type_list.append('liability_payable_non_trade')
        
        # Get partners with matching accounts
        partners = self.env['res.partner']
        if account_type_list:
            # Get accounts of specified types
            accounts = self.env['account.account'].search([
                ('account_type', 'in', account_type_list),
                ('company_id', '=', form['company_id']),
            ])
            
            # Find partners with move lines in these accounts
            if accounts:
                query = """
                    SELECT DISTINCT partner_id FROM account_move_line
                    WHERE account_id IN %s AND partner_id IS NOT NULL
                """
                params = [tuple(accounts.ids)]
                
                # Add target move filter
                if form.get('target_move') == 'posted':
                    query += " AND parent_state = 'posted'"
                
                # Add date filters
                if form.get('date_from'):
                    query += " AND date >= %s"
                    params.append(form['date_from'])
                if form.get('date_to'):
                    query += " AND date <= %s"
                    params.append(form['date_to'])
                
                self.env.cr.execute(query, params)
                partner_ids = [row[0] for row in self.env.cr.fetchall()]
                if partner_ids:
                    domain.append(('id', 'in', partner_ids))
                    partners = self.env['res.partner'].search(domain)
        
        return partners
    
    def _get_currencies(self, form):
        """Get currencies based on filter criteria"""
        currency_ids = form.get('currency_ids', [])
        if currency_ids:
            return self.env['res.currency'].browse(currency_ids)
        return self.env['res.currency'].search([])
    
    def _get_partner_currency_data(self, partner, currency, params):
        """Get ledger data for a partner in specific currency"""
        # Initialize result
        result = {
            'initial_balance': 0.0,
            'final_balance': 0.0,
            'total_debit': 0.0,
            'total_credit': 0.0,
            'lines': [],
        }
        
        # Get move lines for this partner and currency
        lines = self._get_partner_move_lines(
            partner.id, 
            currency.id, 
            params['date_from'], 
            params['date_to'], 
            params['target_move'],
            params['account_types'],
            params['company_id']
        )
        
        # Get initial balance if requested
        if params['show_init_balance'] and params['date_from']:
            result['initial_balance'] = self._get_initial_balance(
                partner.id,
                currency.id,
                params['date_from'],
                params['target_move'],
                params['account_types'],
                params['company_id']
            )
        
        # Process move lines
        balance = result['initial_balance']
        for line in lines:
            balance += line['balance']
            # Convert date string to formatted date string if needed
            date_value = line['date']
            if isinstance(date_value, datetime) or isinstance(date_value, date):
                date_value = date_value.strftime('%Y-%m-%d')
                
            result['lines'].append({
                'date': date_value,
                'journal': line['journal_name'],
                'account': line['account_name'],
                'ref_desc': line['ref'] or line['name'] or '',
                'debit': line['debit'],
                'credit': line['credit'],
                'balance': balance,
            })
            
            # Update totals
            result['total_debit'] += line['debit']
            result['total_credit'] += line['credit']
        
        # Calculate final balance
        result['final_balance'] = balance
        
        return result
    
    def _get_partner_move_lines(self, partner_id, currency_id, date_from, date_to, target_move, account_types, company_id):
        """Get move lines for a partner in specific currency"""
        self.env.cr.execute("""
            SELECT 
                l.id,
                l.date,
                j.code AS journal_code,
                j.name AS journal_name,
                a.name AS account_name,
                l.name,
                l.ref,
                CASE 
                    WHEN l.currency_id = %s THEN l.amount_currency 
                    ELSE (CASE WHEN l.debit > 0 THEN l.debit ELSE 0 END)
                END AS debit,
                CASE 
                    WHEN l.currency_id = %s THEN -l.amount_currency 
                    ELSE (CASE WHEN l.credit > 0 THEN l.credit ELSE 0 END)
                END AS credit,
                CASE 
                    WHEN l.currency_id = %s THEN l.amount_currency 
                    ELSE l.balance
                END AS balance,
                c.name AS currency_name,
                c.symbol AS currency_symbol
            FROM account_move_line l
            JOIN account_move m ON l.move_id = m.id
            JOIN account_journal j ON l.journal_id = j.id
            JOIN account_account a ON l.account_id = a.id
            JOIN res_currency c ON c.id = %s
            WHERE l.partner_id = %s
            AND (l.currency_id = %s OR (l.currency_id IS NULL AND l.company_currency_id = %s))
            AND a.account_type IN %s
            AND l.company_id = %s
        """ + (" AND m.state = 'posted'" if target_move == 'posted' else "") + """
            AND l.date <= %s
        """ + (" AND l.date >= %s" if date_from else ""),
            (
                currency_id, currency_id, currency_id, currency_id, 
                partner_id, 
                currency_id, currency_id,
                tuple(account_types),
                company_id,
                date_to,
                *([date_from] if date_from else [])
            )
        )
        return self.env.cr.dictfetchall()
    
    def _get_initial_balance(self, partner_id, currency_id, date_from, target_move, account_types, company_id):
        """Calculate initial balance for a partner in specific currency"""
        self.env.cr.execute("""
            SELECT SUM(
                CASE 
                    WHEN l.currency_id = %s THEN l.amount_currency 
                    ELSE l.balance
                END
            ) AS initial_balance
            FROM account_move_line l
            JOIN account_move m ON l.move_id = m.id
            JOIN account_account a ON l.account_id = a.id
            WHERE l.partner_id = %s
            AND (l.currency_id = %s OR (l.currency_id IS NULL AND l.company_currency_id = %s))
            AND a.account_type IN %s
            AND l.company_id = %s
        """ + (" AND m.state = 'posted'" if target_move == 'posted' else "") + """
            AND l.date < %s
        """, (
            currency_id,
            partner_id, 
            currency_id, currency_id,
            tuple(account_types),
            company_id,
            date_from,
        ))
        result = self.env.cr.dictfetchone()
        return result['initial_balance'] if result and result['initial_balance'] else 0.0
    
    def _prepare_report_data(self):
        """Prepare data for the report"""
        self.ensure_one()
        return {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'company_id': self.company_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'target_move': self.target_move,
                'display_account': self.display_account,
                'partner_ids': self.partner_ids.ids if self.partner_ids else [],
                'currency_ids': self.currency_ids.ids if self.currency_ids else [],
                'account_type_receivable': self.account_type_receivable,
                'account_type_non_trade_receivable': self.account_type_non_trade_receivable,
                'account_type_payable': self.account_type_payable,
                'account_type_non_trade_payable': self.account_type_non_trade_payable,
                'show_init_balance': self.show_init_balance,
                'partner_tags': self.partner_tags.ids if self.partner_tags else [],
            }
        }
