from odoo import http
from odoo.http import request
import logging
import json
_logger = logging.getLogger(__name__)
from ast import literal_eval
from odoo.exceptions import AccessError, MissingError

class FjrKasirBase(http.Controller):

    @http.route('/midtrans/payout/status', type='json', auth='public', csrf=False)
    def midtrans_payout_status(self, **post):
        data = json.loads(request.httprequest.data)
        _logger.info('Midtrans Payout Status: %s' % data)
        reference_no = data.get('reference_no')
        status = data.get('status')
        midtrans_transaction = request.env['midtrans.payout.log'].sudo().search([('reference_no', '=', reference_no)])
        if midtrans_transaction:
            res_ids = literal_eval(midtrans_transaction.res_id)

            record = request.env[midtrans_transaction.model_name].sudo().browse(res_ids)
            record.write({'midtrans_status': status})
           
        return {'status': 'ok'}
    


    @http.route('/xendit/payout/status', type='json', auth='public', csrf=False)
    def xendit_payout_status(self, **post):
        request_data = json.loads(request.httprequest.data)
        headers = request.httprequest.headers
        webhook_token = headers.get('X-CALLBACK-TOKEN')
        configured_token = request.env['ir.config_parameter'].sudo().get_param('xendit.payout.webhook.token')
        if webhook_token != configured_token:
            raise AccessError("Invalid webhook token.")
    
        _logger.info('Xendit Payout Status: %s' % request_data)

        data = request_data.get('data', {})
        if not data:
            return {'status': 'no data'}
        reference_no = data.get('id')
        status = data.get('status')
        xendit_transaction = request.env['xendit.payout.log'].sudo().search([('reference_no', '=', reference_no)])
        if xendit_transaction:
            res_ids = literal_eval(xendit_transaction.res_id)

            record = request.env[xendit_transaction.model_name].sudo().browse(res_ids)
            record.write({'xendit_status': status})
           
        return {'status': 'ok'}
        
