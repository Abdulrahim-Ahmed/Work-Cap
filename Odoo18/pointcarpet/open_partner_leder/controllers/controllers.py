# -*- coding: utf-8 -*-
# from odoo import http


# class OpenPartnerLeder(http.Controller):
#     @http.route('/open_partner_leder/open_partner_leder', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/open_partner_leder/open_partner_leder/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('open_partner_leder.listing', {
#             'root': '/open_partner_leder/open_partner_leder',
#             'objects': http.request.env['open_partner_leder.open_partner_leder'].search([]),
#         })

#     @http.route('/open_partner_leder/open_partner_leder/objects/<model("open_partner_leder.open_partner_leder"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('open_partner_leder.object', {
#             'object': obj
#         })

