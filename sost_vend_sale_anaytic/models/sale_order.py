# -*- coding: utf-8 -*-

from odoo import _, api,fields, models

class SaleOrder(models.Model):
	_inherit = "sale.order"

	generate_analytic = fields.Boolean(string="Generate Analytic",copy=False)
	analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account",copy=False)
	

	def create_analytic_account_vals(self):
		vals = {
			'name':self.partner_id.display_name,
			'partner_id':self.partner_id.id,
		}
		return vals

	def create_analytic_account(self):
		vals = self.create_analytic_account_vals()
		analytic_account_id = self.env['account.analytic.account'].create(vals)
		return analytic_account_id

	@api.model_create_multi
	def create(self,vals):
		results = super(SaleOrder,self).create(vals)
		for res in results:
			if not res.analytic_account_id and res.generate_analytic:
				analytic_account_id = res.create_analytic_account()
				res.analytic_account_id = analytic_account_id.id
		return results

	def write(self,vals):
		res = super(SaleOrder,self).write(vals)
		if 'partner_id' in vals and vals['partner_id']:
			for order in self:
				if order.analytic_account_id:
					order.analytic_account_id.update(self.create_analytic_account_vals())
		if 'generate_analytic' in vals and vals['generate_analytic']:
			for order in self:
				analytic_account_id = order.create_analytic_account()
				order.analytic_account_id = analytic_account_id.id
		return res

	def action_confirm(self):
		res = super(SaleOrder,self).action_confirm()
		if not self.analytic_account_id and self.generate_analytic:
			analytic_account_id = self.create_analytic_account()
			self.analytic_account_id = analytic_account_id.id
		return res


class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	def _prepare_invoice_line(self, **optional_values):
		values = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
		if self.order_id.analytic_account_id:
			values['analytic_account_id'] = self.order_id.analytic_account_id.id
		return values