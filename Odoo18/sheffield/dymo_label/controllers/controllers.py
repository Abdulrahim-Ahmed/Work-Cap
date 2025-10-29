# -*- coding: utf-8 -*-
# from odoo import http


# class NewLabel(http.Controller):
#     @http.route('/dymo_label/dymo_label', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dymo_label/dymo_label/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dymo_label.listing', {
#             'root': '/dymo_label/dymo_label',
#             'objects': http.request.env['dymo_label.dymo_label'].search([]),
#         })

#     @http.route('/dymo_label/dymo_label/objects/<model("dymo_label.dymo_label"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dymo_label.object', {
#             'object': obj
#         })

