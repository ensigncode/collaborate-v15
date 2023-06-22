# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo.http import content_disposition, Controller, request, route


_logger = logging.getLogger(__name__)


class CustomerPortalNewsLetter(CustomerPortal):

	OPTIONAL_BILLING_FIELDS = CustomerPortal.OPTIONAL_BILLING_FIELDS + ["subscribed_to_newsletter", "subscribed_to_sms"]

	@route(['/my/account'], type='http', auth='user', website=True)
	def account(self, redirect=None, **post):
		response = super(CustomerPortalNewsLetter, self).account(redirect, **post)
		if post and request.httprequest.method == 'POST':
			values = {
				'subscribed_to_newsletter': post.get('subscribed_to_newsletter', False),
				'subscribed_to_sms': post.get('subscribed_to_sms', False)
			}
			request.env.user.partner_id.sudo().write(values)
		return response
