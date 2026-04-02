# -*- coding: utf-8 -*-
# from odoo import http


# class FjrPgpInventory(http.Controller):
#     @http.route('/fjr_pgp_inventory/fjr_pgp_inventory', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fjr_pgp_inventory/fjr_pgp_inventory/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fjr_pgp_inventory.listing', {
#             'root': '/fjr_pgp_inventory/fjr_pgp_inventory',
#             'objects': http.request.env['fjr_pgp_inventory.fjr_pgp_inventory'].search([]),
#         })

#     @http.route('/fjr_pgp_inventory/fjr_pgp_inventory/objects/<model("fjr_pgp_inventory.fjr_pgp_inventory"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fjr_pgp_inventory.object', {
#             'object': obj
#         })

