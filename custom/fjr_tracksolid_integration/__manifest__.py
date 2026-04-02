{
    'name': 'Tracksolid Pro Integration',
    'version': '17.0.1.0.0',
    'summary': 'Integration with Tracksolid Pro API for Fleet Tracking',
    'description': """
        This module integrates Odoo with Tracksolid Pro API.
        Features:
        - Sync Fleet/Vehicles from Tracksolid
        - Real-time location tracking (scheduled)
        - Helper for API signature and authentication
    """,
    'category': 'Operations/Fleet',
    'author': 'Goway',
    'depends': ['base', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/fleet_vehicle_views.xml',
        'data/ir_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
             'fjr_tracksolid_integration/static/src/xml/live_tracking.xml',
             'fjr_tracksolid_integration/static/src/js/live_tracking.js',
             'fjr_tracksolid_integration/static/src/xml/history_map.xml',
             'fjr_tracksolid_integration/static/src/js/history_map.js',
             'fjr_tracksolid_integration/static/src/xml/live_mileage.xml',
             'fjr_tracksolid_integration/static/src/js/live_mileage.js',
             'fjr_tracksolid_integration/static/src/xml/fleet_map.xml',
             'fjr_tracksolid_integration/static/src/js/fleet_map.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
