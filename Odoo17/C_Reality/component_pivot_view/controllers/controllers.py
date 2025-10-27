# -*- coding: utf-8 -*-
# from odoo import http


# class ComponentPivotView(http.Controller):
#     @http.route('/component_pivot_view/component_pivot_view', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/component_pivot_view/component_pivot_view/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('component_pivot_view.listing', {
#             'root': '/component_pivot_view/component_pivot_view',
#             'objects': http.request.env['component_pivot_view.component_pivot_view'].search([]),
#         })

#     @http.route('/component_pivot_view/component_pivot_view/objects/<model("component_pivot_view.component_pivot_view"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('component_pivot_view.object', {
#             'object': obj
#         })
