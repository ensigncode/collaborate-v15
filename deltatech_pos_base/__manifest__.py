# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Deltatech POS Base",
    "summary": "POS Base for print to ECR",
    "version": "15.0.1.0.0",
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "category": "Sales/Point of Sale",
    "depends": [
        "point_of_sale",
        # "nexterp_base_module",
    ],
    "price": 10.00,
    "currency": "EUR",
    "data": [
        "views/pos_config_view.xml",
        "views/pos_payment_method_view.xml",
    ],
    "license": "LGPL-3",
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "maintainers": ["dhongu"],
}
