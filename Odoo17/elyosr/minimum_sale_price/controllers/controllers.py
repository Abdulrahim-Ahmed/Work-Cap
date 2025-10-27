# -*- coding: utf-8 -*-
# from odoo import http


# class MinimumSalePrice(http.Controller):
#     @http.route('/minimum_sale_price/minimum_sale_price', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/minimum_sale_price/minimum_sale_price/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('minimum_sale_price.listing', {
#             'root': '/minimum_sale_price/minimum_sale_price',
#             'objects': http.request.env['minimum_sale_price.minimum_sale_price'].search([]),
#         })

#     @http.route('/minimum_sale_price/minimum_sale_price/objects/<model("minimum_sale_price.minimum_sale_price"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('minimum_sale_price.object', {
#             'object': obj
#         })

