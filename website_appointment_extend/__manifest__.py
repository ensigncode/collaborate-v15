# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Website Appointments Extension',
    'version': '15.0.1.0.13',
    'category': 'Marketing/Online Appointment',
    'sequence': 216,
    'description': """
        Employee wise appointment
        
    """,
    'depends': ['website_appointment', 'appointment'],
    'data': [
        'security/ir.model.access.csv',
        'data/appointment_reason_data.xml',
        'views/appointment_type_views.xml',
        'views/calendar_templates.xml',
        'views/appointment_reason_views.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_frontend': [
            'website_appointment_extend/static/src/js/appointment_select_slot.js',
            'website_appointment_extend/static/src/xml/appointment_slot.xml',
        ],
        'web.assets_qweb': [
            'website_appointment_extend/static/src/xml/**/*',
        ],
    },
}
