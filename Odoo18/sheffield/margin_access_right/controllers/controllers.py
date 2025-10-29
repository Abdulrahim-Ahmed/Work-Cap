# -*- coding: utf-8 -*-
# from odoo import http


# class MarginAccessRight(http.Controller):
#     @http.route('/margin_access_right/margin_access_right', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/margin_access_right/margin_access_right/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('margin_access_right.listing', {
#             'root': '/margin_access_right/margin_access_right',
#             'objects': http.request.env['margin_access_right.margin_access_right'].search([]),
#         })

#     @http.route('/margin_access_right/margin_access_right/objects/<model("margin_access_right.margin_access_right"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('margin_access_right.object', {
#             'object': obj
#         })

