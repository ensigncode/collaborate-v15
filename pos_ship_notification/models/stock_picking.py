
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPickingCustom(models.Model):
    _inherit = "stock.picking"

    def _compute_state(self):
        res = super(StockPickingCustom, self)._compute_state()
        for pick in self:
            template_id = self.env.ref('pos_ship_notification.mail_template_picking_notification_tmpl')
            subject = _('Product picking notification')
            if pick.pos_order_id.config_id.ship_later:
                shop_address = pick.pos_order_id.config_id.warehouse_id.partner_id._display_address(without_company=True)
                if pick.state == 'assigned' and pick.pos_order_id:
                    email_values = {'email_to': pick.partner_id.email or '', 'subject': subject}
                    template_id.with_context(shop_address=shop_address).send_mail(pick.id, email_values=email_values)
        return res
