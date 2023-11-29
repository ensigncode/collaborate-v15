# -*- coding: utf-8 -*-

from odoo import _, api,fields, models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockPicking(models.Model):
	_inherit = "stock.picking"

	raw_production_id = fields.Many2one('mrp.production',string="MRP")

	def move_update_qty(self):
		picking = self
		picking.do_unreserve()
		if picking.state:
			for move in picking.move_ids_without_package.filtered(lambda x:x.reserved_availability > 0):
				if not move.move_line_ids:
					move.state = 'waiting'
					move_line = self.env['stock.move.line'].create(dict(move._prepare_move_line_vals(), qty_done=move.reserved_availability))
					move.write({'move_line_ids': [(4, move_line.id)]})
				move._action_assign()
		return True

class StockMoveLine(models.Model):
	_inherit = "stock.move.line"

	production_product_uom_qty = fields.Float(string="Production UOM QTY")

class StockMove(models.Model):
	_inherit = "stock.move"

	production_product_uom_qty = fields.Float(string="Production UOM QTY")

	def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
		res = super(StockMove,self)._prepare_move_line_vals(quantity,reserved_quant)
		quantity = self._compute_reserved_availability()
		quantity = self.reserved_availability
		if quantity:
			rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
			uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
			uom_quantity = float_round(uom_quantity, precision_digits=rounding)
			uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
			if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
				res['product_uom_qty'] = uom_quantity
			else:
				res['product_uom_qty'] = quantity
		return res

	@api.depends('move_line_ids.product_qty')
	def _compute_reserved_availability(self):
		""" Fill the `availability` field on a stock move, which is the actual reserved quantity
		and is represented by the aggregated `product_qty` on the linked move lines. If the move
		is force assigned, the value will be 0.
		"""
		if not any(self._ids):
			for move in self:
				reserved_availability = sum(move.move_line_ids.mapped('product_qty'))
				move.reserved_availability = move.product_id.uom_id._compute_quantity(
					reserved_availability, move.product_uom, rounding_method='HALF-UP')
		else:
			# compute
			reserved_availability = 0
			result = {data['move_id'][0]: data['product_qty'] for data in
					  self.env['stock.move.line'].read_group([('move_id', 'in', self.ids)], ['move_id', 'product_qty'], ['move_id'])}
			for move in self:
				reserved_availability = move.product_id.uom_id._compute_quantity(
					result.get(move.id, 0.0), move.product_uom, rounding_method='HALF-UP')
				if move.picking_id.raw_production_id:
					raw_production_id = move.picking_id.raw_production_id
					final_product_qty = 0
					if raw_production_id.state == 'done':
						product_qty = raw_production_id.product_qty 
					else:
						product_qty = raw_production_id.qty_producing
					if product_qty > 0:
						product_uom_qty = (move.product_uom_qty * raw_production_id.qty_producing) / raw_production_id.product_qty 
						final_product_qty = move.product_uom._compute_quantity(
							product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
					
					if final_product_qty > 0:
						move.reserved_availability = final_product_qty
					else:
						move.reserved_availability = reserved_availability
				else:
					move.reserved_availability = reserved_availability

	def get_is_production(self):
		ctx = self._context
		is_production = False
		if 'params' in ctx and ctx['params'] and 'model' in ctx['params'] and ctx['params']['model'] == 'mrp.production':
			is_production = True 
		return is_production

	is_production = fields.Boolean(string="Is Production",default=lambda x:x.get_is_production())
	consider_qty = fields.Float(string="Consider Qty")

	@api.depends('product_id', 'product_uom', 'product_uom_qty','is_production','raw_material_production_id.qty_producing','raw_material_production_id.product_qty')
	def _compute_product_qty(self):
		for move in self:
			move.product_qty  = 1
			if move.is_production and move.raw_material_production_id:
				final_product_qty = 0
				if move.raw_material_production_id.state == 'done':
					product_qty = move.raw_material_production_id.product_qty 
				else:
					product_qty = move.raw_material_production_id.qty_producing
				if product_qty > 0:
					product_uom_qty = (move.product_uom_qty * move.raw_material_production_id.qty_producing) / move.raw_material_production_id.product_qty 
					final_product_qty = move.product_uom._compute_quantity(
						product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
				move.product_qty = final_product_qty
			else:
				move.product_qty = move.product_uom._compute_quantity(
					move.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')

class MRPProduction(models.Model):
	_inherit = "mrp.production"

	production_picking_ids = fields.One2many('stock.picking','raw_production_id')

	def action_confirm(self):
		res = super(MRPProduction,self).action_confirm()
		if self.picking_ids:
			for picking in self.picking_ids:
				picking.raw_production_id = self.id
		return res


	def write(self,vals):
		res = super(MRPProduction,self).write(vals)
		if 'qty_producing' in vals:
			for production in self:
				done_picking_id =  production.production_picking_ids.filtered(lambda x:x.state == 'done')
				picking_ids = production.production_picking_ids.filtered(lambda x:x.state != 'done')
				if done_picking_id:
					picking_ids = picking_ids.filtered(lambda x:x.id > done_picking_id.id)
				if picking_ids:
					for picking in picking_ids:
						picking.move_update_qty()
		return res
