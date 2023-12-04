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
		print('\n\n========PICKING___-',self)
		# for move in self.move_ids_without_package:
		# 	print('\n=-----------move--',move)
		return res
