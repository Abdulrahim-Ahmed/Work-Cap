# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.tools import float_is_zero, SQL
from itertools import chain

_logger = logging.getLogger(__name__)


class MulticurrencyRevaluationReportCustomHandler(models.AbstractModel):
    """
    Extend the existing Multicurrency Revaluation Report Handler
    to add Realized Gains/Loss functionality
    """
    _inherit = 'account.multicurrency.revaluation.report.handler'

    def _report_custom_engine_realized_currency_gains(self, expressions, options, date_scope, current_groupby,
                                                      next_groupby, offset=0, limit=None, warnings=None):
        """Handle realized currency gains"""
        return self._realized_currency_get_custom_lines(options, 'gains', current_groupby, next_groupby, offset=offset,
                                                        limit=limit)

    def _report_custom_engine_realized_currency_losses(self, expressions, options, date_scope, current_groupby,
                                                       next_groupby, offset=0, limit=None, warnings=None):
        """Handle realized currency losses"""
        return self._realized_currency_get_custom_lines(options, 'losses', current_groupby, next_groupby, offset=offset,
                                                        limit=limit)

    def _realized_currency_get_custom_lines(self, options, line_code, current_groupby, next_groupby, offset=0,
                                            limit=None):
        """
        Get custom lines for realized currency gains/losses
        Calculates the actual realized exchange differences when payments are made
        Uses the exchange rate at payment date, not current rate
        """

        def build_result_dict(report, query_res):
            return {
                'balance_currency': query_res.get('balance_currency') if query_res and len(
                    query_res.get('currency_id', [])) == 1 else None,
                'currency_id': query_res.get('currency_id', [None])[0] if query_res and len(
                    query_res.get('currency_id', [])) == 1 else None,
                'balance_operation': query_res.get('balance_operation', 0.0) if query_res else 0.0,
                'balance_current': query_res.get('balance_current', 0.0) if query_res else 0.0,
                'adjustment': query_res.get('adjustment', 0.0) if query_res else 0.0,
                'has_sublines': query_res.get('aml_count', 0) > 0 if query_res else False,
            }

        report = self.env['account.report'].browse(options['report_id'])
        report._check_groupby_fields(
            (next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))

        # No need to run any SQL if we're computing the main line
        if not current_groupby:
            return {
                'balance_currency': None,
                'currency_id': None,
                'balance_operation': None,
                'balance_current': None,
                'adjustment': None,
                'has_sublines': False,
            }

        date_to = options['date']['date_to']
        date_from = options['date']['date_from']

        # Use the same query structure approach
        base_query = report._get_report_query(options, 'strict_range')
        groupby_field_sql = self.env['account.move.line']._field_to_sql("account_move_line", current_groupby,
                                                                        base_query)
        tail_query = report._get_engine_query_tail(offset, limit)

        # Get current currency rates for calculation - similar to unrealized report
        currency_values_query = "(VALUES {})".format(', '.join("(%s, %s)" for rate in options['currency_rates']))
        params = list(
            chain.from_iterable((cur['currency_id'], cur['rate']) for cur in options['currency_rates'].values()))
        custom_currency_table_query = SQL(currency_values_query, *params)

        full_query = SQL(
            """
            WITH custom_currency_table(currency_id, rate) AS (%(custom_currency_table_query)s)

            SELECT
                   %(groupby_field_sql)s AS grouping_key,
                   ARRAY_AGG(DISTINCT(account_move_line.currency_id)) AS currency_id,
                   SUM(ABS(account_move_line.amount_currency)) AS balance_currency,
                   SUM(ABS(account_move_line.balance)) AS balance_operation,
                   -- Balance at payment date rate: use the rate that was active when payment was made
                   SUM(ABS(account_move_line.amount_currency) / COALESCE(payment_rate.rate, 1.0)) AS balance_current,    
                   -- Adjustment: balance_current - balance_operation (actual realized gain/loss)
                   SUM((ABS(account_move_line.amount_currency) / COALESCE(payment_rate.rate, 1.0)) - ABS(account_move_line.balance)) AS adjustment,
                   COUNT(DISTINCT account_move_line.id) AS aml_count

              FROM %(table_references)s
              JOIN account_account account ON account_move_line.account_id = account.id
              JOIN custom_currency_table ON account_move_line.currency_id = custom_currency_table.currency_id
              JOIN account_partial_reconcile part ON (
                  part.debit_move_id = account_move_line.id OR part.credit_move_id = account_move_line.id
              )
              JOIN account_move exchange_move ON exchange_move.id = part.exchange_move_id
              JOIN account_move_line exchange_aml ON (
                  exchange_aml.move_id = exchange_move.id 
                  AND exchange_aml.account_id = account_move_line.account_id
              )
              -- Get the currency rate that was active at the time of payment
              LEFT JOIN LATERAL (
                  SELECT 
                      CASE 
                          -- If currency rate exists for exact date, use it
                          WHEN EXISTS (
                              SELECT 1 FROM res_currency_rate r1 
                              WHERE r1.currency_id = account_move_line.currency_id 
                                AND r1.name = part.max_date
                                AND (r1.company_id = account_move_line.company_id OR r1.company_id IS NULL)
                          ) THEN (
                              SELECT r2.rate 
                              FROM res_currency_rate r2 
                              WHERE r2.currency_id = account_move_line.currency_id 
                                AND r2.name = part.max_date
                                AND (r2.company_id = account_move_line.company_id OR r2.company_id IS NULL)
                              ORDER BY r2.company_id DESC NULLS LAST
                              LIMIT 1
                          )
                          -- Otherwise get the most recent rate before or on payment date
                          ELSE (
                              SELECT r3.rate 
                              FROM res_currency_rate r3 
                              WHERE r3.currency_id = account_move_line.currency_id
                                AND r3.name <= part.max_date
                                AND (r3.company_id = account_move_line.company_id OR r3.company_id IS NULL)
                              ORDER BY r3.name DESC, r3.company_id DESC NULLS LAST
                              LIMIT 1
                          )
                      END as rate
              ) payment_rate ON true

             WHERE %(search_condition)s
               -- Get reconciliations that happened in the period
               AND part.max_date BETWEEN %(date_from)s AND %(date_to)s

               -- Only accounts that can have currency differences
               AND account.account_type IN ('asset_receivable', 'liability_payable')

               -- Only include foreign currency transactions
               AND account_move_line.currency_id != account_move_line.company_currency_id

               -- Only include exchange moves that exist and are in the period
               AND exchange_move.id IS NOT NULL
               AND exchange_move.date BETWEEN %(date_from)s AND %(date_to)s

          GROUP BY %(groupby_field_sql)s

          -- Only show lines where there's an actual realized gain/loss
          HAVING ABS(SUM((ABS(account_move_line.amount_currency) / COALESCE(payment_rate.rate, custom_currency_table.rate)) - ABS(account_move_line.balance))) > 0.01
          """ + (f"""
          -- Filter for gains vs losses
          AND SUM((ABS(account_move_line.amount_currency) / COALESCE(payment_rate.rate, custom_currency_table.rate)) - ABS(account_move_line.balance)) {'>' if line_code == 'gains' else '<'} 0
          """ if line_code in ['gains', 'losses'] else "") + f"""

          ORDER BY grouping_key
          %(tail_query)s
            """,
            custom_currency_table_query=custom_currency_table_query,
            groupby_field_sql=groupby_field_sql,
            table_references=base_query.from_clause,
            date_to=date_to,
            date_from=date_from,
            tail_query=tail_query,
            search_condition=base_query.where_clause,
        )

        self._cr.execute(full_query)
        query_res_lines = self._cr.dictfetchall()

        if not current_groupby:
            return build_result_dict(report, query_res_lines and query_res_lines[0] or {})
        else:
            rslt = []
            for query_res in query_res_lines:
                grouping_key = query_res.get('grouping_key') if current_groupby else None
                rslt.append((grouping_key, build_result_dict(report, query_res)))
            return rslt

    def _get_realized_exchange_entries(self, options):
        """
        Helper method to get actual exchange entries that have been posted
        for realized gains/losses
        """
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']

        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('journal_id.type', '=', 'general'),
            ('ref', 'ilike', 'Exchange'),
            ('state', '=', 'posted')
        ]

        return self.env['account.move'].search(domain)

    def _compute_total_realized_gains_losses(self, options):
        """
        Compute the total realized gains and losses for the period
        """
        gains_data = self._realized_currency_get_custom_lines(options, 'gains', None, None)
        losses_data = self._realized_currency_get_custom_lines(options, 'losses', None, None)

        total_gains = gains_data.get('adjustment', 0.0) if isinstance(gains_data, dict) else 0.0
        total_losses = abs(losses_data.get('adjustment', 0.0)) if isinstance(losses_data, dict) else 0.0

        return {
            'total_gains': total_gains,
            'total_losses': total_losses,
            'net_result': total_gains - total_losses
        }
