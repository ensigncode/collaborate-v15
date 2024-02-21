# -*- coding: utf-8 -*-

from translate import Translator
from odoo import models

class GiftCard(models.Model):
    _inherit = "gift.card"

    def get_gift_card_lang(self):
        gift_card_details = self.buy_pos_order_line_id.order_id.config_id.gift_card_details
        if gift_card_details:
            if self.partner_id and self.partner_id.lang and self.company_id.partner_id.lang:
                to_lang_id = self.env['res.lang'].search(
                    [('code', '=', self.company_id.partner_id.lang)])
                from_lang_id = self.env['res.lang'].search(
                    [('code', '=', self.partner_id.lang)])
                if to_lang_id.id != from_lang_id.id:
                    translator = Translator(
                        from_lang=to_lang_id.iso_code, to_lang=from_lang_id.iso_code)
                    translation = translator.translate(
                        self.buy_pos_order_line_id.order_id.config_id.gift_card_details)
                    return translation
                else:
                    return gift_card_details
            else:
                return gift_card_details
        else:
            return ''
