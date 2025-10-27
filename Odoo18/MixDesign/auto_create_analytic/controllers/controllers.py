# -*- coding: utf-8 -*-
# from odoo import http


# class AutoCreateAnalytic(http.Controller):
#     @http.route('/auto_create_analytic/auto_create_analytic', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auto_create_analytic/auto_create_analytic/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('auto_create_analytic.listing', {
#             'root': '/auto_create_analytic/auto_create_analytic',
#             'objects': http.request.env['auto_create_analytic.auto_create_analytic'].search([]),
#         })

#     @http.route('/auto_create_analytic/auto_create_analytic/objects/<model("auto_create_analytic.auto_create_analytic"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auto_create_analytic.object', {
#             'object': obj
#         })

