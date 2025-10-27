# -*- coding: utf-8 -*-
# from odoo import http


# class AllowedDiscountPercentage(http.Controller):
#     @http.route('/allowed_discount_percentage/allowed_discount_percentage', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/allowed_discount_percentage/allowed_discount_percentage/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('allowed_discount_percentage.listing', {
#             'root': '/allowed_discount_percentage/allowed_discount_percentage',
#             'objects': http.request.env['allowed_discount_percentage.allowed_discount_percentage'].search([]),
#         })

#     @http.route('/allowed_discount_percentage/allowed_discount_percentage/objects/<model("allowed_discount_percentage.allowed_discount_percentage"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('allowed_discount_percentage.object', {
#             'object': obj
#         })

