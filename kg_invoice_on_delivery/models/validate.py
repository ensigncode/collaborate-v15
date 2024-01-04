# -*- coding: utf-8 -*-

# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/



from odoo import models, fields, api,_
from odoo.exceptions import UserError

class InvoicePaymentWizard(models.TransientModel):
	_inherit = 'sale.advance.payment.inv'
	_description = 'Invoice payment on delivery'

	# create invoice on delivery
	def create_invoice_on_delivery(self):
		picking_id = self.env['stock.picking'].browse(self._context.get('active_ids', []))
		sale_orders = self.env['sale.order'].search([('name','=',picking_id.origin)])
		if self.advance_payment_method == 'delivered':
			sale_orders._create_invoices(final=self.deduct_down_payments)
		else:
			# Create deposit product if necessary
			if not self.product_id:
				vals = self._prepare_deposit_product()
				self.product_id = self.env['product.product'].create(vals)
				self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

			sale_line_obj = self.env['sale.order.line']
			for order in sale_orders:
				amount, name = self._get_advance_details(order)

				if self.product_id.invoice_policy != 'order':
					raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
				if self.product_id.type != 'service':
					raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
				taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
				tax_ids = order.fiscal_position_id.map_tax(taxes).ids
				analytic_tag_ids = []
				for line in order.order_line:
					analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

				so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
				so_line = sale_line_obj.create(so_line_values)
				self._create_invoice(order, so_line, amount)
		picking_id.invoice_status=0
		if self._context.get('open_invoices', False):
			return sale_orders.action_view_invoice()
		return {'type': 'ir.actions.act_window_close'}


class StockPickingInh(models.Model):
	_inherit = "stock.picking"

	invoice_status = fields.Integer(default=0)

	def button_validate(self):
		self.invoice_status = 1
		return super(StockPickingInh, self).button_validate()
