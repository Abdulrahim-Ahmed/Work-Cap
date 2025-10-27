# -*- coding: utf-8 -*-
# from odoo import http


# class SalesOrderImg(http.Controller):
#     @http.route('/sales_order_img/sales_order_img', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_order_img/sales_order_img/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_order_img.listing', {
#             'root': '/sales_order_img/sales_order_img',
#             'objects': http.request.env['sales_order_img.sales_order_img'].search([]),
#         })

#     @http.route('/sales_order_img/sales_order_img/objects/<model("sales_order_img.sales_order_img"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_order_img.object', {
#             'object': obj
#         })

