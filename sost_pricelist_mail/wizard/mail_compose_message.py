# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class MailComposeMessage(models.TransientModel):
	_inherit = 'mail.compose.message'

	update_pricelist_line_ids = fields.One2many('update.pricelist.line','mail_compose_msg_id')
	is_product_pricelist = fields.Boolean('Is Product Pricelist')

	@api.model
	def default_get(self, fields):
		res = super(MailComposeMessage, self).default_get(fields)
		if self._context.get('active_model') == 'product.pricelist':
			res['is_product_pricelist'] = True
			model = self.env.context.get('active_model')
			active_id = self.env[model].browse(self.env.context.get('active_id'))
		return res

	def _action_send_mail(self, **kwargs):
		if self.partner_ids and self.is_product_pricelist and self._context.get('active_model') == 'update.pricelist':
			for partner in self.partner_ids:
				message_body = self.body
				partner.message_post(body=message_body,subject=self.subject,attachment_ids=self.attachment_ids.ids)
		return super()._action_send_mail(**kwargs)