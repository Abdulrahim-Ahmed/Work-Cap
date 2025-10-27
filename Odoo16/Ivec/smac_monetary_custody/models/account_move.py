from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    request_custody_id = fields.Many2one('request.cash.custody', string='Request Cash Custody')
    reconcile_custody_id = fields.Many2one('reconcile.cash.custody', string='Reconcile Cash Custody')
