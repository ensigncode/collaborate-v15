# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class UpdatePricelist(models.TransientModel):
	_name = 'update.pricelist'
	_description = 'Update Pricelist'

	pricelist_id = fields.Many2one('product.pricelist',string="Pricelist")
	update_pricelist_line_ids = fields.One2many('update.pricelist.line','pricelist_line_id')

	def update_pricelist_send_mail(self):
		update_pricelist_lines = []
		self.pricelist_id.pricelist_info_ids = [(6,0,[])]
		for line in self.update_pricelist_line_ids:
			vals = {
				'product_tmpl_id':line.product_tmpl_id.id if line.product_tmpl_id else False,
				'product_variant_id':line.product_variant_id.id if line.product_variant_id else False, 
				'currency_id':line.currency_id.id if line.currency_id else False,
				'start_date':line.start_date or '',
				'end_date':line.end_date or '',
				'price_unit':line.price_unit,
			}
			update_pricelist_lines.append((0,0,vals))
		self.pricelist_id.pricelist_info_ids = update_pricelist_lines
		mail_template_id = self.env.ref('sost_pricelist_mail.template_pricelist_mail')
		lang = self.env.context.get('lang')
		ctx = {
			'default_model': 'product.pricelist',
			'default_res_id': self.pricelist_id.ids[0],
			'default_use_template': True,
			'default_template_id': mail_template_id.id,
			'default_composition_mode': 'comment',
			'force_email': True,
			'default_is_product_pricelist':True,
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

class UpdatePricelistLine(models.TransientModel):
	_name = 'update.pricelist.line'
	_description = 'Update Pricelist Line'

	product_tmpl_id = fields.Many2one('product.template',string="Product")
	pricelist_line_id = fields.Many2one('update.pricelist',string="Pricelist line")
	product_variant_id = fields.Many2one('product.product',string="Product Variant")
	currency_id = fields.Many2one('res.currency',string="Currency")
	availablity_message = fields.Char(string="Availablity")
	start_date = fields.Date(string="Start Date")
	end_date = fields.Date(string="End Date")
	price_unit = fields.Char(string="Price Unit")
	mail_compose_msg_id = fields.Many2one('mail.compose.message',string="Mail Compose Msg")

