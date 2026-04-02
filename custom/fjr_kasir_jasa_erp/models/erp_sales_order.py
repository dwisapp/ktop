from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class JasaErpSalesOrder(models.Model):
    _name = 'jasa.erp.sales.order'

    name = fields.Char(string='No. Dokumen', required=True)
    customer_name = fields.Char(string='Nama Customer')
    status = fields.Char(string='Status')
    delivery_note_ids = fields.Many2many('jasa.erp.delivery.note', "jasa_erp_sales_order_delivery_note_rel", "sales_order_id", "delivery_note_id", string='Delivery Notes')

    
    @api.model
    def get_sales_order_delivery_note(self):
        
        url = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_url')
        filters = ""
        last_get_data = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.last_get_data')
        if last_get_data:
            filters = f'&filters=[["Sales Order","modified", ">", "{last_get_data}"]]'
        sales_url = f'{url}/api/resource/Sales Order?fields=["name", "customer_name", "status"]{filters}&limit_page_length=50000'
        cookies = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_cookies')
        headers = {
            'Cookie': cookies
        }
        response = requests.get(sales_url, headers=headers)
        _logger.info("Get Sales Order from Jasa ERP %s" % (response.text))
        if response.status_code == 200:
            
            response_text = json.loads(response.text)
            datas = response_text.get('data', [])
            if datas:
                sales_orders = self.search([('name', 'in', [data.get('name') for data in datas])])
                sales_dict = {
                    sales_order.name: sales_order for sales_order in sales_orders
                }
                for data in datas:
                    if data.get('name') not in sales_dict:
                        sale = self.create({
                            'name': data.get('name'),
                            'customer_name': data.get('customer_name'),
                            'status': data.get('status')
                        })
                        sales_dict[sale.name] = sale
                    else:
                        sales_dict[data.get('name')].write({
                            'customer_name': data.get('customer_name'),
                            'status': data.get('status')
                        })
                _logger.info("Get %s Sales Order from Jasa ERP Success " % (len(datas)))
            
            
        else:
            response_text = json.loads(response.text)
            message = response_text.get('_server_messages', '')
            _logger.error("Failed to get data from Jasa ERP, %s" % (message))
            # raise UserError(_("Failed to get data from Jasa ERP, %s" % (message)))
        
        self.env['jasa.erp.delivery.note'].get_delivery_note_from_jasa_erp()
        self.env['fleet.vehicle'].get_fleet_vehicle_from_jasa_erp()
        self.env['ir.config_parameter'].sudo().set_param('fjr_kasir_jasa_erp.last_get_data', fields.Datetime.now())


    @api.model
    def auth_jasa_erp(self):
        url = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_url')
        username = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_email')
        password = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_password')
       
        response = requests.post(f"{url}/api/method/login?usr={username}&pwd={password}")
        if response.status_code == 200:
            self.env['ir.config_parameter'].set_param('fjr_kasir_jasa_erp.last_auth_date', fields.Datetime.now())
            cookies = response.cookies.get_dict()
            cookies_res = ""
            for key, value in cookies.items():
                cookies_res += f"{key}={value};"

            self.env['ir.config_parameter'].set_param('fjr_kasir_jasa_erp.jasa_erp_cookies', cookies_res)

            _logger.info("Successfully authenticated with Jasa ERP")
        else:
            response_text = json.loads(response.text)
            message = response_text.get('_server_messages', '')
            _logger.error("Failed to auth to Jasa ERP, %s" % (message))
            raise UserError(_("Failed to auth to Jasa ERP, %s" % (message)))

