# -*- coding: utf-8 -*-
{
    'name': "Auto Invoicing and Shipping",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "SOSTENIA S.R.L., Razvan Bornac",
    'website': "http://www.sostenia.ro",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'qweb': [],
    "assets": {
        "point_of_sale.assets": [
            "sostenia_auto_invoicing_shipping/static/src/js/models.js"
        ],
        "web.assets_qweb": [
            "sostenia_auto_invoicing_shipping/static/src/xml/**/*",
        ],
    },
}
