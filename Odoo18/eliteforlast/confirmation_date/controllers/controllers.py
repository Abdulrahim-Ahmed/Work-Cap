# -*- coding: utf-8 -*-
# from odoo import http


# class ConfirmationDate(http.Controller):
#     @http.route('/confirmation_date/confirmation_date', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/confirmation_date/confirmation_date/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('confirmation_date.listing', {
#             'root': '/confirmation_date/confirmation_date',
#             'objects': http.request.env['confirmation_date.confirmation_date'].search([]),
#         })

#     @http.route('/confirmation_date/confirmation_date/objects/<model("confirmation_date.confirmation_date"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('confirmation_date.object', {
#             'object': obj
#         })

