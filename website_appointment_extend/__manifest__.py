# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Website Appointments Extension',
    'version': '15.0.1.0.9',
    'category': 'Marketing/Online Appointment',
    'sequence': 216,
    'description': """
        Employee wise appointment
        
    """,
    'depends': ['website_appointment', 'appointment'],
    'data': [
        'views/appointment_type_views.xml',
        'views/calendar_templates.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}
