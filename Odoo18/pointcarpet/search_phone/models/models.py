# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # البحث باستخدام الاسم الافتراضي
        res = super(ResPartner, self).name_search(name, args=args, operator=operator, limit=limit)

        if not res:
            # البحث باستخدام رقم الهاتف
            partners = self.search([('phone', operator, name)] + args, limit=limit)
            res = partners.name_get()

        return res
