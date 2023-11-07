# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, SUPERUSER_ID


class RepairRequest(models.Model):
	_name = 'repair.request'
	_description = 'Repair Request'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	partner_id = fields.Many2one('res.partner',string="Owner")
	product_id = fields.Many2one('product.product',string="Product")
	state = fields.Selection([('not_ok','Not Ok'),
							('fixed','Fixed'),
							('replaced','Replaced'),
							('damage','Damage')],default='not_ok',string="State")

	description = fields.Text(string="Description")
	picking_id = fields.Many2one('stock.picking',string="Transfer")
	location_dest_id = fields.Many2one('stock.location',string="Destination Location")
	location_id = fields.Many2one(
		'stock.location', string='Location', index=True, tracking=True,
		readonly=False, store=True,
		copy=False, group_expand='_read_group_location_ids', ondelete='restrict')
	color = fields.Integer('Color Index', default=0)
	repair_image_ids = fields.One2many('repair.image', 'repair_request_id', string="Extra images", copy=True)


	def write(self, vals):
		print("\n\n vals ==== ",vals)
		if vals.get('location_id'):
			pick_output = self.env['stock.picking'].create({
				'partner_id' : self.partner_id.id,
				'picking_type_id': self.env.ref('stock.picking_type_internal').id,
				'location_id': self.location_id.id,
				'location_dest_id': self.location_dest_id.id,
				'move_lines': [(0, 0, {
					'name': '/',
					'product_id': self.product_id.id,
					'product_uom': self.product_id.uom_id.id,
					# 'product_uom_qty': 10.00,
					# 'procure_method': 'make_to_stock',
            	})],
        	})
			print("\n\n pick output ==== ",pick_output)
		result = super(RepairRequest, self).write(vals)
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
	def _read_group_location_ids(self,locations, domain, order):
		search_domain = [('usage', '=', 'internal')]
		location_ids = locations._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
		return locations.browse(location_ids)
	