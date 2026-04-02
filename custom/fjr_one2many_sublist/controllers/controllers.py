# -*- coding: utf-8 -*-
# from odoo import http


# class FjrOne2manySublist(http.Controller):
#     @http.route('/fjr_one2many_sublist/fjr_one2many_sublist', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fjr_one2many_sublist/fjr_one2many_sublist/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fjr_one2many_sublist.listing', {
#             'root': '/fjr_one2many_sublist/fjr_one2many_sublist',
#             'objects': http.request.env['fjr_one2many_sublist.fjr_one2many_sublist'].search([]),
#         })

#     @http.route('/fjr_one2many_sublist/fjr_one2many_sublist/objects/<model("fjr_one2many_sublist.fjr_one2many_sublist"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fjr_one2many_sublist.object', {
#             'object': obj
#         })

