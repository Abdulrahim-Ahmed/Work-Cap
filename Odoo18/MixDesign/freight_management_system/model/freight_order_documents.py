# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class FreightOrderDocuments(models.Model):
    """Freight order lines Documents"""
    _name = 'freight.order.documents'
    _description = 'Freight Order Documents'

    freight_id = fields.Many2one('freight.order', string='Freight Order',
                                 help='Relation from freight order')
    document_name = fields.Char(string=" Document Name", required=False)
    document_attachment = fields.Binary(string=" Attachment", store=True, attachment=True,
                                        help='Upload the document')


class FreightOrderLogs(models.Model):
    """Freight order lines Logs"""
    _name = 'freight.order.logs'
    _description = 'Freight Order Logs'

    freight_id = fields.Many2one('freight.order', string='Freight Order',
                                 help='Relation from freight order')
    user_id = fields.Many2one('res.users', string="User")
    comment = fields.Char(string="Comment")
