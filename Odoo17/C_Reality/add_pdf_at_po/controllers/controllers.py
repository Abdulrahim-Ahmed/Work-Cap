# -*- coding: utf-8 -*-
# from odoo import http


# class Test15(http.Controller):
#     @http.route('/test15/test15', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test15/test15/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test15.listing', {
#             'root': '/test15/test15',
#             'objects': http.request.env['test15.test15'].search([]),
#         })

#     @http.route('/test15/test15/objects/<model("test15.test15"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test15.object', {
#             'object': obj
#         })
