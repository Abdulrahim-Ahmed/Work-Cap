# -*- coding: utf-8 -*-
# from odoo import http


# class CustomTagsSearch(http.Controller):
#     @http.route('/custom_tags_search/custom_tags_search', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_tags_search/custom_tags_search/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_tags_search.listing', {
#             'root': '/custom_tags_search/custom_tags_search',
#             'objects': http.request.env['custom_tags_search.custom_tags_search'].search([]),
#         })

#     @http.route('/custom_tags_search/custom_tags_search/objects/<model("custom_tags_search.custom_tags_search"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_tags_search.object', {
#             'object': obj
#         })
