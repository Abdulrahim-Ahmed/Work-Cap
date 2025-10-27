# -*- coding: utf-8 -*-
# from odoo import http


# class LocationCost(http.Controller):
#     @http.route('/location_cost/location_cost', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/location_cost/location_cost/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('location_cost.listing', {
#             'root': '/location_cost/location_cost',
#             'objects': http.request.env['location_cost.location_cost'].search([]),
#         })

#     @http.route('/location_cost/location_cost/objects/<model("location_cost.location_cost"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('location_cost.object', {
#             'object': obj
#         })
