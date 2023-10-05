# -*- coding: utf-8 -*-

from odoo import fields, models, api


class CustomResCompany(models.Model):
	_inherit = "res.company"

	@api.model
	def _get_default_report_id(self):
		return self.env.ref('account.account_invoices', False)

	report_template_id = fields.Many2one('ir.actions.report',
	                                     string="Report", domain="[('model','=','account.move')]",
	                                     default=_get_default_report_id)

	def read(self, fields=None, load='_classic_read'):
		for rec in self:
			report_name = self.env.ref('account.account_invoices')
			if report_name in rec.report_template_id:
				name = report_name.invoice_name and report_name.invoice_name.split('-', 1) or [report_name.name, '']
				rec.report_template_id.update({'invoice_name': name[0] + '-' + rec.country_id.code, 'name': 'Invoices'})
		return super(CustomResCompany, self).read(fields=fields, load=load)
