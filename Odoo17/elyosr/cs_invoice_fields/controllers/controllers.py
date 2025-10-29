# -*- coding: utf-8 -*-
# from odoo import http


# class CsInvoiceFields(http.Controller):
#     @http.route('/cs_invoice_fields/cs_invoice_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cs_invoice_fields/cs_invoice_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cs_invoice_fields.listing', {
#             'root': '/cs_invoice_fields/cs_invoice_fields',
#             'objects': http.request.env['cs_invoice_fields.cs_invoice_fields'].search([]),
#         })

#     @http.route('/cs_invoice_fields/cs_invoice_fields/objects/<model("cs_invoice_fields.cs_invoice_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cs_invoice_fields.object', {
#             'object': obj
#         })

