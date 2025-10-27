# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceBillValue(http.Controller):
#     @http.route('/invoice_bill_value/invoice_bill_value', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_bill_value/invoice_bill_value/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_bill_value.listing', {
#             'root': '/invoice_bill_value/invoice_bill_value',
#             'objects': http.request.env['invoice_bill_value.invoice_bill_value'].search([]),
#         })

#     @http.route('/invoice_bill_value/invoice_bill_value/objects/<model("invoice_bill_value.invoice_bill_value"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_bill_value.object', {
#             'object': obj
#         })

