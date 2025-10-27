# -*- coding: utf-8 -*-
# from odoo import http


# class EditDate(http.Controller):
#     @http.route('/edit_date/edit_date', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/edit_date/edit_date/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('edit_date.listing', {
#             'root': '/edit_date/edit_date',
#             'objects': http.request.env['edit_date.edit_date'].search([]),
#         })

#     @http.route('/edit_date/edit_date/objects/<model("edit_date.edit_date"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('edit_date.object', {
#             'object': obj
#         })
