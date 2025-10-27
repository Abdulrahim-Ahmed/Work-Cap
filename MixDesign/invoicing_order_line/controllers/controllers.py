# -*- coding: utf-8 -*-
# from odoo import http


# class InvoicingOrderLine(http.Controller):
#     @http.route('/invoicing_order_line/invoicing_order_line', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoicing_order_line/invoicing_order_line/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoicing_order_line.listing', {
#             'root': '/invoicing_order_line/invoicing_order_line',
#             'objects': http.request.env['invoicing_order_line.invoicing_order_line'].search([]),
#         })

#     @http.route('/invoicing_order_line/invoicing_order_line/objects/<model("invoicing_order_line.invoicing_order_line"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoicing_order_line.object', {
#             'object': obj
#         })

