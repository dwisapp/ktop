from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    tracksolid_imei = fields.Char(string="IMEI", help="IMEI number from Tracksolid")
    tracksolid_device_name = fields.Char(string="Device Name (Tracksolid)")
    last_gps_latitude = fields.Float(string="Last Latitude", digits=(10, 7))
    last_gps_longitude = fields.Float(string="Last Longitude", digits=(10, 7))
    last_gps_speed = fields.Float(string="Speed (km/h)")
    last_gps_timestamp = fields.Datetime(string="Last GPS Update")
    gps_device_status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('inactive', 'Inactive'),
        ('unknown', 'Unknown')
    ], string="Device Status", default='unknown', help="Status from Tracksolid")
    
    def action_sync_from_tracksolid(self):
        """ Pulls data for this specific vehicle if IMEI is set """
        self.ensure_one()
        if not self.tracksolid_imei:
            return
            
        connector = self.env['tracksolid.connector']
        # Use location get for single device
        # Endpoint: jimi.device.location.get
        params = {'imeis': self.tracksolid_imei}
        result = connector._make_request('jimi.device.location.get', params)
        

        if result and isinstance(result, list) and len(result) > 0:
            data = result[0] 
            self._update_gps_data(data)


    def _update_gps_data(self, data):
        """ Update fields from API data """
        # Data format depends on API response, assuming keys based on standard
        # lat, lng, speed, gpsTime/deviceTime
        
        # Handle NoneType safely
        lat = data.get('lat')
        lng = data.get('lng')
        speed = data.get('speed')
        
        self.last_gps_latitude = float(lat) if lat is not None else 0.0
        self.last_gps_longitude = float(lng) if lng is not None else 0.0
        self.last_gps_speed = float(speed) if speed is not None else 0.0
        # Handling Status Mapping (1 = Online, others = Offline/Inactive assumed)
        # Based on user screenshot: '1' appears to be Online/Moving, '0' or others might be Offline.
        raw_status = str(data.get('status') or data.get('vehicleStatus') or '')
        
        status_map = {
            '1': 'online',
            'online': 'online',
            'Moving': 'online',
            'Static': 'online',
            '0': 'offline',
            'offline': 'offline'
        }
        self.gps_device_status = status_map.get(raw_status, 'unknown')
        
        # deviceTime is often string, need conversion
        # content often: "2023-01-01 12:00:00"
        time_str = data.get('gpsTime') or data.get('deviceTime')
        if time_str:
            self.last_gps_timestamp = fields.Datetime.to_datetime(time_str)

    @api.model
    def cron_sync_all_vehicles(self):
        """ Scheduled action to sync all vehicles """
        connector = self.env['tracksolid.connector']
        
        # Determining Target User ID
        # Priority: Specific Target Setting > Main Login User ID
        config = self.env['ir.config_parameter'].sudo()
        target_user = config.get_param('tracksolid.target_user_id')
        if not target_user:
            target_user = config.get_param('tracksolid.user_id')

        params = {
            'target': target_user,
        } 
        
        # If the API requires paging, we'd handle it. 
        # For now, let's try obtaining mapping.
        
        # However, the user said "Mapping fleet/vehicle from dashboard". 
        # This implies: Fetch ALL from API -> Connect to existing Odoo vehicle by IMEI or Create New.
        
        # Let's assume we map by IMEI.
        results = connector._make_request('jimi.user.device.location.list', params)
        
        if results:
            for item in results:
                imei = item.get('imei')
                if not imei:
                    continue
                    
                vehicle = self.search([('tracksolid_imei', '=', imei)], limit=1)
                
                # If not found, check if we can match by License Plate (often 'deviceName' in tracksolid is license plate)
                if not vehicle:
                    device_name = item.get('deviceName')
                    if device_name:
                        vehicle = self.search([('license_plate', '=', device_name)], limit=1)
                        if vehicle:
                            vehicle.tracksolid_imei = imei # Link them
                

                # If still not found, create new?
                if not vehicle:
                    # Find a default brand/model
                    model = self.env['fleet.vehicle.model'].search([], limit=1)
                    if not model:
                        # Should rarely happen if fleet is installed
                        _logger.warning("No Fleet Model found, skipping creation for IMEI %s", imei)
                        continue
                        
                    vehicle = self.create({
                        'model_id': model.id,
                        'license_plate': item.get('deviceName', imei),
                        'tracksolid_imei': imei,
                        'tracksolid_device_name': item.get('deviceName')
                    })

                
                # Update status
                vehicle._update_gps_data(item)
