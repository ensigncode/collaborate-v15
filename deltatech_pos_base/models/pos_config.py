# ©  2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    cod_ecr = fields.Char(string="Cod ECR", default="0", size=1)


class PosConfig(models.Model):
    _inherit = "pos.config"

    ecr_type = fields.Selection(
        [
            ("datecs18", "FiscalWire"),
            ("optima", "Optima"),
            ("daisy", "Daisy"),
            ("succes", "Succes"),
            ("fiscalnet", "FiscalNet"),
            ("incotex", "Incotex"),
        ],
        default="datecs18",
    )
    ecr_trim = fields.Boolean("Trim long product name")
    ecr_trim_to = fields.Integer(default=30)

    file_prefix = fields.Char(string="File prefix", default="order")
    file_ext = fields.Char(string="File extension", default="inp")
