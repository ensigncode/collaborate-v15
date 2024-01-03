# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	def get_notes(self):
		notes = """ - Our purchase conditions are applicable for this purchase order.<br/>
					- Always print our purchase order number and our reference number on your packing list(s) and invoice(s).<br/>
					- Confimation within 48H by return e-mail please: purchasingprimebatteries.com <br/>
					- Invoicing at e-mal address: invoiceprimebatteries.com """
		return notes

	notes = fields.Html('Terms and Conditions',default=lambda self:self.get_notes())

	tax_use = fields.Boolean(string="Tax User",compute="_compute_tax_use")
	approved_by_id = fields.Many2one('res.users',string="Approved By")

	@api.depends('order_line.taxes_id')
	def _compute_tax_use(self):
		tax_use = False
		for order in self:
			have_taxes = order.order_line.filtered(lambda x:x.taxes_id)
			if have_taxes:
				tax_use = True 
			order.tax_use = tax_use

	def merge_purchase_order_lines(self):
		merged_lines = {}
		product_qty = 0.0
		for line in self.order_line:
			key = (line.product_id.id,line.price_unit)
			if key not in merged_lines:
				merged_lines[key] = {'order_line':line,'quantity':0.0,'notes': [],'subtotal':0.0}
			merged_lines[key]['quantity'] += line.product_uom_qty
			merged_lines[key]['subtotal'] += line.price_subtotal
			if line.notes:
				merged_lines[key]['notes'].append(line.notes)
		return merged_lines

	def button_approve(self,force=False):
		res = super(PurchaseOrder,self).button_approve(force=force)
		self.approved_by_id = self.env.user
		return res

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	notes = fields.Text(string="Notes")


class ResPartner(models.Model):
	_inherit = "res.partner"

	nrc = fields.Char(string="NRC")