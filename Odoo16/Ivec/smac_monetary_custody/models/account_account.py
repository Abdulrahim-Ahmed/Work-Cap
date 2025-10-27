from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'
    _rec_name = 'name'
