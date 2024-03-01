# -*- coding: utf-8 -*-

from functools import partial
from odoo import models, fields


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    margin_per = fields.Float(string='Margin %')
    total_payment = fields.Float(string='Total Payment')

    def _select(self):
        return super(PosOrderReport, self)._select() + ', (SUM(l.price_subtotal - COALESCE(l.total_cost,0) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) / SUM(COALESCE(NULLIF(l.price_subtotal, 0), 1)))*100 AS margin_per' + ', (SELECT sum(amount) FROM account_payment AS ap WHERE move_id IN (SELECT id FROM account_move am WHERE ref=am.name)) AS total_payment' 

