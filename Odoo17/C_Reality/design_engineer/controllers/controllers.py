# -*- coding: utf-8 -*-
# from odoo import http


# class DesignEngineer(http.Controller):
#     @http.route('/design_engineer/design_engineer', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/design_engineer/design_engineer/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('design_engineer.listing', {
#             'root': '/design_engineer/design_engineer',
#             'objects': http.request.env['design_engineer.design_engineer'].search([]),
#         })

#     @http.route('/design_engineer/design_engineer/objects/<model("design_engineer.design_engineer"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('design_engineer.object', {
#             'object': obj
#         })
