# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_due = fields.Monetary(
        compute='_compute_total_due',
        groups='account.group_account_readonly,account.group_account_invoice,sales_team.group_sale_salesman')
    total_overdue = fields.Monetary(
        compute='_compute_total_due',
        groups='account.group_account_readonly,account.group_account_invoice,sales_team.group_sale_salesman')
