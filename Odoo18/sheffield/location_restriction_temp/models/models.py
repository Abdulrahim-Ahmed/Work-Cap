# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_location_ids = fields.Many2many(
        'stock.location',
        'res_users_stock_location_rel',
        'user_id',
        'location_id',
        string="Allowed Source Locations",
        domain="[('usage', '=', 'internal')]"
    )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        user = self.env.user
        if view_type == 'form' and user.allowed_location_ids:
            doc = etree.XML(res['arch'])
            for field in doc.xpath("//field[@name='location_id']"):
                field.set('domain', "[('id', 'in', %s)]" % user.allowed_location_ids.ids)
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @api.model
    def create(self, vals):
        user = self.env.user
        if vals.get('location_id') and user.allowed_location_ids:
            if vals['location_id'] not in user.allowed_location_ids.ids:
                raise ValidationError(_("You are not allowed to use this source location."))
        return super().create(vals)

    def write(self, vals):
        user = self.env.user
        if vals.get('location_id') and user.allowed_location_ids:
            if vals['location_id'] not in user.allowed_location_ids.ids:
                raise ValidationError(_("You are not allowed to use this source location."))
        return super().write(vals)
