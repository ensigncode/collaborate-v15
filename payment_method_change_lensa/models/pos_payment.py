from odoo import fields, models
from odoo.exceptions import UserError


class PosPayment(models.Model):
    _inherit = "pos.payment"

    def change_payment_method(self):
        payment_ids = self.filtered(lambda id:id.session_id.state in ['opening_control','opened'])
        if payment_ids:
            return {
                'name': 'Change Payment Method',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'change.payment.method.wizard',
                'target': 'new',
                'context':{
                    'default_pos_payment_ids':[(6, 0, payment_ids.ids)]
                }
            }
        else:
            raise UserError("There is no open session.")