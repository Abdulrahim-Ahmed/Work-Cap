# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseViewCustom(http.Controller):
#     @http.route('/purchase_view_custom/purchase_view_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_view_custom/purchase_view_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_view_custom.listing', {
#             'root': '/purchase_view_custom/purchase_view_custom',
#             'objects': http.request.env['purchase_view_custom.purchase_view_custom'].search([]),
#         })

#     @http.route('/purchase_view_custom/purchase_view_custom/objects/<model("purchase_view_custom.purchase_view_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_view_custom.object', {
#             'object': obj
#         })

