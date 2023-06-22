# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.http import request


_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS.add('subscribed_to_newsletter')
SIGN_UP_REQUEST_PARAMS.add('subscribed_to_sms')


class AuthSignupHomeNewsletter(AuthSignupHome):

	def do_signup(self, qcontext):
		"""
		Update the newsletter, sms field on the partner
		:param qcontext: value dictionary posted by registered user
		:return: None
		"""
		super(AuthSignupHomeNewsletter, self).do_signup(qcontext)
		request.env.user.partner_id.sudo().write({
			'subscribed_to_newsletter': qcontext.get('subscribed_to_newsletter', False) or False,
			'subscribed_to_sms': qcontext.get('subscribed_to_sms', False) or False,
		})
