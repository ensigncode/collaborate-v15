# -*- coding: utf-8 -*-
{
    'name': "Sales Reporting Lensa",
    'description': """
        Add margin and total payment in sales report pivot view.
    """,
    'category': 'Sales/Sales',
    'version': '15.0.1.0.1',

    'depends': ['sale','sale_margin'],

    'data': [

        # Views
        'views/sales_reporting_pivot_view.xml',
    ],
    'installable': True,
    'auto_install': True
}
