# -*- coding: utf-8 -*-
# from odoo import http


# class FjrKasirJasaErp(http.Controller):
#     @http.route('/fjr_kasir_jasa_erp/fjr_kasir_jasa_erp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fjr_kasir_jasa_erp/fjr_kasir_jasa_erp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fjr_kasir_jasa_erp.listing', {
#             'root': '/fjr_kasir_jasa_erp/fjr_kasir_jasa_erp',
#             'objects': http.request.env['fjr_kasir_jasa_erp.fjr_kasir_jasa_erp'].search([]),
#         })

#     @http.route('/fjr_kasir_jasa_erp/fjr_kasir_jasa_erp/objects/<model("fjr_kasir_jasa_erp.fjr_kasir_jasa_erp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fjr_kasir_jasa_erp.object', {
#             'object': obj
#         })
