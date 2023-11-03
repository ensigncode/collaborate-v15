# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict
from odoo import conf, http, _
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR, AND

_logger = logging.getLogger(__name__)


class CustomerAppointmentReceipt(CustomerPortal):

	def _prepare_appointments_domain(self):
		event_sudo = request.env['calendar.event'].sudo()
		event_ids = event_sudo.search([('partner_ids', 'in', request.env.user.partner_id.ids)])
		return [
			('res_model', '=', 'calendar.event'),
			('res_id', 'in', event_ids.ids)
		]

	def _prepare_home_portal_values(self, counters):
		values = super()._prepare_home_portal_values(counters)
		attachment_ids = request.env['ir.attachment'].sudo()
		if 'appointment_count' in counters:
			values['appointment_count'] = attachment_ids.search_count(self._prepare_appointments_domain())
		return values

	@http.route(['/my/receipts', '/my/receipts/page/<int:page>'], type='http', auth="user", website=True)
	def portal_my_receipts(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
							search_in='all', groupby='none', **kw):
		values = self._prepare_portal_layout_values()
		attachment_sudo = request.env['ir.attachment'].sudo()

		attachment_ids = attachment_sudo.search(self._prepare_appointments_domain())

		domain = []
		if date_begin and date_end:
			domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
		#
		searchbar_sortings = {
			'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
			'name': {'label': _('Name'), 'order': 'name asc, id asc'},
		}
		#
		# # default sortby order
		if not sortby:
			sortby = 'date'
		order = searchbar_sortings[sortby]['order']
		#
		searchbar_filters = {
			'all': {'label': _('All'), 'domain': []},
		}
		#
		searchbar_inputs = {
			'all': {'input': 'all', 'label': _('Search in All')},
			'name': {'input': 'name', 'label': _('Search in Name')},
			'description': {'input': 'description', 'label': _('Search in Description')},
			'create_date': {'input': 'create_date', 'label': _('Search in Create Date')},
			'mimetype': {'input': 'mimetype', 'label': _('Search in Mime Type')},
		}
		#
		searchbar_groupby = {
			'none': {'input': 'none', 'label': _('None')},
			'mimetype': {'input': 'mimetype', 'label': _('Type')},
		}
		#
		# # search
		if search and search_in:
			search_domain = []
			if search_in in ('name', 'all'):
				search_domain = OR([search_domain, [('name', 'ilike', search)]])
			if search_in in ('description', 'all'):
				search_domain = OR([search_domain, [('description', 'ilike', search)]])
			if search_in in ('create_date', 'all'):
				search_domain = OR([search_domain, [('create_date', 'ilike', search)]])
			if search_in in ('mimetype', 'all'):
				search_domain = OR([search_domain, [('mimetype', 'ilike', search)]])
			domain += search_domain

		domain += [('id', 'in', attachment_ids.ids)]
		# count for pager
		attachment_count = attachment_sudo.search_count(domain)
		#
		# default filter by value
		if not filterby:
			filterby = 'all'
		domain += searchbar_filters[filterby]['domain']

		# make pager
		pager = portal_pager(
			url="/my/receipts",
			url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
					  'groupby': groupby, 'search_in': search_in, 'search': search},
			total=attachment_count,
			page=page,
			step=self._items_per_page
		)
		attachment_ids = attachment_sudo.search(
			domain,
			order=order,
			limit=self._items_per_page,
			offset=pager['offset']
		)
		values.update({
			'date': date_begin,
			'date_end': date_end,
			'page_name': 'receipts',
			'default_url': '/my/receipts',
			'pager': pager,
			'attachment_ids': attachment_ids,
			'searchbar_sortings': searchbar_sortings,
			'searchbar_groupby': searchbar_groupby,
			'searchbar_inputs': searchbar_inputs,
			'search_in': search_in,
			'search': search,
			'sortby': sortby,
			'groupby': groupby,
			'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
			'filterby': filterby,
			'base_url': http.request.env["ir.config_parameter"].sudo().get_param("web.base.url"),
		})
		return request.render("appointment_receipt.portal_my_receipt", values)