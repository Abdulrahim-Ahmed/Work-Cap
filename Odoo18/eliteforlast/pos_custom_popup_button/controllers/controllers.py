# -*- coding: utf-8 -*-
# from odoo import http


# class PosCustomPopupButton(http.Controller):
#     @http.route('/pos_custom_popup_button/pos_custom_popup_button', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_custom_popup_button/pos_custom_popup_button/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_custom_popup_button.listing', {
#             'root': '/pos_custom_popup_button/pos_custom_popup_button',
#             'objects': http.request.env['pos_custom_popup_button.pos_custom_popup_button'].search([]),
#         })

#     @http.route('/pos_custom_popup_button/pos_custom_popup_button/objects/<model("pos_custom_popup_button.pos_custom_popup_button"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_custom_popup_button.object', {
#             'object': obj
#         })

