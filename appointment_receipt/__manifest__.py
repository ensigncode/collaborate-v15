# -*- coding: utf-8 -*-

{
    'name': 'Appointment Receipt',
    'version': '15.0.1.0.10',
    'category': 'Marketing/Online Appointment',
    'sequence': 216,
    'description': """
        Appointment Receipt
    """,
    'depends': ['appointment', 'calendar', 'web', 'website_appointment_extend'],
    'data': [
        'data/sequences.xml',
        'views/meeting_views.xml',
        'views/portal_view.xml',
        'reports/prescription_report.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}
