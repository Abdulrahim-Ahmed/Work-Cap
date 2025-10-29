from odoo import models, fields, api, _


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Analytic Account",
        copy=False,
        check_company=True)
