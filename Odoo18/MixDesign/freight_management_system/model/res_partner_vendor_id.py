# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartnerVendorRef(models.Model):
    _inherit = 'res.partner'

    md_company_id = fields.Char(string='MD Company Id', required=False)
