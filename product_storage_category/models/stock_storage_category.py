# -*- coding: utf-8 -*-
from odoo import models,fields,api

class StockStorageCategoryCapacity(models.Model):
	_inherit = 'stock.storage.category.capacity'

	product_tmp_id = fields.Many2one('product.template',string="Template")
	prod_storage_category_line_id = fields.Many2one('product.storage.category.lines',string="Category Lines")
	active = fields.Boolean(string="Active",default=True)

	# def unlink(self):
	# 	for record in self:
	# 		if record.prod_storage_category_line_id:
	# 			record.prod_storage_category_line_id.unlink()
	# 	super(StockStorageCategoryCapacity, self).unlink()

	@api.model
	def create(self,vals):
		res = super(StockStorageCategoryCapacity,self).create(vals)
		if not res.prod_storage_category_line_id:
			prod_storage_category_line_id = self.env['product.storage.category.lines'].create({'storage_category_id':res.storage_category_id.id,'storage_capacity':res.quantity,'product_tmp_id':res.product_id.product_tmpl_id.id})
			res.prod_storage_category_line_id = prod_storage_category_line_id.id
		return res

class StockStorageCategoryCapacity(models.Model):
	_inherit = 'stock.storage.category.capacity'
	
	auto_putaway_rule = fields.Boolean(string="Auto Putaway Rules",related="storage_category_id.auto_putaway_rule")

