# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountInvoicesAction(models.Model):
    _inherit = 'ir.actions.report'


    invoice_name = fields.Char('Invoice Name')

    def name_get(self):
        res = []
        for record in self:
            if self.env.ref('account.account_invoices') and self.env.ref('account.account_invoices').id == record.id:
                 res.append((record.id, record.invoice_name))
            else:
                res.append((record.id, record.name))
        return res
