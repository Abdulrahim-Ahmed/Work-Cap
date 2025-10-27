# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleConfirmationDate(models.Model):
    _inherit = 'sale.order'

    confirmation_date = fields.Datetime('Confirmation Date')

    def action_confirm(self):
        res = super(SaleConfirmationDate, self).action_confirm()
        for order in self:
            if not order.confirmation_date:
                order.confirmation_date = fields.Datetime.now()
        return res


class SaleReport(models.Model):
    _inherit = 'sale.report'

    confirmation_date = fields.Datetime('Confirmation Date')

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['confirmation_date'] = "s.confirmation_date"
        return res
