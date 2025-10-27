# -*- coding: utf-8 -*-
# from odoo import http


# class PosPhoneNum(http.Controller):
#     @http.route('/pos_phone_num/pos_phone_num', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_phone_num/pos_phone_num/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_phone_num.listing', {
#             'root': '/pos_phone_num/pos_phone_num',
#             'objects': http.request.env['pos_phone_num.pos_phone_num'].search([]),
#         })

#     @http.route('/pos_phone_num/pos_phone_num/objects/<model("pos_phone_num.pos_phone_num"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_phone_num.object', {
#             'object': obj
#         })

