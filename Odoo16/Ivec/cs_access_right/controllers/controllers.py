# -*- coding: utf-8 -*-
# from odoo import http


# class CsAccessRight(http.Controller):
#     @http.route('/cs_access_right/cs_access_right', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cs_access_right/cs_access_right/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cs_access_right.listing', {
#             'root': '/cs_access_right/cs_access_right',
#             'objects': http.request.env['cs_access_right.cs_access_right'].search([]),
#         })

#     @http.route('/cs_access_right/cs_access_right/objects/<model("cs_access_right.cs_access_right"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cs_access_right.object', {
#             'object': obj
#         })

