# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Amount - Curreny Wise',
    'version': '15.0.0.3',
    'category': 'sale',
    'summary': 'Sale Amount - Curreny Wise',
    'description': 'Sale Amount - Curreny Wise',
    'depends': [
                'sale',
                'sale_management',
                'sale_enterprise',
        ],
    'data': [
        'data/ir_cron.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
    'assets': {},
    'license': 'LGPL-3',
}
