# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResPartner(models.Model):
	_inherit = "res.partner"

	location_ids = fields.Many2many('stock.location',string="Inventory Locations")

class StockPicking(models.Model):
	_inherit = "stock.picking"


	def update_location(self):
		location_dest_id = self.location_dest_id
		location_vals = {}
		update_dest_id = False
		if self.owner_id and self.owner_id.location_ids:
			locations = []
			owner_locations = ",".join(str(location.complete_name) for location in self.owner_id.location_ids)
			update_dest_id = False 
			first_location_dest = location_dest_id.complete_name.split('/')
			if first_location_dest:
				first_location_dest = first_location_dest[0]
			else:
				first_location_dest = location_dest_id.complete_name
			for location in self.owner_id.location_ids:
				find_loc = location.complete_name.startswith(first_location_dest)
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
		if 'owner_id' in vals and vals['owner_id']:
			for obj in self:
				obj.update_location()
		return res
