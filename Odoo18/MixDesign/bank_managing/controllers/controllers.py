# -*- coding: utf-8 -*-
# from odoo import http


# class BankManaging(http.Controller):
#     @http.route('/bank_managing/bank_managing', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bank_managing/bank_managing/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('bank_managing.listing', {
#             'root': '/bank_managing/bank_managing',
#             'objects': http.request.env['bank_managing.bank_managing'].search([]),
#         })

#     @http.route('/bank_managing/bank_managing/objects/<model("bank_managing.bank_managing"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bank_managing.object', {
#             'object': obj
#         })

