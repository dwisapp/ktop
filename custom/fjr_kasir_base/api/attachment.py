
from odoo.http import request
from odoo import http, _
import json
import uuid
from datetime import datetime, timedelta
from odoo.exceptions import AccessDenied, UserError
from odoo.tools.image import image_data_uri
import base64
from werkzeug.exceptions import Forbidden, NotFound
import pdb
from ast import literal_eval
from math import ceil

class Attachment(http.Controller):

    @http.route("/attachment/<string:access_token>", type="http", auth="none", methods=["GET"])
    def get_attachment(self, access_token):
        attachment = request.env['ir.attachment'].sudo().search(
            [('access_token', '=', access_token)])
    

        if not attachment:
            raise Forbidden()

        file_content = base64.b64decode(attachment.datas)
        mime_type = attachment.mimetype or attachment.guess_type(
            attachment.name)[0] or 'application/octet-stream'

        response_headers = [('Content-Type', mime_type),
                            ('Content-Disposition',
                            f'inline; filename="{attachment.name}"'),
                            ('Content-Length', len(file_content))]

        return request.make_response(file_content, headers=response_headers)