# -*- coding: utf-8 -*-
# from odoo import http


# class LocationRestrictionTemp(http.Controller):
#     @http.route('/location_restriction_temp/location_restriction_temp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/location_restriction_temp/location_restriction_temp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('location_restriction_temp.listing', {
#             'root': '/location_restriction_temp/location_restriction_temp',
#             'objects': http.request.env['location_restriction_temp.location_restriction_temp'].search([]),
#         })

#     @http.route('/location_restriction_temp/location_restriction_temp/objects/<model("location_restriction_temp.location_restriction_temp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('location_restriction_temp.object', {
#             'object': obj
#         })

