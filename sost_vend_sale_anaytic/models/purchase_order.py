# -*- coding: utf-8 -*-

from odoo import _, api,fields, models

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	generate_analytic = fields.Boolean(string="Generate Analytic",copy=False)
	analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account",copy=False)

	def create_analytic_account_vals(self):
		if self.partner_ref and self.partner_id:
			name = self.partner_ref + ' - ' + self.partner_id.display_name
		else:
			name = self.partner_id.display_name
		vals = {
			'name':name,
			'partner_id':self.partner_id.id,
		}
		return vals

	def create_analytic_account(self):
		vals = self.create_analytic_account_vals()
		analytic_account_id = self.env['account.analytic.account'].create(vals)
		return analytic_account_id

	def write(self,vals):
		res = super(PurchaseOrder,self).write(vals)
		if ('partner_id' in vals and vals['partner_id']) or ('partner_ref' in vals):
			for order in self:
				if order.analytic_account_id:
					order.analytic_account_id.update(self.create_analytic_account_vals())
		if 'generate_analytic' in vals and vals['generate_analytic']:
			for order in self:
				analytic_account_id = order.create_analytic_account()
				order.analytic_account_id = analytic_account_id.id
		return res


	@api.model_create_multi
	def create(self,vals):
		results = super(PurchaseOrder,self).create(vals)
		for res in results:
			if not res.analytic_account_id and res.generate_analytic:
				analytic_account_id = res.create_analytic_account()
				res.analytic_account_id = analytic_account_id.id
		return results



	def button_confirm(self):
		res = super(PurchaseOrder,self).button_confirm()
		if not self.analytic_account_id and self.generate_analytic:
			analytic_account_id = self.create_analytic_account()
			self.analytic_account_id = analytic_account_id.id
		return res


class PurchaseOrderLine(models.Model):
	_inherit = "purchase.order.line"


	def _prepare_account_move_line(self, move=False):
		res = super()._prepare_account_move_line(move)
		if self.order_id.analytic_account_id:
			res['analytic_account_id'] = self.order_id.analytic_account_id.id
		# res.update({'is_landed_costs_line': self.product_id.landed_cost_ok})
		return res


	# def _prepare_account_move_line(self, move):
	# 	self.ensure_one()
	# 	values = super(PurchaseOrderLine,self)._prepare_account_move_line(move)
	# 	if self.order_id.analytic_account_id:
	# 		values['analytic_account_id'] = self.order_id.analytic_account_id.id
	# 		print('\n\n=========values======',values)
	# 	return values