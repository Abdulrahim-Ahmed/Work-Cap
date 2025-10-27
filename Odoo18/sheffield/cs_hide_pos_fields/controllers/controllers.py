# -*- coding: utf-8 -*-
# from odoo import http


# class CsHidePosFields(http.Controller):
#     @http.route('/cs_hide_pos_fields/cs_hide_pos_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cs_hide_pos_fields/cs_hide_pos_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cs_hide_pos_fields.listing', {
#             'root': '/cs_hide_pos_fields/cs_hide_pos_fields',
#             'objects': http.request.env['cs_hide_pos_fields.cs_hide_pos_fields'].search([]),
#         })

#     @http.route('/cs_hide_pos_fields/cs_hide_pos_fields/objects/<model("cs_hide_pos_fields.cs_hide_pos_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cs_hide_pos_fields.object', {
#             'object': obj
#         })

