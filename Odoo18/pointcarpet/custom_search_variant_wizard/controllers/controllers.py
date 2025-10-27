# -*- coding: utf-8 -*-
# from odoo import http


# class CustomSearchVariantWizard(http.Controller):
#     @http.route('/custom_search_variant_wizard/custom_search_variant_wizard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_search_variant_wizard/custom_search_variant_wizard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_search_variant_wizard.listing', {
#             'root': '/custom_search_variant_wizard/custom_search_variant_wizard',
#             'objects': http.request.env['custom_search_variant_wizard.custom_search_variant_wizard'].search([]),
#         })

#     @http.route('/custom_search_variant_wizard/custom_search_variant_wizard/objects/<model("custom_search_variant_wizard.custom_search_variant_wizard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_search_variant_wizard.object', {
#             'object': obj
#         })

