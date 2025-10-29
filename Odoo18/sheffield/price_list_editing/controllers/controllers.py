# -*- coding: utf-8 -*-
# from odoo import http


# class PriceListEditing(http.Controller):
#     @http.route('/price_list_editing/price_list_editing', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/price_list_editing/price_list_editing/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('price_list_editing.listing', {
#             'root': '/price_list_editing/price_list_editing',
#             'objects': http.request.env['price_list_editing.price_list_editing'].search([]),
#         })

#     @http.route('/price_list_editing/price_list_editing/objects/<model("price_list_editing.price_list_editing"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('price_list_editing.object', {
#             'object': obj
#         })

