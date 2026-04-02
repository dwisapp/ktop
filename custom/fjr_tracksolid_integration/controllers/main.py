from odoo import http
from odoo.http import request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class TracksolidController(http.Controller):
    @http.route('/tracksolid/get_device_location', type='json', auth='user')
    def get_device_location(self, vehicle_id):
        vehicle = request.env['fleet.vehicle'].browse(vehicle_id)
        if not vehicle.exists() or not vehicle.tracksolid_imei:
            return {'error': 'Vehicle or IMEI not found'}
        
        connector = request.env['tracksolid.connector']
        params = {'imeis': vehicle.tracksolid_imei}
        
        # We fetch fresh data from API
        result = connector._make_request('jimi.device.location.get', params)
        
        if result and isinstance(result, list) and len(result) > 0:
            data = result[0]
            # Return necessary data for map
            return {
                'lat': data.get('lat'),
                'lng': data.get('lng'),
                'speed': data.get('speed'),
                'course': data.get('course'),
                'deviceName': data.get('deviceName'),
                'deviceTime': data.get('deviceTime') or data.get('gpsTime')
            }
        return {'error': 'No data returned from Tracksolid API'}

    @http.route('/tracksolid/get_tracking_history', type='json', auth='user')
    def get_tracking_history(self, vehicle_id, start_time, end_time):
        """ Fetch history points for playback """
        vehicle = request.env['fleet.vehicle'].browse(vehicle_id)
        if not vehicle.exists() or not vehicle.tracksolid_imei:
            return {'error': 'Vehicle or IMEI not found'}
            
        connector = request.env['tracksolid.connector']
        params = {
            'imeis': vehicle.tracksolid_imei,
            'startTime': start_time,
            'endTime': end_time
        }
        
        # Endpoint for history
        # Based on doc assumption: jimi.device.track.list
        _logger.info(f"TRACKSOLID HISTORY REQ: IMEI={vehicle.tracksolid_imei}, Start={start_time}, End={end_time}")
        try:
            result = connector._make_request('jimi.device.track.list', params)
            _logger.info(f"TRACKSOLID HISTORY RES: {str(result)[:500]}") # Log first 500 chars
        except Exception as e:
            _logger.error(f"TRACKSOLID HISTORY ERROR: {e}")
            return {'error': str(e)}
        
        if result and isinstance(result, list):
            # Map data to simpler format
            # API usually returns: [{lat, lng, speed, gpsTime, ...}, ...]
            points = []
            for p in result:
                points.append({
                    'lat': p.get('lat'),
                    'lng': p.get('lng'),
                    'speed': p.get('speed'),
                    'time': p.get('gpsTime') or p.get('deviceTime')
                })
            return {'points': points}
            
        return {'points': []}

    @http.route('/tracksolid/get_live_mileage', type='json', auth='user')
    def get_live_mileage(self, vehicle_id):
        """ Fetch today's mileage directly from API """
        vehicle = request.env['fleet.vehicle'].browse(vehicle_id)
        if not vehicle.exists() or not vehicle.tracksolid_imei:
            return {'error': 'No IMEI'}
            
        connector = request.env['tracksolid.connector']
        
        # Endpoint: jimi.device.track.mileage
        # Params usually: imeis, startTime, endTime
        # We'll fetch Today's mileage
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
        end_of_day = now.strftime("%Y-%m-%d %H:%M:%S")
        
        params = {
            'imeis': vehicle.tracksolid_imei,
            'startTime': start_of_day,
            'endTime': end_of_day
        }
        
        result = connector._make_request('jimi.device.track.mileage', params)
        if result and isinstance(result, list) and len(result) > 0:
            # Result usually: [{'imei': '...', 'mileage': '12345 (meter)', ...}]
            data = result[0]
            mileage_meters = float(data.get('mileage', 0))
            mileage_km = round(mileage_meters / 1000, 2)
            return {'mileage_km': mileage_km}
            
        return {'mileage_km': 0}

    @http.route('/tracksolid/get_fleet_map_data', type='json', auth='user')
    def get_fleet_map_data(self):
        """ Fetch all vehicles with valid GPS data from DB """
        domain = [('tracksolid_imei', '!=', False)]
        vehicles = request.env['fleet.vehicle'].search(domain)
        
        data = []
        for v in vehicles:
            # Skip if no coordinates (0,0)
            if v.last_gps_latitude == 0.0 and v.last_gps_longitude == 0.0:
                continue

            data.append({
                'id': v.id,
                'name': v.license_plate or v.name,
                'model': v.model_id.name if v.model_id else '',
                'lat': v.last_gps_latitude,
                'lng': v.last_gps_longitude,
                'speed': v.last_gps_speed,
                'status': v.gps_device_status,
                'time': v.last_gps_timestamp, # DateTime will be serialized by Odoo JSON
                'driver': v.driver_id.name if v.driver_id else 'No Driver'
            })
        return {'vehicles': data}

