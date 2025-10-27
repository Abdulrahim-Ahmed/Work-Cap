# -*- coding: utf-8 -*-
# from odoo import http


# class DiscountInAmount(http.Controller):
#     @http.route('/discount_in_amount/discount_in_amount', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/discount_in_amount/discount_in_amount/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('discount_in_amount.listing', {
#             'root': '/discount_in_amount/discount_in_amount',
#             'objects': http.request.env['discount_in_amount.discount_in_amount'].search([]),
#         })

#     @http.route('/discount_in_amount/discount_in_amount/objects/<model("discount_in_amount.discount_in_amount"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('discount_in_amount.object', {
#             'object': obj
#         })