class StockStorageCategory(models.Model):
	_inherit = 'stock.storage.category'

	auto_putaway_rule = fields.Boolean(string="Auto Putaway Rules")
	storage_location = fields.Integer(string="Storage Location")


	def _default_location_id(self):
		wh = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
		input_loc, _ = wh._get_input_output_locations(wh.reception_steps, wh.delivery_steps)
		location_out_id = self.env['stock.location'].search([('id', 'child_of', input_loc.id), '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id),('storage_category_id','=',self.id)], limit=1)
		if not location_out_id:
			location_out_id = self.env['stock.location'].search([('id', 'child_of', input_loc.id), '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)], limit=1)
		return {'location_out_id':location_out_id,'location_in_id':input_loc or False}

	def update_putaway_rule(self):
		putaway_rule_id = False
		for storage in self:
			if storage.auto_putaway_rule:
				if 'default_destination_id' in self._context  and self._context['default_destination_id']:
					destination_id  = self._context['default_destination_id']
				else:
					location_vals = self._default_location_id()
					destination_id = location_vals['location_out_id']

				for product_line in storage.product_capacity_ids:
					location_ids = self.env['stock.location'].search([('storage_category_id','=',self.id),('location_id','=',destination_id.id)])
					
					for location in location_ids:
						location_in_id = location
						location_out_id = destination_id

						product_id = product_line.product_id
						if product_id and not product_id.qty_available:
							rules = []
							query1 = """SELECT id from stock_putaway_rule WHERE PRODUCT_ID='%s'""" %(product_id.id)
							self._cr.execute(query1)
							for row in self._cr.fetchall():
								rules.append(row[0])						
							rule_ids = self.env['stock.putaway.rule'].sudo().search([('id','in',rules)])
							storage_location_rule_ids = rule_ids.filtered(lambda x:x.location_out_id.storage_category_id and x.location_out_id.storage_category_id.id == storage.id)
							if storage_location_rule_ids:
								for rule in storage_location_rule_ids:
									rule.unlink()


						elif location_out_id and location_in_id:
							domain = [
								('storage_category_id','=',self.id),
								('product_id','=',product_line.product_id.id),
								('location_in_id','=',location_in_id.id),
							]
							rule_id = self.env['stock.putaway.rule'].search(domain)
							if not rule_id:
								vals = {
									# 'storage_category_id':self.id,
									'product_id':product_line.product_id.id,
									'location_out_id':location_in_id.id,
									'location_in_id':location_out_id.id,
									# 'location_out_id':location_out_id.id,
									# 'location_in_id':location_in_id.id,
								}
								putaway_rule_id = self.env['stock.putaway.rule'].create(vals)
		return putaway_rule_id
				
	@api.model
	def create(self,vals):
		res = super(StockStorageCategory,self).create(vals)
		for storage in res:
			storage.update_putaway_rule()
		return res

	def write(self,vals):
		res = super(StockStorageCategory,self).write(vals)
		for storage in self:
			storage.update_putaway_rule()
		return res


class StockPutawayRule(models.Model):
	_inherit = 'stock.putaway.rule'

	prod_storage_category_line_id = fields.Many2one('product.storage.category.lines',string="Category Lines")
	location_out_storage_category_id = fields.Many2one('stock.storage.category',string="Storage Category",related="location_out_id.storage_category_id",store=True)

	


class StockPicking(models.Model):
	_inherit = 'stock.picking'

# 	def get_lines(self,storage_category_lines,used_location):
# 		lines = []
# 		destination_id = self.location_dest_id
# 		for line in storage_category_lines:
# 			storage_category_id = line.storage_category_id
# 			domain = [
# 				('storage_category_id','=',storage_category_id.id),
# 				('location_id','=',destination_id.id),
# 				('id','!=',destination_id.id),
# 				('id','not in',used_location),
# 			]
# 			location_ids = self.env['stock.location'].search(domain)
# 			rule_ids = self.env['stock.putaway.rule'].search([('storage_category_id','=',storage_category_id.id)])
# 			location_rule_ids = []
# 			left_location_ids = []
# 			for rule in rule_ids:
# 				location_rule_ids += rule.location_out_id.ids		

# 			for location in location_ids:
# 				if location not in location_rule_ids:
# 					left_location_ids.append(location.id)

# 			vals = {
# 				'product_id':line.product_id.id,
# 				'location_in_id':destination_id.id,
# 				# 'storage_category_id':storage_category_id.id,
# 			}
# 			if left_location_ids:
# 				vals.update({'location_out_id':left_location_ids[0]})
# 			lines.append(vals)
# 		return lines


# 	def action_update_rules(self):
# 		line_data = []
# 		used_location = []
# 		for line in self.move_ids_without_package:
# 			product_id = line.product_id

# 			if product_id:
# 				storage_category_lines = product_id.product_storage_line_ids
# 				datas = self.get_lines(storage_category_lines,used_location)

# 				for data in datas:
# 					data.update({'product_id':product_id.id})
# 					line_data.append((0,0,data))
# 					if 'location_out_id' in data and data['location_out_id']:
# 						used_location.append(data['location_out_id'])

# 		rule_vals = {'picking_id':self.id,'product_putaway_rule_line_ids':line_data}
# 		rule_id = self.env['product.putaway.rule'].create(rule_vals)
# 		return {
# 			'name': 'Putaway Rule',
# 			'view_mode': 'form',
# 			'target': 'new',
# 			'res_id': rule_id.id,
# 			'res_model': 'product.putaway.rule',
# 			'type': 'ir.actions.act_window',
# 		}

# 	def get_product_putaway_rule_data(self):
# 		line_data = []
# 		used_location = []
# 		for line in self.move_ids_without_package:
# 			product_id = line.product_id
# 			datas =  product_id.get_rule_lines()
# 		return True

	def _action_done(self):
		res = super(StockPicking,self)._action_done()
		# self.with_context(location_dest_id=self.location_dest_id).get_product_putaway_rule_data()

		precision_digits = max(6, self.sudo().env.ref('product.decimal_product_uom').digits * 2)
		# Use a select instead of ORM search for UoM robustness.
		query = """SELECT id FROM stock_quant WHERE (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
					AND round(reserved_quantity::numeric, %s) = 0
					AND (round(inventory_quantity::numeric, %s) = 0 OR inventory_quantity IS NULL)
					AND user_id IS NULL;"""
		params = (precision_digits, precision_digits, precision_digits)
		self.env.cr.execute(query, params)
		quant_ids = self.env['stock.quant'].browse([quant['id'] for quant in self.env.cr.dictfetchall()])

		for quant in quant_ids:
			location_id = quant.location_id
			product_id = quant.product_id

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
						for rule in rule_ids:
							rule.sudo().unlink()
			quant.sudo().unlink()
		return res

