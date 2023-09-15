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
