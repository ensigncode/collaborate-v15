# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # mutat in pos.payment.method

    cod_ecr = fields.Char(string="Cod ECR", default="0", size=1)
