# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResPartner(models.Model):
	_inherit = "res.partner"

	location_ids = fields.Many2many('stock.location',string="Inventory Locations")

class StockPicking(models.Model):
	_inherit = "stock.picking"

	assign_owner_id = fields.Many2one('res.partner',string="Assign Owner")

	def update_location(self):
		location_dest_id = self.location_dest_id
		location_vals = {}
		update_dest_id = False
		if self.assign_owner_id and self.assign_owner_id.location_ids:
			locations = []
			owner_locations = ",".join(str(location.complete_name) for location in self.assign_owner_id.location_ids)
			update_dest_id = False
			for location in self.assign_owner_id.location_ids:
				find_loc = location.complete_name.startswith(location_dest_id.complete_name)
				if find_loc:
					update_dest_id = location
		if update_dest_id: 
			self.location_dest_id = update_dest_id.id
			for move in self.move_ids_without_package:
				move.location_dest_id = update_dest_id.id
		return True

	@api.model
	def create(self,vals):
		res = super(StockPicking,self).create(vals)
		res.update_location()
		return res


	def write(self,vals):
		res = super(StockPicking,self).write(vals)
		if 'assign_owner_id' in vals and vals['assign_owner_id']:
			for obj in self:
				obj.update_location()
		return res
