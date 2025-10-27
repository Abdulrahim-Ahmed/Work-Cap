# -*- coding: utf-8 -*-
# from odoo import http


# class DevestCutingList(http.Controller):
#     @http.route('/devest_cuting_list/devest_cuting_list', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/devest_cuting_list/devest_cuting_list/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('devest_cuting_list.listing', {
#             'root': '/devest_cuting_list/devest_cuting_list',
#             'objects': http.request.env['devest_cuting_list.devest_cuting_list'].search([]),
#         })

#     @http.route('/devest_cuting_list/devest_cuting_list/objects/<model("devest_cuting_list.devest_cuting_list"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('devest_cuting_list.object', {
#             'object': obj
#         })
