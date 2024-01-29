# -*- coding: utf-8 -*-

{
    'name': 'Merge Sale Order Backorders and Create New Sale Order',
    'category': 'Sales',
    'summary': 'Merge Sale Order Backorders and Create New Sale Order',
    'version': '15.0.1.0.1',
    'website': 'http://www.unicoding.net',
    'author': 'Unicoding',
    'description': 'Merge Sale Order Backorders and Create New Sale Order',
    'license': "AGPL-3",


    'depends': [
        'sale_management',
        'stock',
        'sale_stock'
    ],

    'data': [
        'wizard/merge_sale_order_backorder_wizard_view.xml',
        "security/ir.model.access.csv",
    ],

    'images': [
        #'static/description/banner.jpg',
    ],

    'installable': True,

}
