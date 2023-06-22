# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    # iface_tally_sheet = fields.Boolean() # Borderou

    quantity = fields.Float(compute="_compute_quantity")

    iface_cash_in_out = fields.Boolean(string="Cash In/Out")
    ecr_cash_in_out = fields.Boolean(string="Cash In/Out to ECR", default=True)
    text_cash_in = fields.Char(string="Text for Cash In", default="Cash collection")
    text_cash_out = fields.Char(string="Text for Cash Out", default="Payment disposal")

    transfer_account_id = fields.Many2one("account.account", string="Transfer account")

    # campul asta exista in 12.0
    stock_location_id = fields.Many2one("stock.location")
    print_duplicate_in_out = fields.Boolean(string="Print duplicate payment disposal")
    print_order_barcode = fields.Boolean(string="Print order number as barcode")

    def _compute_quantity(self):
        for config in self:
            qty = 0.0
            stock_location_id = config.stock_location_id
            quants = self.env["stock.quant"].search([("location_id", "=", stock_location_id.id)])
            for quant in quants:
                qty += quant.quantity
            config.quantity = qty

    def open_stock(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("product.product_template_action")
        action["context"] = {"location": self.stock_location_id.id, "search_default_real_stock_available": 1}
        return action

    @api.onchange("iface_cash_in_out")
    def onchange_iface_cash_in_out(self):
        if self.iface_cash_in_out:
            self.cash_control = True
