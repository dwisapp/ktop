# -*- coding: utf-8 -*-
from odoo import http

# class Pph21Payroll(http.Controller):
#     @http.route('/pph_21_payroll/pph_21_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pph_21_payroll/pph_21_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pph_21_payroll.listing', {
#             'root': '/pph_21_payroll/pph_21_payroll',
#             'objects': http.request.env['pph_21_payroll.pph_21_payroll'].search([]),
#         })

#     @http.route('/pph_21_payroll/pph_21_payroll/objects/<model("pph_21_payroll.pph_21_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pph_21_payroll.object', {
#             'object': obj
#         })