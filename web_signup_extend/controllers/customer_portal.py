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
		"""
		Add two fields to partner
		:param redirect: redirecting to the other route
		:param post: post values dict
		:return: response
		"""
		response = super(CustomerPortalNewsLetter, self).account(redirect, **post)
		if post and request.httprequest.method == 'POST':
			values = {
				'subscribed_to_newsletter': post.get('subscribed_to_newsletter', False),
				'subscribed_to_sms': post.get('subscribed_to_sms', False)
			}
			request.env.user.partner_id.sudo().write(values)
		return response

	@route('/my/account/delete', type="json", auth="user", website=True)
	def delete_my_account(self):
		"""
		Delete the user's account
		:return: response
		"""
		# Delete user's account
		user_id = request.env.user.id
		request.session.logout()
		request.env.cr.execute(f"""DELETE from res_users where id={user_id};""")
		return request.redirect('/web/login', 303)
