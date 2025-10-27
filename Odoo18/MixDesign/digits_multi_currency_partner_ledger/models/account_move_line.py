# -*- coding: utf-8 -*-
###############################################################################
#
#    Digital Integrated Transformation Solutions (DigitsCode)
#    Copyright (C) 2025-TODAY Digital Integrated Transformation Solutions (<https://www.digitscode.com>).
#    Author: Digital Integrated Transformation Solutions (<https://www.digitscode.com>)
#
###############################################################################

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_amounts_in_currency(self, currency):
        """
        Get the debit and credit amounts in the specified currency
        
        :param currency: The currency to convert to
        :return: Dictionary with debit and credit in specified currency
        """
        self.ensure_one()
        result = {
            'debit_currency': 0.0,
            'credit_currency': 0.0,
            'balance_currency': 0.0,
        }
        
        if not currency:
            return result
            
        # If the line currency is the same as requested currency
        if self.currency_id == currency:
            if self.amount_currency > 0:
                result['debit_currency'] = abs(self.amount_currency)
            else:
                result['credit_currency'] = abs(self.amount_currency)
            result['balance_currency'] = self.amount_currency
            return result
            
        # If the company currency is the same as requested currency
        if self.company_currency_id == currency:
            result['debit_currency'] = self.debit
            result['credit_currency'] = self.credit
            result['balance_currency'] = self.balance
            return result
            
        # Need to convert from the line currency to the requested currency
        company = self.company_id or self.env.company
        date = self.date or fields.Date.context_today(self)
        
        # Convert amount currency to company currency
        amount_company = self.currency_id._convert(
            self.amount_currency, self.company_currency_id, company, date)
            
        # Convert company currency to requested currency
        amount_requested = self.company_currency_id._convert(
            amount_company, currency, company, date)
            
        if amount_requested > 0:
            result['debit_currency'] = abs(amount_requested)
        else:
            result['credit_currency'] = abs(amount_requested)
        result['balance_currency'] = amount_requested
        
        return result
