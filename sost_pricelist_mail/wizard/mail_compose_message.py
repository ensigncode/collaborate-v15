# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class MailComposeMessage(models.TransientModel):
	_inherit = 'mail.compose.message'

	is_product_pricelist = fields.Boolean('Is Product Pricelist')

	def default_get(self, fields):
		res = super(MailComposeMessage, self).default_get(fields)
		if self._context.get('active_model') == 'product.pricelist':
			res['is_product_pricelist'] = True
			model = self.env.context.get('active_model')
		return res

	def _action_send_mail(self, **kwargs):
		if self.partner_ids and self.is_product_pricelist and self._context.get('active_model') == 'product.pricelist':
			for partner in self.partner_ids:
				message_body = self.body
				partner.message_post(body=message_body,subject=self.subject,attachment_ids=self.attachment_ids.ids)
		return super()._action_send_mail(**kwargs)