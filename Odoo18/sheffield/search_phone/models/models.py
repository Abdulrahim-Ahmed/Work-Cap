# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _normalize_input_number(self, number):
        number = re.sub(r'\D', '', str(number or ''))
        if number.startswith('0') and len(number) == 11:
            return '+20 {} {} {}'.format(number[1:4], number[4:7], number[7:])
        return number

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        res = super().name_search(name, args=args, operator=operator, limit=limit)

        if not res and name and name.isdigit():
            formatted_number = self._normalize_input_number(name)
            domain = ['|', ('phone', 'ilike', formatted_number), ('mobile', 'ilike', formatted_number)]
            partners = self.search(domain + args, limit=limit)
            res = [(partner.id, partner.display_name) for partner in partners]

        return res

    # Working version with no auto format for numbers
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     res = super().name_search(name, args=args, operator=operator, limit=limit)
    #
    #     if not res:
    #         # Search by phone number
    #         partners = self.search([('phone', operator, name)] + args, limit=limit)
    #         res = [(partner.id, partner.display_name) for partner in partners]  # Replace name_get()
    #
    #     return res

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     # البحث باستخدام الاسم الافتراضي
    #     res = super(ResPartner, self).name_search(name, args=args, operator=operator, limit=limit)
    #
    #     if not res:
    #         # البحث باستخدام رقم الهاتف
    #         partners = self.search([('phone', operator, name)] + args, limit=limit)
    #         res = partners.name_get()
    #
    #     return res
