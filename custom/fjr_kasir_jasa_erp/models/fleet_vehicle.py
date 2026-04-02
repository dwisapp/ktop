from odoo import models, fields, api, _
import requests
import json
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    @api.model
    def get_fleet_vehicle_from_jasa_erp(self):
        fleet_vehicles = self.search([])
        fleet_makes = self.env['fleet.vehicle.model.brand'].search([])
        fleet_model = self.env['fleet.vehicle.model'].search([])
        fleet_make_dict = {
            fleet_make.name: fleet_make for fleet_make in fleet_makes
        }
        fleet_model_dict = {
            fleet_model.name: fleet_model for fleet_model in fleet_model
        }
        fleet_dict = {
            fleet.license_plate: fleet for fleet in fleet_vehicles
        }
        url = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_url')
        filters = ""
        last_get_data = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.last_get_data')
        if last_get_data:
            filters = f'&filters=[["Vehicle","modified", ">", "{last_get_data}"]]'
        fleet_url = f'{url}/api/resource/Vehicle?fields=["plate_number", "make", "model"]{filters}&limit_page_length=50000'
        cookies = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_cookies')
        headers = {
            'Cookie': cookies
        }
        response = requests.get(fleet_url, headers=headers)
        if response.status_code == 200:
            response_text = json.loads(response.text)
            datas = response_text.get('data', [])
            for data in datas:
                if data.get('plate_number') not in fleet_dict:
                    make = False
                    model = False
                    if data.get('make') and data.get('make') not in fleet_make_dict:
                        make = self.env['fleet.vehicle.model.brand'].create({
                            'name': data.get('make')
                        })
                        fleet_make_dict[make.name] = make
                    elif data.get('make') in fleet_make_dict:
                        make = fleet_make_dict[data.get('make')]
                    if data.get('model') and data.get('model') not in fleet_model_dict:
                        model = self.env['fleet.vehicle.model'].create({
                            'name': data.get('model'),
                            'brand_id': make.id if make else False
                        })
                        fleet_model_dict[model.name] = model
                    elif data.get('model') in fleet_model_dict:
                        model = fleet_model_dict[data.get('model')]


                    fleet = self.create({
                        'license_plate': data.get('plate_number'),
                        'model_id': model.id if model else False,
                    })
                    fleet_dict[fleet.license_plate] = fleet
                else:
                    fleet_dict[data.get('plate_number')].write({
                        'license_plate': data.get('plate_number'),
                    })
            _logger.info("Get %s Vehicle from Jasa ERP Success " % (len(datas)))
            self.env['jasa.erp.delivery.note'].get_delivery_note_from_jasa_erp()
            self.env['ir.config_parameter'].sudo().set_param('fjr_kasir_jasa_erp.last_get_data', fields.Datetime.now())
            
        else:
            response_text = json.loads(response.text)
            message = response_text.get('_server_messages', '')
            _logger.error("Failed to get data from Jasa ERP, %s" % (message))
            # raise UserError(_("Failed to get data from Jasa ERP, %s" % (message)))