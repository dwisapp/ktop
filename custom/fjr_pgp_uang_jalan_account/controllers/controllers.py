# -*- coding: utf-8 -*-
# from odoo import http


# class FjrPgpUangJalanAccount(http.Controller):
#     @http.route('/fjr_pgp_uang_jalan_account/fjr_pgp_uang_jalan_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fjr_pgp_uang_jalan_account/fjr_pgp_uang_jalan_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fjr_pgp_uang_jalan_account.listing', {
#             'root': '/fjr_pgp_uang_jalan_account/fjr_pgp_uang_jalan_account',
#             'objects': http.request.env['fjr_pgp_uang_jalan_account.fjr_pgp_uang_jalan_account'].search([]),
#         })

#     @http.route('/fjr_pgp_uang_jalan_account/fjr_pgp_uang_jalan_account/objects/<model("fjr_pgp_uang_jalan_account.fjr_pgp_uang_jalan_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fjr_pgp_uang_jalan_account.object', {
#             'object': obj
#         })

