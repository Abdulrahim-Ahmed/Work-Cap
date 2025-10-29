# -*- coding: utf-8 -*-
# from odoo import http


# class PosPrintInvoice(http.Controller):
#     @http.route('/pos_print_invoice/pos_print_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_print_invoice/pos_print_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_print_invoice.listing', {
#             'root': '/pos_print_invoice/pos_print_invoice',
#             'objects': http.request.env['pos_print_invoice.pos_print_invoice'].search([]),
#         })

#     @http.route('/pos_print_invoice/pos_print_invoice/objects/<model("pos_print_invoice.pos_print_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_print_invoice.object', {
#             'object': obj
#         })
