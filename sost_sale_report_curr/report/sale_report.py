# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    invoice_no = fields.Char(string="Invoice No", readonly=True)
    untaxed_amount_usd = fields.Float(string="Untaxed Amount USD", readonly=True)
    untaxed_amount_eur = fields.Float(string="Untaxed Amount EUR", readonly=True)

    def _group_by_sale(self, groupby=''):
        res = super()._group_by_sale(groupby)
        res += """,s.invoice_no"""
        return res

    def _select_additional_fields(self, fields):
        fields['invoice_no'] = ", s.invoice_no as invoice_no"
        fields['untaxed_amount_usd'] = ", s.untaxed_amount_usd as untaxed_amount_usd"
        fields['untaxed_amount_eur'] = ", s.untaxed_amount_eur as untaxed_amount_eur"
        return super()._select_additional_fields(fields)
