# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockScrapAnalyticAccount(models.Model):
    _inherit = "stock.scrap"

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    def do_scrap(self):
        """Override do_scrap to apply analytic account to journal entries"""
        # Call the original do_scrap method
        res = super(StockScrapAnalyticAccount, self).do_scrap()

        # If we have an analytic account, update the journal entries
        if self.analytic_account_id and self.move_ids:
            self._apply_analytic_to_journal_entries()

        return res

    def _apply_analytic_to_journal_entries(self):
        """Apply analytic distribution to journal entries created by the scrap"""
        analytic_distribution = {str(self.analytic_account_id.id): 100.0}

        # Look for journal entries related to this stock move
        # Method 1: Direct approach through stock move
        if hasattr(self.move_ids, 'account_move_ids') and self.move_ids.account_move_ids:
            for account_move in self.move_ids.account_move_ids:
                self._update_journal_entry_analytics(account_move, analytic_distribution)

        # Method 2: Search for related journal entries
        else:
            # Search for journal entries that might be related to this scrap
            domain = [
                ('ref', 'ilike', self.name),
                ('state', '=', 'posted')
            ]
            journal_entries = self.env['account.move'].search(domain)
            for entry in journal_entries:
                self._update_journal_entry_analytics(entry, analytic_distribution)

    def _update_journal_entry_analytics(self, account_move, analytic_distribution):
        """Update analytic distribution on journal entry lines"""
        for line in account_move.line_ids:
            # Apply analytic distribution to both debit and credit lines
            # Skip lines that are reconciliation accounts (like customer/supplier accounts)
            if (line.account_id and
                line.account_id.account_type not in ['asset_receivable', 'liability_payable'] and
                (line.debit > 0 or line.credit > 0)):  # Only lines with actual amounts
                try:
                    line.write({'analytic_distribution': analytic_distribution})
                except Exception as e:
                    # Log the error but don't break the process
                    _logger.warning(f"Could not set analytic distribution on journal entry line {line.id}: {e}")

    # Alternative approach: Hook into the journal entry creation process
    @api.model
    def _prepare_account_move_vals(self, move, qty, cost):
        """Override if this method exists to inject analytic data"""
        vals = super()._prepare_account_move_vals(move, qty, cost)

        # Find the scrap record that created this move
        scrap = self.search([('move_id', '=', move.id)], limit=1)

        if scrap and scrap.analytic_account_id:
            analytic_distribution = {str(scrap.analytic_account_id.id): 100.0}

            # Add analytic distribution to line items
            if 'line_ids' in vals:
                for line_vals in vals['line_ids']:
                    if isinstance(line_vals, (list, tuple)) and len(line_vals) >= 3:
                        line_data = line_vals[2]  # (0, 0, {line_data})
                        if isinstance(line_data, dict):
                            # Only add to lines that should have analytics
                            account_id = line_data.get('account_id')
                            if account_id:
                                account = self.env['account.account'].browse(account_id)
                                if account.account_type not in ['asset_receivable', 'liability_payable']:
                                    line_data['analytic_distribution'] = analytic_distribution

        return vals

    @api.model
    def create_multiple_scraps(self, scrap_data_list):
        """
        Helper method to create multiple scrap records efficiently
        Returns a list of created scrap IDs and any errors encountered
        """
        created_scraps = []
        errors = []
        
        for scrap_data in scrap_data_list:
            try:
                scrap = self.create(scrap_data)
                created_scraps.append({
                    'id': scrap.id,
                    'name': scrap.name,
                    'product_id': scrap.product_id.id,
                    'product_name': scrap.product_id.name,
                    'scrap_qty': scrap.scrap_qty,
                })
            except Exception as e:
                product_name = scrap_data.get('product_id', 'Unknown')
                if isinstance(product_name, int):
                    try:
                        product = self.env['product.product'].browse(product_name)
                        product_name = product.name
                    except:
                        product_name = f"Product ID {product_name}"
                
                errors.append({
                    'product_name': product_name,
                    'error': str(e)
                })
                _logger.warning(f"Failed to create scrap for product {product_name}: {e}")
        
        return {
            'created_scraps': created_scraps,
            'errors': errors,
            'success_count': len(created_scraps),
            'error_count': len(errors)
        }


# Enhanced alternative approach using account move creation hook
class AccountMoveScrapAnalytic(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to add analytic distribution from related scrap"""
        moves = super().create(vals_list)

        for move in moves:
            # Check if this journal entry is related to a scrap
            if move.ref and 'scrap' in move.ref.lower():
                # Try to find the related scrap
                scrap = self.env['stock.scrap'].search([
                    ('name', '=', move.ref)
                ], limit=1)

                if scrap and scrap.analytic_account_id:
                    analytic_distribution = {str(scrap.analytic_account_id.id): 100.0}

                    # Update both debit and credit lines (exclude reconciliation accounts)
                    lines_to_update = move.line_ids.filtered(
                        lambda l: l.account_id and
                                  l.account_id.account_type not in ['asset_receivable', 'liability_payable'] and
                                  (l.debit > 0 or l.credit > 0)
                    )

                    for line in lines_to_update:
                        line.analytic_distribution = analytic_distribution

        return moves
