# -*- coding: utf-8 -*-

from odoo import _, api,fields, models

class StockPicking(models.Model):
	_inherit = "stock.picking"

	analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account",copy=False)
	account_analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account",copy=False)

class StockMove(models.Model):
	_inherit = "stock.move"	

	account_analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account",copy=False)

	def _action_assign(self, force_qty=False):
		res = super(StockMove, self)._action_assign()
		for move in self:
			if move.move_line_ids and move.product_id.tracking == 'lot' and move.purchase_line_id:
				for move_line in move.move_line_ids[0]:
					if not move_line.lot_name:
						
						partner_ref = ''
						if move.purchase_line_id.order_id.product_id.default_code:
							product_name = move.purchase_line_id.order_id.product_id.default_code
						else:
							product_name = move.purchase_line_id.order_id.product_id.name
						lot_serial = self.env['ir.sequence'].next_by_code('stock.lot.serial')

						if move.purchase_line_id.order_id.partner_ref:
							partner_ref = move.purchase_line_id.order_id.partner_ref
							lot_name = partner_ref + ' - ' + product_name + ' - ' + lot_serial
						else:
							lot_name = product_name + ' - ' + lot_serial

						move_line.lot_name = lot_name
						move_line.qty_done = move.product_uom_qty
		return res
