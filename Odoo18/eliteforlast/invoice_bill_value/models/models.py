from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    def default_get(self, fields_list):

        defaults = super().default_get(fields_list)
        journal_model = self.env['account.journal']

        if 'move_type' in defaults:
            if defaults['move_type'] == 'out_invoice':
                journal = journal_model.search([('type', '=', 'sale')], limit=1)
                if journal:
                    defaults['journal_id'] = journal.id
            elif defaults['move_type'] == 'in_invoice':
                journal = journal_model.search([('type', '=', 'purchase')], limit=1)
                if journal:
                    defaults['journal_id'] = journal.id

        return defaults
