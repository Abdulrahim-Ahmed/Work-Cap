# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class smac_monetary_custody(models.Model):
#     _name = 'smac_monetary_custody.smac_monetary_custody'
#     _description = 'smac_monetary_custody.smac_monetary_custody'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
