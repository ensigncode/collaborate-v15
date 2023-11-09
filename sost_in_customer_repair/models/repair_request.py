# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, SUPERUSER_ID


class RepairRequest(models.Model):
	_name = 'repair.request'
	_description = 'Repair Request'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'partner_id'

	name = fields.Char(string="Namefixed_location_id")
	partner_id = fields.Many2one('res.partner',string="Owner")
	product_id = fields.Many2one('product.product',string="Product")
	state = fields.Selection([('not_ok','Not Ok'),
							('fixed','Fixed'),
							('replaced','Replaced'),
							('damage','Damage')],default='not_ok',string="State")

	description = fields.Text(string="Description")
	picking_id = fields.Many2one('stock.picking',string="Transfer")
	location_dest_id = fields.Many2one('stock.location',string="Destination Location")
	
	current_location_id = fields.Many2one('stock.location',string="Current Location")

	# 	'stock.location', string='Location', index=True, tracking=True,
	# 	readonly=False, store=True,
	# 	copy=False, group_expand='_read_group_location_ids', ondelete='restrict')
	location_id = fields.Many2one(
		'stock.location', string='Location', index=True, tracking=True,
		readonly=False)
	warehouse_id = fields.Many2one(
		'stock.warehouse', string='warehouse', index=True, tracking=True,
		readonly=False, store=True,
		copy=False, group_expand='_read_group_warehouse_ids', ondelete='restrict')
	color = fields.Integer('Color Index', default=0)
	repair_image_ids = fields.One2many('repair.image', 'repair_request_id', string="Extra images", copy=True)

	accepted_by_warehouse = fields.Boolean(string="Accepted By Warehouse")
	wh_message_1 = fields.Char(default="Accepted By Warehouse")
	wh_message_2 = fields.Char(default="Not Accepted By Warehouse")	

	@api.model
	def create(self,vals_list):
		result = super(RepairRequest,self).create(vals_list)
		for res in result:
			res.accepted_by_warehouse = True
			aa = res.warehouse_id.reparation_location_id or res.warehouse_id.lot_stock_id
			res.current_location_id = res.warehouse_id.reparation_location_id or res.warehouse_id.lot_stock_id
		return result


	# def _create_internal_transfer(self,new_warehouse_id,line_vals):
	# 	picking_id = False
	# 	location_dest_id = new_warehouse_id.repair_location_id or new_warehouse_id.fixed_location_id
	# 	if 'location_id' in line_vals and line_vals['location_id'] and location_dest_id:
	# 		move_lines_vals = {}
	# 		line_vals.update({'location_dest_id': location_dest_id.id,
	# 				'location_id': line_vals['location_id'],
	# 				'product_uom_qty':1,
	# 				'name':self.product_id.display_name,
	# 				'product_uom':self.product_id.uom_id.id})
	# 		move_lines_vals = {
	# 				'partner_id' : self.partner_id.id,
	# 				'picking_type_id': self.env.ref('stock.picking_type_internal').id,
	# 				'location_id': line_vals['location_id'],
	# 				'location_dest_id': location_dest_id.id,
	# 				'move_lines': [(0, 0,line_vals)],
	# 		}
	# 		picking_id = self.env['stock.picking'].create(move_lines_vals)
	# 		self.picking_id = picking_id.id
	# 	return True

	reparation_location_id = fields.Many2one('stock.location',string="Reparation Location")
	repaired_location_id = fields.Many2one('stock.location',string="Repaired Location")


	def _create_internal_transfer(self,new_warehouse_id,line_vals):
		picking_id = False
		# location_dest_id = new_warehouse_id.repair_location_id or new_warehouse_id.fixed_location_id
		if 'location_id' in line_vals and line_vals['location_id']:

			current_location_id = line_vals['location_id']

			if current_location_id.repair_type == 'reparation':
				location_dest_id = new_warehouse_id.reparation_location_id or new_warehouse_id.lot_stock_id

			elif current_location_id.repair_type == 'repaired':
				location_dest_id = new_warehouse_id.repaired_location_id or new_warehouse_id.lot_stock_id
			
			else:
				location_dest_id =  new_warehouse_id.lot_stock_id

			move_lines_vals = {}
			line_vals.update({'location_dest_id': location_dest_id.id,
					'location_id': current_location_id.id,
					'product_uom_qty':1,
					'name':self.product_id.display_name,
					'product_uom':self.product_id.uom_id.id})
			move_lines_vals = {
					'partner_id' : self.partner_id.id,
					'picking_type_id': self.env.ref('stock.picking_type_internal').id,
					'location_id': line_vals['location_id'],
					'location_dest_id': location_dest_id.id,
					'move_lines': [(0, 0,line_vals)],
			}
			picking_id = self.env['stock.picking'].create(move_lines_vals)
			self.picking_id = picking_id.id
		return True

	def write(self, vals):
		for obj in self:
			old_warehouse_id = obj.warehouse_id
			line_vals = {
				# 'location_id':self.location_dest_id.id,
				'location_id':self.current_location_id,
				'product_id':self.product_id.id,
			}
		result = super(RepairRequest, self).write(vals)
		if 'warehouse_id' in vals and vals['warehouse_id']:
			for obj in self:
				new_warehouse_id = obj.warehouse_id
				obj._create_internal_transfer(new_warehouse_id,line_vals)
				obj.accepted_by_warehouse = False
		return result
			
	def action_send_mail(self):
		''' 
			Opens a wizard to compose an email, with relevant mail template loaded by default 
		'''
		self.ensure_one()
		template_id = self.env.ref('sost_in_customer_repair.email_template_repair_request')
		lang = self.env.context.get('lang')
		template = template_id
		if template.lang:
			lang = template._render_lang(self.ids)[self.id]
		ctx = {
			'default_model': 'repair.request',
			'default_partner_ids':[(6,0,self.partner_id.ids)],
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id.id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True,
			'custom_layout': "mail.mail_notification_paynow",
			'force_email': True,
			'model_description': 'Hello',
		}
		return {
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(False, 'form')],
			'view_id': False,
			'target': 'new',
			'context': ctx,
		}

	@api.model
	def _read_group_warehouse_ids(self,warehouses, domain, order):
		# search_domain = [('usage', '=', 'internal')]
		search_domain = [('company_id', '=', self.env.company.id)]
		warehouse_ids = warehouses._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
		return warehouses.browse(warehouse_ids)

	# @api.model
	# def _read_group_location_ids(self,locations, domain, order):
	# 	search_domain = [('usage', '=', 'internal')]
	# 	location_ids = locations._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
	# 	return locations.browse(location_ids)
	