# -*- coding: utf-8 -*-
# from odoo import http


# class AnalyticTransfers(http.Controller):
#     @http.route('/analytic_transfers/analytic_transfers', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/analytic_transfers/analytic_transfers/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('analytic_transfers.listing', {
#             'root': '/analytic_transfers/analytic_transfers',
#             'objects': http.request.env['analytic_transfers.analytic_transfers'].search([]),
#         })

#     @http.route('/analytic_transfers/analytic_transfers/objects/<model("analytic_transfers.analytic_transfers"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('analytic_transfers.object', {
#             'object': obj
#         })
