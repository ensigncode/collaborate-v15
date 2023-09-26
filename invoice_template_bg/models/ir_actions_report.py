# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountInvoicesAction(models.Model):
    _inherit = 'ir.actions.report'

    def name_get(self):
        """
        Update template name based on the selected company
        """
        res = []
        for record in self:
            if self.env.ref('account.account_invoices') and self.env.ref('account.account_invoices').id == record.id:
                if self.env.company and self.env.company.country_id:
                    res.append((record.id, f'Invoices - {self.env.company.country_id.code}'))
            else:
                res.append((record.id, record.name))

        return res
