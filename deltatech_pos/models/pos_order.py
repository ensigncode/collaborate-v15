# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    file = fields.Text()
    receipt_print = fields.Boolean()

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        if "file" in ui_order:
            order_fields["file"] = ui_order["file"]
            if ui_order["file"]:
                order_fields["receipt_print"] = True
        return order_fields
