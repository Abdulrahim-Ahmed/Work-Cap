# -*- coding: utf-8 -*-
# from odoo import http


# class NewFieldsAtSo(http.Controller):
#     @http.route('/new_fields_at_so/new_fields_at_so', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/new_fields_at_so/new_fields_at_so/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('new_fields_at_so.listing', {
#             'root': '/new_fields_at_so/new_fields_at_so',
#             'objects': http.request.env['new_fields_at_so.new_fields_at_so'].search([]),
#         })

#     @http.route('/new_fields_at_so/new_fields_at_so/objects/<model("new_fields_at_so.new_fields_at_so"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('new_fields_at_so.object', {
#             'object': obj
#         })

