# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseDelivery(http.Controller):
#     @http.route('/purchase_delivery/purchase_delivery', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_delivery/purchase_delivery/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_delivery.listing', {
#             'root': '/purchase_delivery/purchase_delivery',
#             'objects': http.request.env['purchase_delivery.purchase_delivery'].search([]),
#         })

#     @http.route('/purchase_delivery/purchase_delivery/objects/<model("purchase_delivery.purchase_delivery"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_delivery.object', {
#             'object': obj
#         })

