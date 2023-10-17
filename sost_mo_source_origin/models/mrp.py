# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class MRPProduction(models.Model):
	_inherit = 'mrp.production'

	sale_order_id = fields.Many2one('sale.order',string="Order",compute="_compute_sale_order",store=True)

	@api.depends('origin','state',
				'procurement_group_id',
				'procurement_group_id.mrp_production_ids',
				'procurement_group_id.mrp_production_ids',
				'procurement_group_id.mrp_production_ids.move_dest_ids',
				'procurement_group_id.mrp_production_ids.move_dest_ids.group_id',
				'procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id')
	def _compute_sale_order(self):
		for production in self:
			order_id = False
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
				parent_production_id = production._get_sources()
				for parent_prod in parent_production_id:
					if parent_prod and parent_prod.sale_order_id:
						order_id = parent_prod.sale_order_id.id
			production.sale_order_id = order_id

