# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Print to ECR from POS",
    "version": "15.0.2.0.10",
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "support": "odoo@terrabit.ro",
    "summary": "Generare fisier pentru casa de marcat",
    "license": "LGPL-3",
    "price": 150.00,
    "currency": "EUR",
    "category": "Point Of Sale",
    "depends": ["point_of_sale", "deltatech_download", "deltatech_pos_base"],
    "data": [
        # "views/assets.xml",
        # 'views/account_journal_view.xml',
        # "views/pos_payment_method_view.xml",
        "views/pos_config_view.xml",
        "views/pos_order_view.xml",
        "views/point_of_sale_dashboard.xml",
        "views/pos_session_view.xml",
        "wizard/pos_box_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "qweb": ["static/src/xml/pos.xml"],
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "assets": {
        "point_of_sale.assets": [
            "deltatech_pos/static/src/css/pos.css",
            "deltatech_pos/static/src/js/db.js",
            "deltatech_pos/static/src/js/ecr_file.js",
            "deltatech_pos/static/src/js/PaymentScreen.js",
            # "deltatech_pos/static/src/js/ReceiptScreen.js",
            "deltatech_pos/static/src/js/ProductScreen.js",
            "deltatech_pos/static/src/js/CashBoxOpening.js",
            "deltatech_pos/static/src/js/CashMovePopup.js",
            "deltatech_pos/static/src/js/ClosePosPopup.js",
        ],
        "web.assets_qweb": [
            "deltatech_pos/static/src/xml/**/*",
        ],
    },
    "extra_buy": True,
}
