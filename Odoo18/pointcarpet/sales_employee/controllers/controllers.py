# -*- coding: utf-8 -*-
# from odoo import http


# class TestEmployees(http.Controller):
#     @http.route('/test_employees/test_employees', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_employees/test_employees/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_employees.listing', {
#             'root': '/test_employees/test_employees',
#             'objects': http.request.env['test_employees.test_employees'].search([]),
#         })

#     @http.route('/test_employees/test_employees/objects/<model("test_employees.test_employees"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_employees.object', {
#             'object': obj
#         })

