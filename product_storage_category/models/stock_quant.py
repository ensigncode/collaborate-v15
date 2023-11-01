# -*- coding: utf-8 -*-

from odoo import models,fields,api, _

class StockInventoryAdjustmentName(models.TransientModel):
	_inherit = 'stock.inventory.adjustment.name'

	def action_apply(self):
		data_found = False
		quant_ids = self
		occupied_locations = []
		line_data = []
		occupied_locations = []
		no_empty_location_found = False
		quant_ids = self.quant_ids.filtered('inventory_quantity_set')
		# quant_ids = self.quant_ids
		if 'update_inventory' not in self._context:
			for quant in quant_ids:
				location_dest_id = quant.location_id
				product_id = quant.product_id
				datas =  product_id.get_rule_lines(location_dest_id,occupied_locations)
				# print('\n\n===datas==',datas)
				if datas['create_product_rule']:
					if not datas['issue_product_rule']:
						data_vals = datas['vals']
						data_vals.update({'product_id':product_id.id,'location_in_id':location_dest_id.id,'fix_location':True})
						line_data.append(data_vals)
						occupied_locations.append(datas['occupied_location_id'])
					else:
						no_empty_location_found = True
						data_vals = datas['vals']
						data_vals.update({'product_id':product_id.id})
						line_data.append(data_vals)
						
			if no_empty_location_found and line_data:
				rule_line_data = []
				for l_data in line_data:
					l_data.update({'operation_type':'existing','location_in_id':location_dest_id.id})
					rule_line_data.append((0,0,l_data))
				rule_vals = {'quant_ids':[(6,0,quant_ids.ids)],'product_putaway_rule_line_ids':rule_line_data}
				rule_id = self.env['product.putaway.rule'].create(rule_vals)
				return {
					'name': _('Putaway Rule'),
					'type': 'ir.actions.act_window',
					'view_mode': 'form',
					'views': [(False, 'form')],
					'res_model': 'product.putaway.rule',
					'target': 'new',
					'res_id': rule_id.id,
				}
			elif line_data:
				for l_data in line_data:
					l_data.pop('fix_location')
					rule_id = self.env['stock.putaway.rule'].create(l_data)
		res = super(StockInventoryAdjustmentName,self).action_apply()
		return res

