# -*- coding: utf-8 -*-
# from odoo import http


# class ActionConfirm(http.Controller):
#     @http.route('/action_confirm/action_confirm', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/action_confirm/action_confirm/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('action_confirm.listing', {
#             'root': '/action_confirm/action_confirm',
#             'objects': http.request.env['action_confirm.action_confirm'].search([]),
#         })

#     @http.route('/action_confirm/action_confirm/objects/<model("action_confirm.action_confirm"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('action_confirm.object', {
#             'object': obj
#         })

