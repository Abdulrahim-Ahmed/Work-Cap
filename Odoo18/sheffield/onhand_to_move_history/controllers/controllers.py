# -*- coding: utf-8 -*-
# from odoo import http


# class OnhandToMoveHistory(http.Controller):
#     @http.route('/onhand_to_move_history/onhand_to_move_history', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/onhand_to_move_history/onhand_to_move_history/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('onhand_to_move_history.listing', {
#             'root': '/onhand_to_move_history/onhand_to_move_history',
#             'objects': http.request.env['onhand_to_move_history.onhand_to_move_history'].search([]),
#         })

#     @http.route('/onhand_to_move_history/onhand_to_move_history/objects/<model("onhand_to_move_history.onhand_to_move_history"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('onhand_to_move_history.object', {
#             'object': obj
#         })

