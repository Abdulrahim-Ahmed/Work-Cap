# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryReservation(http.Controller):
#     @http.route('/inventory_reservation/inventory_reservation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_reservation/inventory_reservation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_reservation.listing', {
#             'root': '/inventory_reservation/inventory_reservation',
#             'objects': http.request.env['inventory_reservation.inventory_reservation'].search([]),
#         })

#     @http.route('/inventory_reservation/inventory_reservation/objects/<model("inventory_reservation.inventory_reservation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_reservation.object', {
#             'object': obj
#         })

