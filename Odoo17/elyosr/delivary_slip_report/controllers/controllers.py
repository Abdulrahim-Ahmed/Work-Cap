# -*- coding: utf-8 -*-
# from odoo import http


# class DelivarySlipReport(http.Controller):
#     @http.route('/delivary_slip_report/delivary_slip_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/delivary_slip_report/delivary_slip_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('delivary_slip_report.listing', {
#             'root': '/delivary_slip_report/delivary_slip_report',
#             'objects': http.request.env['delivary_slip_report.delivary_slip_report'].search([]),
#         })

#     @http.route('/delivary_slip_report/delivary_slip_report/objects/<model("delivary_slip_report.delivary_slip_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('delivary_slip_report.object', {
#             'object': obj
#         })

