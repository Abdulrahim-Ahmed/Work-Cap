# -*- coding: utf-8 -*-
# from odoo import http


# class ExtraRights(http.Controller):
#     @http.route('/extra_rights/extra_rights', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/extra_rights/extra_rights/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('extra_rights.listing', {
#             'root': '/extra_rights/extra_rights',
#             'objects': http.request.env['extra_rights.extra_rights'].search([]),
#         })

#     @http.route('/extra_rights/extra_rights/objects/<model("extra_rights.extra_rights"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('extra_rights.object', {
#             'object': obj
#         })

