# -*- coding: utf-8 -*-
{
    'name': "Sales Reporting Lensa",
    'description': """
        Add margin and total payment in sales report pivot view.
    """,
    'category': 'Sales/Sales',
    'version': '15.0.1.0.4',

    'depends': ['product', 'sale','sale_margin', 'point_of_sale', 'product_margin'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/sales_reporting_pivot_view.xml',
    ],
    'installable': True,
    'auto_install': True
}
