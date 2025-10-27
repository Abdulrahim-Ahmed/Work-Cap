# -*- coding: utf-8 -*-
# from odoo import http


# class SmacMonetaryCustody(http.Controller):
#     @http.route('/smac_monetary_custody/smac_monetary_custody', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smac_monetary_custody/smac_monetary_custody/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('smac_monetary_custody.listing', {
#             'root': '/smac_monetary_custody/smac_monetary_custody',
#             'objects': http.request.env['smac_monetary_custody.smac_monetary_custody'].search([]),
#         })

#     @http.route('/smac_monetary_custody/smac_monetary_custody/objects/<model("smac_monetary_custody.smac_monetary_custody"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smac_monetary_custody.object', {
#             'object': obj
#         })
