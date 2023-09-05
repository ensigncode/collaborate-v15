# -*- coding: utf-8 -*-
{
    'name': "Payment Method Change Lensa",
    'description': """
        Payment Method Change
    """,
    'category': 'Point Of Sale',
    'version': '15.0.1.0.0',

    'depends': ['point_of_sale'],

    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/ir_action_server.xml',

        # Wizards
        'wizards/change_payment_method_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': True
}
