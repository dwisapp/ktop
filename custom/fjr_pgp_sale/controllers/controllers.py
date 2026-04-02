# -*- coding: utf-8 -*-
# from odoo import http


# class FjrPgpSale(http.Controller):
#     @http.route('/fjr_pgp_sale/fjr_pgp_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fjr_pgp_sale/fjr_pgp_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fjr_pgp_sale.listing', {
#             'root': '/fjr_pgp_sale/fjr_pgp_sale',
#             'objects': http.request.env['fjr_pgp_sale.fjr_pgp_sale'].search([]),
#         })

#     @http.route('/fjr_pgp_sale/fjr_pgp_sale/objects/<model("fjr_pgp_sale.fjr_pgp_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fjr_pgp_sale.object', {
#             'object': obj
#         })

