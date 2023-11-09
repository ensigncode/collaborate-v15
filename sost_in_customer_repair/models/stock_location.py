# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, SUPERUSER_ID

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	picking_repair_request_id = fields.Many2one('repair.request',string="Repair Request")

	def _action_done(self):
		res = super(StockPicking,self)._action_done()
		if self.picking_repair_request_id and self.picking_repair_request_id.picking_ids:
			last_picking_id = self.picking_repair_request_id.picking_ids[-1]
			if last_picking_id and last_picking_id.id == self.id:
				self.picking_repair_request_id.accepted_by_warehouse = True
				self.picking_repair_request_id.current_location_id = self.location_dest_id.id
		return res
		
	
class StockLocation(models.Model):
	_inherit = 'stock.location'

	repair_type = fields.Selection([('empty','Empty'),
									('reparation','Reparation'),
									('repaired','Repaired'),
									('repair','Repair'),
									('fixed','Fixed')],string="Repair Type",default="empty")


	def get_main_location_wh(self,main_destination_id):
		warehouse_id = False
		if main_destination_id:
			count = 0
			while count == 0:
				if main_destination_id.location_id and main_destination_id.location_id.usage == 'internal':
					main_destination_id = main_destination_id.location_id
				elif main_destination_id.location_id and main_destination_id.location_id.usage == 'view':
					main_destination_id = main_destination_id.location_id
					count = 1
				else:
					count = 1
			warehouse_id = self.env['stock.warehouse'].search([('code','=',main_destination_id.name)])
		return warehouse_id

	def update_repair_type_wh(self):
		warehouse_id = self.get_main_location_wh(self)
		if self.repair_type == 'repair' and warehouse_id:
			warehouse_id.repair_location_id = self.id
			warehouse_id.fixed_location_id = False
		elif self.repair_type == 'fixed' and warehouse_id:
			warehouse_id.fixed_location_id = self.id
			warehouse_id.repair_location_id = False
		elif warehouse_id:
			warehouse_id.fixed_location_id = False 
			warehouse_id.repair_location_id = False
		return True

	@api.model
	def create(self,vals):
		res = super(StockLocation,self).create(vals)
		if res.repair_type:
			res.update_repair_type_wh()
		return res

	def write(self,vals):
		res = super(StockLocation,self).write(vals)
		if 'repair_type' in vals and vals['repair_type']:
			for obj in self:
				obj.update_repair_type_wh()
		return res

class StockWarehouse(models.Model):
	_inherit = 'stock.warehouse'

	repair_location_id = fields.Many2one('stock.location',string="Repair Location")
	fixed_location_id = fields.Many2one('stock.location',string="Fix Location")

	reparation_location_id = fields.Many2one('stock.location',string="Reparation Location")
	repaired_location_id = fields.Many2one('stock.location',string="Repaired Location")