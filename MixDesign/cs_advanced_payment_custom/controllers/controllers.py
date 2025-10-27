# -*- coding: utf-8 -*-
# from odoo import http


# class CsPrintDelivary(http.Controller):
#     @http.route('/cs_print_delivary/cs_print_delivary', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cs_print_delivary/cs_print_delivary/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cs_print_delivary.listing', {
#             'root': '/cs_print_delivary/cs_print_delivary',
#             'objects': http.request.env['cs_print_delivary.cs_print_delivary'].search([]),
#         })

#     @http.route('/cs_print_delivary/cs_print_delivary/objects/<model("cs_print_delivary.cs_print_delivary"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cs_print_delivary.object', {
#             'object': obj
#         })

