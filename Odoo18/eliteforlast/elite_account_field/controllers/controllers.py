# -*- coding: utf-8 -*-
# from odoo import http


# class EliteAccountField(http.Controller):
#     @http.route('/elite_account_field/elite_account_field', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/elite_account_field/elite_account_field/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('elite_account_field.listing', {
#             'root': '/elite_account_field/elite_account_field',
#             'objects': http.request.env['elite_account_field.elite_account_field'].search([]),
#         })

#     @http.route('/elite_account_field/elite_account_field/objects/<model("elite_account_field.elite_account_field"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('elite_account_field.object', {
#             'object': obj
#         })

