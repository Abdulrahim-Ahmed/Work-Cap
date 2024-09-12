# -*- coding: utf-8 -*-
# from odoo import http


# class EditSale16(http.Controller):
#     @http.route('/edit_sale16/edit_sale16', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/edit_sale16/edit_sale16/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('edit_sale16.listing', {
#             'root': '/edit_sale16/edit_sale16',
#             'objects': http.request.env['edit_sale16.edit_sale16'].search([]),
#         })

#     @http.route('/edit_sale16/edit_sale16/objects/<model("edit_sale16.edit_sale16"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('edit_sale16.object', {
#             'object': obj
#         })
