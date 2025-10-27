# -*- coding: utf-8 -*-
# from odoo import http


# class RealizedGainsLoss(http.Controller):
#     @http.route('/realized_gains_loss/realized_gains_loss', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/realized_gains_loss/realized_gains_loss/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('realized_gains_loss.listing', {
#             'root': '/realized_gains_loss/realized_gains_loss',
#             'objects': http.request.env['realized_gains_loss.realized_gains_loss'].search([]),
#         })

#     @http.route('/realized_gains_loss/realized_gains_loss/objects/<model("realized_gains_loss.realized_gains_loss"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('realized_gains_loss.object', {
#             'object': obj
#         })

