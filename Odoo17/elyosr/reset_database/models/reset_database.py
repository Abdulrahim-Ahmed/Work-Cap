from odoo import models, fields, api, _

class reset_database(models.Model):
    _name = 'reset.database'

    def update_exp_date(self):
        self.env['ir.config_parameter'].search([('key', '=', 'database.expiration_date')])[0].value = '2026-10-10 23:59:59'
