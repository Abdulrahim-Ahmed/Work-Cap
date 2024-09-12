# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_max_conf = fields.Integer(related="company_id.sale_max_co", string="Max Price", required=False)
    warning_title = fields.Char(string="Warning Title", related="company_id.warning_title", required=False)
    warning_message = fields.Text(string="Warning Message", related="company_id.warning_message", required=False)
    low_warning_title = fields.Char(string="Low Warning Title", related="company_id.low_warning_title", required=False)
    low_warning_message = fields.Text(string="Low Warning Message", related="company_id.low_warning_message",
                                      required=False)


    @api.onchange('sale_max_conf', 'warning_title', 'warning_message', 'low_warning_title', 'low_warning_message')
    def _onchange_sale_conf(self):
        # Update the corresponding company settings
        company = self.env.user.company_id
        company.sale_max_co = self.sale_max_conf
        company.warning_title = self.warning_title
        company.warning_message = self.warning_message
        company.low_warning_title = self.low_warning_title
        company.low_warning_message = self.low_warning_message


class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_max_co = fields.Integer(string="Default Max Price", default=0)
    warning_title = fields.Char(string="Warning Title")
    warning_message = fields.Text(string="Warning Message")
    low_warning_title = fields.Char(string="Low Warning Title")
    low_warning_message = fields.Text(string="Low Warning Message")
