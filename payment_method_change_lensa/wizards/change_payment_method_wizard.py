from odoo import fields, models

class ChangePaymentMethodWizard(models.TransientModel):
    _name = "change.payment.method.wizard"
    _description = "Change Payment wizard"

    payment_method_id = fields.Many2one("pos.payment.method",string="Payment Method")
    pos_payment_ids = fields.Many2many("pos.payment", "pos_payment_ids",string="Payments")
    
    def change_payment_method(self):
        for payment in self.pos_payment_ids:
            payment.payment_method_id = self.payment_method_id.id