# -*- coding: utf-8 -*-
# from odoo import http


# class FollowUpSale(http.Controller):
#     @http.route('/follow_up_sale/follow_up_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/follow_up_sale/follow_up_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('follow_up_sale.listing', {
#             'root': '/follow_up_sale/follow_up_sale',
#             'objects': http.request.env['follow_up_sale.follow_up_sale'].search([]),
#         })

#     @http.route('/follow_up_sale/follow_up_sale/objects/<model("follow_up_sale.follow_up_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('follow_up_sale.object', {
#             'object': obj
#         })
