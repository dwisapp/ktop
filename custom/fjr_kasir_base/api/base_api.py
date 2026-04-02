from odoo.http import request, JsonRPCDispatcher, Request
from odoo import http, _
import json
from math import ceil
from odoo.exceptions import AccessDenied, UserError
import traceback
from odoo.tools import (ustr,)
import logging
_logger = logging.getLogger(__name__)

def _response(self, result=None, error=None):
        response = {'jsonrpc': '2.0', 'id': self.request_id}
        url_path = self.request.httprequest.path.lower()
        if error is not None:
            response['status'] = 'error'
            if 'api' in url_path:
                # error.pop('debug', None)
                _logger.error("API Error: %s", error['data']['debug'])
                del error['data']['debug']
            response['error'] = error
        if result is not None:
            response['status'] = 'success'
            response['result'] = result
            

        return self.request.make_json_response(response)

def get_json_data(self):
        if self.httprequest.get_data(as_text=True):
            return json.loads(self.httprequest.get_data(as_text=True))
        else:
            return {}

JsonRPCDispatcher._response = _response
Request.get_json_data = get_json_data

# def serialize_exception(exception):
#     name = type(exception).__name__
#     module = type(exception).__module__
#     _logger.error(traceback.format_exc())

#     return {
#         'name': f'{module}.{name}' if module else name,
#         'message': ustr(exception),
#         'debug': traceback.format_exc(),
#         'arguments': exception.args,
#         'context': getattr(exception, 'context', {}),
#     }

# http.serialize_exception = serialize_exception

class BaseAPI(http.Controller):
     
    @http.route("/api/country", type="json", auth="jwt", methods=["GET"])
    def get_country(self):
        kwargs = request.httprequest.args
        domain = []
        if kwargs.get("code"):
            domain.append(("code", "ilike", kwargs.get("code")))
        if kwargs.get("name"):
            domain.append(("name", "ilike", kwargs.get("name")))
        
        order_by = kwargs.get("order", "name")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit
        countries = request.env["res.country"].sudo().search(domain, order=order_by, limit=limit, offset=offset)

        country_list = []
        total_count = countries.search_count(domain)
        for country in countries:
            country_list.append({
                "name": country.name,
                "code": country.code
            })
        return {
            "countries": country_list,
            "total": total_count,
            "page" : page,
            "total_page" : ceil(total_count / limit),
            "limit" : limit,
        }

    

    @http.route("/api/province", type="json", auth="jwt", methods=["GET"])
    def get_province(self):
        

        kwargs = request.httprequest.args

        country_code = kwargs.get("country_code")
        if not country_code:
            raise UserError(_("Country code is required"))
        domain = [("country_id.code", "=", country_code)]
        if kwargs.get("code"):
            domain.append(("code", "ilike", kwargs.get("code")))
        if kwargs.get("name"):
            domain.append(("name", "ilike", kwargs.get("name")))
        order_by = kwargs.get("order", "name")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit
        state_ids = request.env["res.country.state"].sudo().search(domain, order=order_by, limit=limit, offset=offset)
        total_count = state_ids.search_count(domain)


        province_list = []
        for state in state_ids:
            province_list.append({
                "name": state.name,
                "code": state.code
            })
        return {
            "provinces": province_list,
            "total": total_count,
            "page" : page,
            "total_page" : ceil(total_count / limit),
            "limit" : limit,
        }
        


