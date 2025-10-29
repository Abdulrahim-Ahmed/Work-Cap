# -*- coding: utf-8 -*-
# from odoo import http


# class TestModule6(http.Controller):
#     @http.route('/test_module6/test_module6', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_module6/test_module6/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_module6.listing', {
#             'root': '/test_module6/test_module6',
#             'objects': http.request.env['test_module6.test_module6'].search([]),
#         })

#     @http.route('/test_module6/test_module6/objects/<model("test_module6.test_module6"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_module6.object', {
#             'object': obj
#         })
