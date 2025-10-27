from odoo import models, fields, api
from num2words import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_total_words = fields.Char(
        string="Total in Words",
        compute="_compute_amount_total_words"
    )

    @api.depends('amount_total', 'currency_id')
    def _compute_amount_total_words(self):
        for rec in self:
            if not rec.currency_id:
                rec.amount_total_words = ''
                continue

            lang = (self.env.user.lang or 'en').split('_')[0]

            main_currency_name = rec.currency_id.currency_unit_label or rec.currency_id.name
            sub_currency_name = rec.currency_id.currency_subunit_label or "Cents"

            # Split amount into main and subunit parts
            main_part = int(rec.amount_total)
            sub_part = int(round((rec.amount_total - main_part) * 100))

            try:
                main_words = num2words(main_part, lang=lang).title()
                if sub_part > 0:
                    sub_words = num2words(sub_part, lang=lang).title()
                    rec.amount_total_words = f"{main_words} {main_currency_name} And {sub_words} {sub_currency_name}"
                else:
                    rec.amount_total_words = f"{main_words} {main_currency_name} Only"
            except NotImplementedError:
                main_words = num2words(main_part, lang='en').title()
                if sub_part > 0:
                    sub_words = num2words(sub_part, lang='en').title()
                    rec.amount_total_words = f"{main_words} {main_currency_name} And {sub_words} {sub_currency_name}"
                else:
                    rec.amount_total_words = f"{main_words} {main_currency_name} Only"
