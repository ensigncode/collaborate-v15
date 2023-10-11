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
            sale_line_pos_order_ids = move.invoice_line_ids.mapped('sale_line_ids.order_id.pos_order_line_ids.order_id')
            pos_order_ids = move.pos_order_ids
            if pos_order_ids:
                move.payment_methods = ','.join(list(set(pos_order_ids.mapped('payment_ids.payment_method_id.name'))))
            elif sale_line_pos_order_ids:
                move.payment_methods = ','.join(list(set(sale_line_pos_order_ids.mapped(
                    'payment_ids.payment_method_id.name'))))
            else:
                move.payment_methods = 'Bank Transfer'
