# -*- coding: utf-8 -*-
# from odoo import http


# class PoNumber(http.Controller):
#     @http.route('/po_number/po_number', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/po_number/po_number/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('po_number.listing', {
#             'root': '/po_number/po_number',
#             'objects': http.request.env['po_number.po_number'].search([]),
#         })

#     @http.route('/po_number/po_number/objects/<model("po_number.po_number"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('po_number.object', {
#             'object': obj
#         })
