# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Users(models.Model):
	_inherit = 'res.users'

	subscribed_to_newsletter = fields.Boolean(string="Subscribed To Newsletter?",
	                                          related="partner_id.subscribed_to_newsletter",
	                                          help="If it's checked then user will be subscribed for Newsletter.",
	                                          store=True)
	subscribed_to_sms = fields.Boolean(string="Subscribed To SMS?",
	                                   related="partner_id.subscribed_to_sms",
	                                   help="If it's checked then user will be subscribed for SMS.",
	                                   store=True)

	@api.model
	def signup(self, values, token=None):
		"""
		Override signup to get the partner with same email id if partner not found
		:param values: signup values
		:param token: signup token
		:return: login, password
		"""
		if not values.get('partner_id', False):
			values['partner_id'] = self.env['res.partner'].sudo().search([('email', '=', values.get('login', ''))], limit=1).id
		return super(Users, self).signup(values, token)
