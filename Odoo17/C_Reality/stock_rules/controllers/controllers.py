# -*- coding: utf-8 -*-
# from odoo import http


# class StockRules(http.Controller):
#     @http.route('/stock_rules/stock_rules', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_rules/stock_rules/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_rules.listing', {
#             'root': '/stock_rules/stock_rules',
#             'objects': http.request.env['stock_rules.stock_rules'].search([]),
#         })

#     @http.route('/stock_rules/stock_rules/objects/<model("stock_rules.stock_rules"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_rules.object', {
#             'object': obj
#         })
