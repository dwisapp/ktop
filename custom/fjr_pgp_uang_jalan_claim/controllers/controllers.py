# -*- coding: utf-8 -*-
# from odoo import http


# class FjrPgpUangJalanClaim(http.Controller):
#     @http.route('/fjr_pgp_uang_jalan_claim/fjr_pgp_uang_jalan_claim', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fjr_pgp_uang_jalan_claim/fjr_pgp_uang_jalan_claim/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fjr_pgp_uang_jalan_claim.listing', {
#             'root': '/fjr_pgp_uang_jalan_claim/fjr_pgp_uang_jalan_claim',
#             'objects': http.request.env['fjr_pgp_uang_jalan_claim.fjr_pgp_uang_jalan_claim'].search([]),
#         })

#     @http.route('/fjr_pgp_uang_jalan_claim/fjr_pgp_uang_jalan_claim/objects/<model("fjr_pgp_uang_jalan_claim.fjr_pgp_uang_jalan_claim"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fjr_pgp_uang_jalan_claim.object', {
#             'object': obj
#         })

