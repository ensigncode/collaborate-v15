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
    payment_methods = fields.Char(string="Payment Methods", compute='_compute_payment_methods')

    def _compute_payment_methods(self):
        for move in self:
            move.payment_methods = ','.join(list(set(move.invoice_line_ids.mapped(
                'sale_line_ids.order_id.pos_order_line_ids.order_id.payment_ids.payment_method_id.name'))))
            if not move.payment_methods:
                move.payment_methods = 'Bank Transfer'
