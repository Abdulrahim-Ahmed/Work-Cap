# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_advanced_payment = fields.Boolean(
        string='Advanced Payment',
        default=False,
        help="Check this to create an advanced payment with custom journal entries"
    )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        """Override to handle advanced payment logic"""
        line_vals_list = super()._prepare_move_line_default_vals(write_off_line_vals, force_balance)
        
        if self.is_advanced_payment:
            company = self.company_id
            
            if self.partner_type == 'supplier' and company.vendor_debit_account_id:
                # For vendor advanced payment, use vendor_debit_account
                for line_vals in line_vals_list:
                    if line_vals.get('account_id') == self.destination_account_id.id:
                        line_vals['account_id'] = company.vendor_debit_account_id.id
                        
            elif self.partner_type == 'customer' and company.customer_credit_account_id:
                # For customer advanced payment, use customer_credit_account
                for line_vals in line_vals_list:
                    if line_vals.get('account_id') == self.destination_account_id.id:
                        line_vals['account_id'] = company.customer_credit_account_id.id

        return line_vals_list

    @api.model
    def create(self, vals):
        """Override create to validate advanced payment configuration"""
        payment = super().create(vals)
        
        if payment.is_advanced_payment:
            company = payment.company_id
            
            if payment.partner_type == 'supplier' and not company.vendor_debit_account_id:
                raise UserError(_("Please configure the Vendor Debit Account in Accounting Settings before creating vendor advanced payments."))
                
            elif payment.partner_type == 'customer' and not company.customer_credit_account_id:
                raise UserError(_("Please configure the Customer Credit Account in Accounting Settings before creating customer advanced payments."))
                
        return payment