class JasaErpDeliveryNote(models.Model):
    _name = 'jasa.erp.delivery.note'

    name = fields.Char(string='No. Dokumen', required=True)
    sales_order_ids = fields.Many2many('jasa.erp.sales.order', "jasa_erp_sales_order_delivery_note_rel", "delivery_note_id", "sales_order_id", string='Sales Orders')
    customer_name = fields.Char(string='Nama Customer')
    driver_id = fields.Many2one('res.partner', string='Driver')
    fleet_id = fields.Many2one('fleet.vehicle', string='Fleet')
    jenis_barang = fields.Char(string='Jenis Barang')
    tujuan_bongkar = fields.Char(string='Tujuan Bongkar')
    tempat_muat = fields.Char(string='Tempat Muat')
    item_ids = fields.One2many('jasa.erp.delivery.items', 'delivery_note_id', string='Items')

    @api.model
    def get_delivery_note_from_jasa_erp(self):
        """"""
        # drivers = self.env['res.partner'].search([('is_driver', '=', True)])
        # driver_dict = {
        #     driver.nik: driver for driver in drivers
        # }
        
        # url = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_url')
        # filters = ""
        # last_get_data = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.last_get_data')
        # if last_get_data:
        #     filters = f'&filters=[["Delivery Note","modified", ">", "{last_get_data}"]]'
        # delivery_url = f'{url}/api/resource/Delivery Note?fields=["name", "customer_name", "driver", "driver_name", "jenis_barang", "tujuan_bongkar", "tempat_muat", "vehicle"]{filters}&limit_page_length=50000'
        # cookies = self.env['ir.config_parameter'].sudo().get_param('fjr_kasir_jasa_erp.jasa_erp_cookies')
        # headers = {
        #     'Cookie': cookies
        # }
        # response = requests.get(delivery_url, headers=headers)
        # if response.status_code == 200:
        #     response_text = json.loads(response.text)
        #     datas = response_text.get('data', [])
        #     if datas:
                
        #         delivery_notes = self.search([('name', 'in', [data.get('name') for data in datas])])
        #         fleet_vehicle = self.env['fleet.vehicle'].search([])
        #         fleet_dict = {
        #             fleet.license_plate: fleet for fleet in fleet_vehicle
        #         }
        #         delivery_dict = {
        #             delivery_note.name: delivery_note for delivery_note in delivery_notes
        #         }
        #         for data in datas:
        #             driver = False
        #             fleet_id = False
        #             if data.get('driver') and data.get('driver') not in driver_dict:
        #                 driver = self.env['res.partner'].create({
        #                     'name': data.get('driver_name'),
        #                     'nik': data.get('driver'),
        #                     'is_driver': True
        #                 })
        #                 driver_dict[driver.nik] = driver
        #             elif data.get('driver') in driver_dict:
        #                 driver = driver_dict[data.get('driver')]
                    
        #             if data.get('vehicle') in fleet_dict:
        #                 fleet_id = fleet_dict[data.get('vehicle')].id

        #             if data.get('name') not in delivery_dict:
        #                 delivery_note = self.create({
        #                     'name': data.get('name'),
        #                     'customer_name': data.get('customer_name'),
        #                     'jenis_barang': data.get('jenis_barang'),
        #                     'tujuan_bongkar': data.get('tujuan_bongkar'),
        #                     'tempat_muat': data.get('tempat_muat'),
        #                     'driver_id': driver.id if driver else False,
        #                     'fleet_id': fleet_id
        #                 })
        #                 delivery_dict[delivery_note.name] = delivery_note
        #             else:
        #                 delivery_dict[data.get('name')].write({
        #                     'customer_name': data.get('customer_name'),
        #                     'jenis_barang': data.get('jenis_barang'),
        #                     'tujuan_bongkar': data.get('tujuan_bongkar'),
        #                     'tempat_muat': data.get('tempat_muat'),
        #                     'driver_id': driver.id if driver else False,
        #                     'fleet_id': fleet_id
        #                 })
        #         _logger.info("Get %s Delivery Note from Jasa ERP Success " % (len(datas)))
        # else:
        #     response_text = json.loads(response.text)
        #     message = response_text.get('_server_messages', '')
        #     _logger.error("Failed to get data from Jasa ERP, %s" % (message))
        #     # raise UserError(_("Failed to get data from Jasa ERP, %s" % (message)))


class JasaErpDeliveryItems(models.Model):
    _name = 'jasa.erp.delivery.items'

    delivery_note_id = fields.Many2one('jasa.erp.delivery.note', string='Delivery Note')
    item_code = fields.Char(string='Item Code')
    item_name = fields.Char(string='Item Name')
    qty = fields.Float(string='Qty')
    uom = fields.Char(string='UOM')
    rate = fields.Float(string='Rate')

