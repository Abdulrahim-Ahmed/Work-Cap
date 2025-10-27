# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    analytic_distribution = fields.Json(
        string="Analytic Distribution"
    )

    analytic_precision = fields.Integer(
        string="Analytic Precision",
        default=lambda self: self.env['decimal.precision'].precision_get('Analytic')
    )

    @api.onchange('analytic_distribution')
    def _onchange_analytic_distribution(self):
        """Apply analytic distribution to all invoice/bill lines"""
        for move in self:
            if move.analytic_distribution:
                for line in move.invoice_line_ids:
                    line.analytic_distribution = move.analytic_distribution


    # analytic_account_id = fields.Many2one(
    #     'account.analytic.account',
    #     string="Analytic Account"
    # )
    #
    # @api.onchange('analytic_account_id')
    # def _onchange_analytic_account_id(self):
    #     """Apply analytic account to all lines using analytic_distribution"""
    #     for move in self:
    #         if move.analytic_account_id:
    #             for line in move.invoice_line_ids:
    #                 line.analytic_distribution = {move.analytic_account_id.id: 100}
