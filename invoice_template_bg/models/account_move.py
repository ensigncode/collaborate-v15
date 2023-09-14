# -*- coding: utf-8 -*-

from odoo import fields, models, api


class InvoiceOrder(models.Model):
    _inherit = 'account.move'

    def _compute_number_to_words(self):
        """Compute the amount to words in Invoice"""
        for rec in self:
            rec.number_to_words = rec.currency_id.amount_to_text(
                rec.amount_total)

    number_to_words = fields.Char(string="Amount in Words (Total) : ",
                                  compute='_compute_number_to_words')







