# -*- coding: utf-8 -*-

from odoo import models,fields,_,api

class StockPicking(models.Model):
	_inherit = "stock.picking"

	raw_production_id = fields.Many2one('mrp.production',string="MRP")

	def move_update_qty(self):
		if self.raw_production_id:
			for move in self.move_ids_without_package:
				move._compute_reserved_availability()
				move_line_ids = move.move_line_ids
				if move_line_ids:
					move_line_ids[0].product_uom_qty = move.reserved_availability
		return True


class StockMoveLine(models.Model):
	_inherit = "stock.move.line"

	production_product_uom_qty = fields.Float(string="Production UOM QTY")

class StockMove(models.Model):
	_inherit = "stock.move"

	production_product_uom_qty = fields.Float(string="Production UOM QTY")


	@api.depends('move_line_ids.product_qty')
	def _compute_reserved_availability(self):
		""" Fill the `availability` field on a stock move, which is the actual reserved quantity
		and is represented by the aggregated `product_qty` on the linked move lines. If the move
		is force assigned, the value will be 0.
		"""
		if not any(self._ids):
			# onchange
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
				
				print('\n\n==reserved_availability==========',reserved_availability)
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
					print('\n\n-------final_product_qty------',final_product_qty)
					move.reserved_availability = final_product_qty
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

	# def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
	# 	print('\n\n\n==============_get_move_raw_values=======',product_uom_qty)
	# 	source_location = self.location_src_id
	# 	origin = self.name
	# 	if self.orderpoint_id and self.origin:
	# 		origin = self.origin.replace(
	# 			'%s - ' % (self.orderpoint_id.display_name), '')
	# 		origin = '%s,%s' % (origin, self.name)
	# 	data = {
	# 		'sequence': bom_line.sequence if bom_line else 10,
	# 		'name': self.name,
	# 		'date': self.date_planned_start,
	# 		'date_deadline': self.date_planned_start,
	# 		'bom_line_id': bom_line.id if bom_line else False,
	# 		'picking_type_id': self.picking_type_id.id,
	# 		'product_id': product_id.id,
	# 		'production_product_uom_qty':product_uom_qty,
	# 		# 'product_uom_qty': product_uom_qty,
	# 		'product_uom_qty':0,
	# 		'product_uom': product_uom.id,
	# 		'location_id': source_location.id,
	# 		'location_dest_id': self.product_id.with_company(self.company_id).property_stock_production.id,
	# 		'raw_material_production_id': self.id,
	# 		'company_id': self.company_id.id,
	# 		'operation_id': operation_id,
	# 		'price_unit': product_id.standard_price,
	# 		'procure_method': 'make_to_stock',
	# 		'origin': origin,
	# 		'state': 'draft',
	# 		'warehouse_id': source_location.warehouse_id.id,
	# 		'group_id': self.procurement_group_id.id,
	# 		'propagate_cancel': self.propagate_cancel,
	# 	}
	# 	return data

	production_picking_ids = fields.One2many('stock.picking','raw_production_id')

	# def write(self,vals):
	# 	res = super(MRPProduction,self).write(vals)
	# 	if 'qty_producing' in vals and vals['qty_producing']:
	# 		for production in self:
	# 			if production.state == 'done':
	# 				product_qty = production.product_qty 
	# 			else:
	# 				product_qty = production.qty_producing
	# 			if product_qty > 0:
	# 				for move in production.move_raw_ids:
	# 					product_uom_qty = (move.product_uom_qty * move.raw_material_production_id.qty_producing) / move.raw_material_production_id.product_qty 
	# 					final_product_qty = move.product_uom._compute_quantity(product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
	# 					move.product_uom_qty = final_product_qty
	# 	return res 


	# def product_uom_qty(self):
	#     final_product_qty = 0
	#     raw_material_production_id  = self
	#     if raw_material_production_id.state == 'done':
	#         product_qty = move.raw_material_production_id.product_qty 
	#     else:
	#         product_qty = move.raw_material_production_id.qty_producing
	#     if product_qty > 0:
	#         product_uom_qty = (move.product_uom_qty * move.raw_material_production_id.qty_producing) / move.raw_material_production_id.product_qty 
	#         final_product_qty = move.product_uom._compute_quantity(
	#             product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
		
	#     return final_product_qty


	def action_confirm(self):
		res = super(MRPProduction,self).action_confirm()
		print('\n\n=========self.picking_ids=====',self.picking_ids)
		if self.picking_ids:
			for picking in self.picking_ids:
				picking.raw_production_id = self.id

				# _compute_reserved_availability
		return res


	def write(self,vals):
	    res = super(MRPProduction,self).write(vals)
	    if 'qty_producing' in vals:
	        for production in self:
	            if production.production_picking_ids:
	                for picking in production.production_picking_ids:
	                	picking.move_update_qty()
	                    # move_ids = picking.move_ids_without_package
	                    # for move in move_ids:
	                    #     move_line_ids = move.move_line_ids
	                    #     for move_line in 
	                    #     move.product_uom_qty = move.reserved_availability

	    return res
