# -*- coding: utf-8 -*-
# from odoo import http


# class VolumeByLiter(http.Controller):
#     @http.route('/volume_by_liter/volume_by_liter', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/volume_by_liter/volume_by_liter/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('volume_by_liter.listing', {
#             'root': '/volume_by_liter/volume_by_liter',
#             'objects': http.request.env['volume_by_liter.volume_by_liter'].search([]),
#         })

#     @http.route('/volume_by_liter/volume_by_liter/objects/<model("volume_by_liter.volume_by_liter"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('volume_by_liter.object', {
#             'object': obj
#         })

