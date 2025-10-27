# -*- coding: utf-8 -*-
# from odoo import http


# class CustomSalesApproval(http.Controller):
#     @http.route('/custom_sales_approval/custom_sales_approval', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_sales_approval/custom_sales_approval/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_sales_approval.listing', {
#             'root': '/custom_sales_approval/custom_sales_approval',
#             'objects': http.request.env['custom_sales_approval.custom_sales_approval'].search([]),
#         })

#     @http.route('/custom_sales_approval/custom_sales_approval/objects/<model("custom_sales_approval.custom_sales_approval"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_sales_approval.object', {
#             'object': obj
#         })
