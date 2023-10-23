# -*- coding: utf-8 -*-
{
    "name": "Product Storage Capacity",
    "category": "product",
    "summary": "Product Storage Capacity",
    "description": '''
                Product Storage Capacity
            ''',
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
            'stock',
            'sale_stock',
            'sale_management',
            ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/update_putaway_rule_views.xml',
        
        'views/product_views.xml',
        'views/stock_storage_category_views.xml',
    ],
    "author": "Ensigncode Software",
    "installable": True,
}