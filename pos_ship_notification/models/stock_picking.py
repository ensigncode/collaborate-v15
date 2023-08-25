
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class StockPickingCustom(models.Model):
    _inherit = "stock.picking"

    def _compute_state(self):
        res = super(StockPickingCustom, self)._compute_state()
        template_id = self.env.ref('pos_ship_notification.mail_template_picking_notification_tmpl')
        subject = _('Product picking notification')
        address = self.partner_id.address_get(['delivery']) 
        pickings = self.env['stock.picking'].search([('state', '=', 'done')])
        products = pickings.mapped('move_ids_without_package.product_id')
        print("\n\n products ::; ",products,products.ids)
        print("\n\n compute state ----- ",self,self.state)
        if self.state == 'done' and self.pos_order_id :
            email_values = {'email_to': self.partner_id.email or '', 'subject': subject}
            template_id.send_mail(self.id, email_values=email_values)
        return res