class StockQuant(models.Model):
	_inherit = 'stock.quant'

	def action_apply_inventory(self):
		data_found = False
		quant_ids = self
		occupied_locations = []
		line_data = []
		occupied_locations = []
		no_empty_location_found = False
		if 'update_inventory' not in self._context:
			for quant in quant_ids:
				location_dest_id = quant.location_id
				product_id = quant.product_id
				datas =  product_id.get_rule_lines(location_dest_id,occupied_locations)
				# print('\n\n===datas==',datas)
				if datas['create_product_rule']:
					if not datas['issue_product_rule']:
						data_vals = datas['vals']
						data_vals.update({'product_id':product_id.id,'location_in_id':location_dest_id.id,'fix_location':True})
						line_data.append(data_vals)
						occupied_locations.append(datas['occupied_location_id'])
					else:
						no_empty_location_found = True
						data_vals = datas['vals']
						data_vals.update({'product_id':product_id.id})
						line_data.append(data_vals)
						
			if no_empty_location_found and line_data:
				rule_line_data = []
				for l_data in line_data:
					l_data.update({'operation_type':'existing','location_in_id':location_dest_id.id})
					rule_line_data.append((0,0,l_data))
				rule_vals = {'quant_ids':[(6,0,quant_ids.ids)],'product_putaway_rule_line_ids':rule_line_data}
				rule_id = self.env['product.putaway.rule'].create(rule_vals)
				return {
					'name': _('Putaway Rule'),
					'type': 'ir.actions.act_window',
					'view_mode': 'form',
					'views': [(False, 'form')],
					'res_model': 'product.putaway.rule',
					'target': 'new',
					'res_id': rule_id.id,
				}
			elif line_data:
				for l_data in line_data:
					l_data.pop('fix_location')
					rule_id = self.env['stock.putaway.rule'].create(l_data)
		res = super(StockQuant,self).action_apply_inventory()
		return res

	@api.model
	def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
		""" Create or update move lines.
		"""
		res = super(StockQuant,self)._update_reserved_quantity(product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False)
		for quant in self:
			product_id = quant.product_id
			for storage_line in product_id.product_storage_line_ids:
				storage_line.storage_category_id.update_putaway_rule()
		return res

	@api.model
	def _unlink_zero_quants(self):

		print('\n\n\n====_unlink_zero_quants==============')
		""" _update_available_quantity may leave quants with no
		quantity and no reserved_quantity. It used to directly unlink
		these zero quants but this proved to hurt the performance as
		this method is often called in batch and each unlink invalidate
		the cache. We defer the calls to unlink in this method.
		"""
		precision_digits = max(6, self.sudo().env.ref('product.decimal_product_uom').digits * 2)
		# Use a select instead of ORM search for UoM robustness.
		query = """SELECT id FROM stock_quant WHERE (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
													 AND round(reserved_quantity::numeric, %s) = 0
													 AND (round(inventory_quantity::numeric, %s) = 0 OR inventory_quantity IS NULL)
													 AND user_id IS NULL;"""
		params = (precision_digits, precision_digits, precision_digits)
		self.env.cr.execute(query, params)
		quants = []
		for quant in self.env.cr.dictfetchall():
			quants.append(quant['id'])
		quant_ids = self.env['stock.quant'].search([('id','in',quants)])

		for quant in quant_ids:

			product_id = quant.product_id
			location_id = quant.location_id
			

			parent_location_id = False
			if location_id.location_id:
				parent_location_id = location_id.location_id
			if parent_location_id:
				location_ids = self.env['stock.location'].search(['|',('id','=',parent_location_id.id),('location_id','=',parent_location_id.id)])
			else:
				location_ids = self.env['stock.location'].search([('location_id','=',parent_location_id.id)])
			check_quants = self.env['stock.quant'].search([('id','=',quant.id),('location_id','in',location_ids.ids),('product_id','=',product_id.id),('on_hand','=',True)])
			
			if not check_quants:
			
				if product_id.product_storage_line_ids:
					for storage_line in product_id.product_storage_line_ids:
						storage_category_id = storage_line.storage_category_id
						query1 = """SELECT id from stock_putaway_rule WHERE LOCATION_OUT_STORAGE_CATEGORY_ID='%s' and  PRODUCT_ID='%s'""" %(storage_category_id.id,product_id.id)
						self._cr.execute(query1)
						rules = []
						for row in self._cr.fetchall():
							rules.append(row[0])  
						rule_ids = self.env['stock.putaway.rule'].sudo().search([('id','in',rules)])

						print('\n\n=====rule_ids======',rule_ids)
						for rule in rule_ids:
							rule.sudo().unlink()
						# rule.sudo().unlink()


			# storage_category_id  = location_id.storage_category_id
			# if storage_category_id  and product_id.product_storage_line_ids:
			# 	storage_line_ids = product_id.product_storage_line_ids.filtered(lambda x:x.storage_category_id and x.storage_category_id.id ==  storage_category_id.id)
			# if storage_category_id:
			# query1 = """SELECT id from stock_putaway_rule WHERE LOCATION_IN_ID='%s' and  PRODUCT_ID='%s'""" %(location_id.id,product_id.id)
			# self._cr.execute(query1)
			# rules = []
			# for row in self._cr.fetchall():
			# 	rules.append(row[0])  
			# rule_ids = self.env['stock.putaway.rule'].sudo().search([('id','in',rules)])
			# print('\n\n\n==========rule_ids=======',rule_ids)

			
			# for rule in rule_ids:
			# 	rule.unlink()

		# stop
		quant_ids.sudo().unlink()