# -*- coding: utf-8 -*-

from odoo.addons.appointment.controllers.main import Appointment
from odoo import http, _, fields
from babel.dates import format_datetime, format_date
from datetime import datetime
from odoo.tools.misc import get_lang
from odoo.http import request
from odoo.tools import html2plaintext, is_html_empty, plaintext2html, DEFAULT_SERVER_DATETIME_FORMAT as dtf


class AppointmentExtend(Appointment):

	@http.route(['/calendar/<model("calendar.appointment.type"):appointment_type>/info'], type='http', auth="public",
	            website=True, sitemap=True)
	def calendar_appointment_form(self, appointment_type, employee_id, date_time, duration, **kwargs):
		"""
			Override to change the employee sequence
		"""
		partner = self._get_customer_partner()
		partner_data = partner.read(fields=['name', 'mobile', 'email'])[0] if partner else {}
		day_name = format_datetime(datetime.strptime(date_time, dtf), 'EEE', locale=get_lang(request.env).code)
		date_formated = format_datetime(datetime.strptime(date_time, dtf), locale=get_lang(request.env).code)
		return request.render("appointment.appointment_form", {
			'partner_data': partner_data,
			'appointment_type': appointment_type,
			'main_object': appointment_type,
			'datetime': date_time,
			'datetime_locale': day_name + ' ' + date_formated,
			'datetime_str': date_time,
			'duration_str': duration,
			'employee_id': employee_id,
		})
