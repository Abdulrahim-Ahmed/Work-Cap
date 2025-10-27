# -*- coding: utf-8 -*-
###############################################################################
#
#    Digital Integrated Transformation Solutions (DigitsCode)
#    Copyright (C) 2025-TODAY Digital Integrated Transformation Solutions (<https://www.digitscode.com>).
#    Author: Digital Integrated Transformation Solutions (<https://www.digitscode.com>)
#
###############################################################################

from odoo import models, api, _
from datetime import datetime
import json
import logging

_logger = logging.getLogger(__name__)


class MultiCurrencyLedger(models.AbstractModel):
    _name = 'report.digits_multi_currency_partner_ledger.report_template'
    _description = 'Multi Currency Partner Ledger Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare the data for rendering the report template"""
        _logger.info("Report data received: %s", data)
        
        if not data:
            _logger.warning("No data received for report")
            return {}
        
        form = data.get('form', {})
        _logger.info("Form data: %s", form)
        
        # Get selected partners or all partners if none selected
        if form.get('partner_ids'):
            partner_ids = form['partner_ids']
            partners = self.env['res.partner'].browse(partner_ids)
        else:
            # Get all partners with receivable/payable accounts
            account_types = ['asset_receivable', 'liability_payable']
            partners = self.env['res.partner'].search([])
            
        _logger.info("Selected partners: %s", partners)
        
        # Filter partners based on tags if specified
        if form.get('partner_tags'):
            tag_ids = form['partner_tags']
            filtered_partners = self.env['res.partner'].search([
                ('id', 'in', partners.ids),
                ('category_id', 'in', tag_ids)
            ])
            partners = filtered_partners if filtered_partners else partners
        
        # Get selected currencies or all currencies if none selected
        if form.get('currency_ids'):
            currency_ids = form['currency_ids']
            currencies = self.env['res.currency'].browse(currency_ids)
        else:
            currencies = self.env['res.currency'].search([])
            
        _logger.info("Selected currencies: %s", currencies)
            
        # Get accounts based on account types selected
        # Build domain based on account types selected
        domain = []
        
        account_type_receivable = form.get('account_type_receivable', True)
        account_type_non_trade_receivable = form.get('account_type_non_trade_receivable', False)
        account_type_payable = form.get('account_type_payable', True)
        account_type_non_trade_payable = form.get('account_type_non_trade_payable', False)
        
        # If no type is selected, default to all types
        if not any([account_type_receivable, account_type_non_trade_receivable, 
                   account_type_payable, account_type_non_trade_payable]):
            account_type_receivable = True
            account_type_payable = True
        
        # Count selected types to determine number of OR operators needed
        selected_types = []
        if account_type_receivable:
            selected_types.append(('account_type', '=', 'asset_receivable'))
        if account_type_non_trade_receivable:
            selected_types.append(('account_type', '=', 'asset_receivable_non_trade'))
        if account_type_payable:
            selected_types.append(('account_type', '=', 'liability_payable'))
        if account_type_non_trade_payable:
            selected_types.append(('account_type', '=', 'liability_payable_non_trade'))
        
        # Construct domain with proper OR operators
        if len(selected_types) > 1:
            # Add n-1 OR operators for n conditions
            domain.extend(['|'] * (len(selected_types) - 1))
            # Add all conditions
            domain.extend(selected_types)
        elif len(selected_types) == 1:
            domain.extend(selected_types)
        else:
            # Fallback if somehow no types are selected
            domain.append(('account_type', 'in', ['asset_receivable', 'liability_payable']))
            
        _logger.info("Account search domain: %s", domain)
        accounts = self.env['account.account'].search(domain)
            
        _logger.info("Selected accounts based on types: %s", accounts)
        
        # Prepare report data
        results = {}
        company_id = form.get('company_id', self.env.company.id)
        company = self.env['res.company'].browse(company_id)
        
        # Get parameters
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', datetime.now().date())
        target_move = form.get('target_move', 'posted')
        display_account = form.get('display_account', 'movement')
        show_init_balance = form.get('show_init_balance', True)
        
        _logger.info("Report parameters: from=%s, to=%s, target_move=%s, display_account=%s", 
                    date_from, date_to, target_move, display_account)
        
        for partner in partners:
            results[partner.id] = {}
            for currency in currencies:
                results[partner.id][currency.id] = {
                    'debit': 0.0,
                    'credit': 0.0,
                    'balance': 0.0,
                    'init_balance': 0.0,
                    'lines': []
                }
                
                # Compute initial balance if needed
                if date_from and show_init_balance:
                    init_balance = self._get_initial_balance(
                        partner, currency, accounts, date_from, target_move, company_id
                    )
                    results[partner.id][currency.id]['init_balance'] = init_balance
                
                # Get move lines
                move_lines = self._get_move_lines(
                    partner, currency, accounts, date_from, date_to, 
                    target_move, company_id
                )
                
                _logger.info("Partner %s, Currency %s: found %s move lines", 
                           partner.name, currency.name, len(move_lines))
                
                # Process move lines
                for line in move_lines:
                    results[partner.id][currency.id]['lines'].append(line)
                    results[partner.id][currency.id]['debit'] += line['debit']
                    results[partner.id][currency.id]['credit'] += line['credit']
                    results[partner.id][currency.id]['balance'] += line['balance']
        
        return {
            'doc_ids': partners.ids,
            'doc_model': 'res.partner',
            'docs': partners,
            'company': company,
            'currencies': currencies,
            'accounts': accounts,
            'form': form,
            'results': results,
        }
        
    def _get_initial_balance(self, partner, currency, accounts, date_from, target_move, company_id):
        """Calculate initial balance for a partner in a specific currency"""
        query = """
            SELECT COALESCE(SUM(aml.amount_currency), 0) as initial_balance
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            WHERE aml.partner_id = %s
            AND aml.account_id IN %s
            AND aml.currency_id = %s
            AND am.company_id = %s
            AND aml.date < %s
            AND aml.parent_state = %s
        """
        params = (
            partner.id, 
            tuple(accounts.ids) if accounts and accounts.ids else (0,),
            currency.id,
            company_id,
            date_from,
            'posted' if target_move == 'posted' else '%'
        )
        
        _logger.debug("Initial balance query: %s, params: %s", query, params)
        try:
            self.env.cr.execute(query, params)
            result = self.env.cr.fetchone()
            return result[0] if result else 0.0
        except Exception as e:
            _logger.error("Error calculating initial balance: %s", e)
            return 0.0
    
    def _get_move_lines(self, partner, currency, accounts, date_from, date_to, target_move, company_id):
        """Get move lines for a partner in a specific currency within date range"""
        domain = [
            ('partner_id', '=', partner.id),
            ('account_id', 'in', accounts.ids),
            ('currency_id', '=', currency.id),
            ('move_id.company_id', '=', company_id),
        ]
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))
        
        _logger.debug("Move lines search domain: %s", domain)
        try:
            move_lines = self.env['account.move.line'].search(
                domain, order='date, move_id, id'
            )
            _logger.debug("Found %s move lines for partner %s and currency %s", 
                        len(move_lines), partner.name, currency.name)
            result = []
            for line in move_lines:
                # Check if this is a purchase invoice and has a vendor reference
                description = line.name or ''
                
                # For purchase invoices, include vendor reference in description
                if line.move_id.move_type in ['in_invoice', 'in_refund']:
                    # Get the vendor reference (invoice number)
                    vendor_ref = line.move_id.ref or ''
                    # Get the invoice number
                    invoice_number = line.move_id.name or ''
                    
                    # Only add vendor reference if it exists and is different from invoice number
                    if vendor_ref and vendor_ref != invoice_number:
                        if description:
                            description = f"{description} - {_('Vendor Ref')}: {vendor_ref}"
                        else:
                            description = f"{_('Vendor Ref')}: {vendor_ref}"
                
                # For sales invoices, include customer reference in description
                elif line.move_id.move_type in ['out_invoice', 'out_refund']:
                    # Get the customer reference
                    customer_ref = line.move_id.ref or ''
                    # Get the invoice number
                    invoice_number = line.move_id.name or ''
                    
                    # Only add customer reference if it exists and is different from invoice number
                    if customer_ref and customer_ref != invoice_number:
                        if description:
                            description = f"{description} - {_('Customer Ref')}: {customer_ref}"
                        else:
                            description = f"{_('Customer Ref')}: {customer_ref}"
                
                result.append({
                    'id': line.id,
                    'date': line.date,
                    'move_id': line.move_id.id,
                    'move_name': line.move_id.name,
                    'ref': line.move_id.ref or '',
                    'name': description,
                    'account_id': line.account_id.id,
                    'account_code': line.account_id.code,
                    'account_name': line.account_id.name,
                    'debit': abs(line.amount_currency) if line.amount_currency > 0 else 0.0,
                    'credit': abs(line.amount_currency) if line.amount_currency < 0 else 0.0,
                    'balance': line.amount_currency,
                })
            return result
        except Exception as e:
            _logger.error("Error retrieving move lines: %s", e)
            return []
