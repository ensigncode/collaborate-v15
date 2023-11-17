# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	@api.depends('origin','state',
				'procurement_group_id',
				'procurement_group_id.mrp_production_ids',
				'procurement_group_id.mrp_production_ids',
				'procurement_group_id.mrp_production_ids.move_dest_ids',
				'procurement_group_id.mrp_production_ids.move_dest_ids.group_id',
				'procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id',
				)
	def _compute_source_document(self):
		for production in self:
			order_id = False
			source_document = ''
			orig_source_document = ''
			if production.procurement_group_id and production.procurement_group_id.mrp_production_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id:
				order_id =  production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.id
			
			if not order_id and production.origin:
				origins = production.origin.split('S')
				origin_data = []
				for origin in origins:
					if origin:
						order_name = 'S'
						for letter in origin:
							if letter.isalnum() and len(order_name) < 6:
								order_name += letter
							else:
								break
						if order_name:
							origin_data.append(order_name)
				for ord_name in origin_data:
					order = self.env['sale.order'].search([('name','=',ord_name)])
					if order:
						order_id = order.id
						source_document = order.name
			production.source_document = source_document
			production.orig_source_document = orig_source_document
			
	source_document = fields.Char(string="Source Document",compute="_compute_source_document")
	orig_source_document = fields.Char(string="Original Source Document")

