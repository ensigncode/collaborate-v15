# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# def write(self,vals):
	# 	res = super(SaleOrder,self).write(vals)

	# 	print('\n\n\n========vals==',vals)

	# 	return res

	# def action_confirm(self):
	# 	res = super(SaleOrder,self).action_confirm()
	# 	print('\n\n\n========action_confirm==',self.procurement_group_id)
	# 	procurement_groups = self.env['procurement.group'].search([('sale_id', 'in', self.procurement_group_id.ids)])

	# 	print('\n\n\n========procurement_group_id.mrp_production_ids==',self.procurement_group_id.mrp_production_ids)

	# 	mrp_production_ids = set(procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids) | set(procurement_groups.mrp_production_ids.ids)
	# 	print('\n\n\n========mrp_production_ids==',mrp_production_ids)
	# 	return res

		# procurement_groups = self.env['procurement.group'].search([('sale_id', 'in', self.ids)])
        # mrp_production_ids = set(procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids) |\
        #     set(procurement_groups.mrp_production_ids.ids)



class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	# def write(self,vals):
	# 	res = super(MrpProduction,self).write(vals)
	# 	print('\n\n\n========vals==',vals)
	# 	return res

	def get_order(self,production):
		order_id = False
		if production.procurement_group_id and production.procurement_group_id.mrp_production_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id:
			order_id =  production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
		return order_id

	@api.depends('origin','state',
				'procurement_group_id',
				'procurement_group_id.mrp_production_ids',
				'procurement_group_id.mrp_production_ids',
				'procurement_group_id.mrp_production_ids.move_dest_ids',
				'procurement_group_id.mrp_production_ids.move_dest_ids.group_id',
				'procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id',
				'procurement_group_id.stock_move_ids.move_orig_ids')
	def _compute_source_document(self):
		print('\n\n====_compute_source_document===========')
		for production in self:
			order_id = False
			source_document = ''
			orig_source_document = ''
			# if production.procurement_group_id and production.procurement_group_id.mrp_production_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id:
			# 	order_id =  production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
					

			# Parent Production ID - Parent Manufacturing - Source Manufacturing
			dest_moves = production.procurement_group_id.mrp_production_ids.move_dest_ids
			parent_moves = production.procurement_group_id.stock_move_ids.move_dest_ids
			parent_production_id = (dest_moves | parent_moves).group_id.mrp_production_ids.filtered(lambda p: p.origin != production.origin) - production



			if parent_production_id:
				order_id = production.get_order(parent_production_id)
			else:
				order_id = production.get_order(production)

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
						order_id = order

			if order_id:
				orig_source_document =  order_id.name
				source_document = ''
			else:
				orig_source_document = production.name
				source_document = ''




			print('\n\n=======production=========',production)
			print('\n\n=======order_id=========',order_id)


			# stop
			if parent_production_id and parent_production_id.id < production.id:
				source_document = parent_production_id.name
			else:
				source_document = production.name


# 		  self.ensure_one()
#         dest_moves = self.procurement_group_id.mrp_production_ids.move_dest_ids
#         parent_moves = self.procurement_group_id.stock_move_ids.move_dest_ids
#         return (dest_moves | parent_moves).group_id.mrp_production_ids.filtered(lambda p: p.origin != self.origin) - self


			print('\n\n=======source_document=========',source_document)
			production.source_document = source_document
			production.orig_source_document = orig_source_document

	source_document = fields.Char(string="Source Document")
	orig_source_document = fields.Char(string="Original Source Document",compute="_compute_source_document",store=True)