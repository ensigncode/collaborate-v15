# -*- coding: utf-8 -*-

from odoo.addons.appointment.controllers.main import Appointment
from odoo import http, _, fields
from babel.dates import format_datetime, format_date
from datetime import datetime
from odoo.tools.misc import get_lang
from odoo.http import request
from odoo.tools import html2plaintext, is_html_empty, plaintext2html, DEFAULT_SERVER_DATETIME_FORMAT as dtf
from odoo.addons.base.models.ir_ui_view import keep_query
import pytz
from dateutil.relativedelta import relativedelta
from werkzeug.exceptions import NotFound
from odoo.addons.http_routing.models.ir_http import slug
import json


class AppointmentExtend(Appointment):

	@http.route([
		'/calendar/<model("calendar.appointment.type"):appointment_type>',
	], type='http', auth="public", website=True, sitemap=True)
	def calendar_appointment_type(self, appointment_type, filter_employee_ids=None, timezone=None, state=False,
	                              **kwargs):
		"""
			Override to handle the screening, of the months available
		"""
		appointment_type = appointment_type.sudo()
		request.session['timezone'] = timezone or appointment_type.appointment_tz
		try:
			filter_employee_ids = json.loads(filter_employee_ids) if filter_employee_ids else []
		except json.decoder.JSONDecodeError:
			raise ValueError()

		if appointment_type.assign_method == 'chosen' and not filter_employee_ids:
			suggested_employees = appointment_type.employee_ids
		else:
			suggested_employees = appointment_type.employee_ids.filtered(lambda emp: emp.id in filter_employee_ids)
		# Keep retrocompatibility with the the old personnal link ?employee_id=
		employee_id = kwargs.get('employee_id')
		if not suggested_employees and employee_id and int(employee_id) in appointment_type.employee_ids.ids:
			suggested_employees = request.env['hr.employee'].sudo().browse(int(employee_id))

		default_employee = suggested_employees[0] if suggested_employees else request.env['hr.employee']
		slots = appointment_type._get_appointment_slots(request.session['timezone'], default_employee)
		formated_days = [
			format_date(fields.Date.from_string('2021-03-0%s' % str(day + 1)), "EEE", get_lang(request.env).code) for
			day in range(7)]

		assigned_class_calendar = False
		for slot in slots:
			if not assigned_class_calendar and all(len(day['slots']) == 0 for week in slot['weeks'] for day in week):
				slot['calendar_class'] = 'd-none'
				assigned_class_calendar = True
			else:
				slot['calendar_class'] = ''
		if not assigned_class_calendar:
			for hide_Slot in slots[1::]:
				hide_Slot['calendar_class'] = 'd-none'

		return request.render("appointment.appointment_info", {
			'appointment_type': appointment_type,
			'suggested_employees': suggested_employees,
			'main_object': appointment_type,
			'timezone': request.session['timezone'],
			'slots': slots,
			'state': state,
			'filter_appointment_type_ids': kwargs.get('filter_appointment_type_ids'),
			'formated_days': formated_days,
		})

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

	@http.route(['/calendar/<model("calendar.appointment.type"):appointment_type>/submit'], type='http', auth="public",
	            website=True, methods=["POST"])
	def calendar_appointment_submit(self, appointment_type, datetime_str, duration_str, employee_id, name, phone, email,
	                                **kwargs):
		"""
			Override this method to pass context and make sure that the appointment will be booked
			 even if the availability is not there for the employee
		"""
		timezone = request.session['timezone'] or appointment_type.appointment_tz
		tz_session = pytz.timezone(timezone)
		date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc)
		duration = float(duration_str)
		date_end = date_start + relativedelta(hours=duration)
		# check availability of the employee again (in case someone else booked while the client was entering the form)
		employee = request.env['hr.employee'].sudo().browse(int(employee_id)).exists()
		if employee not in appointment_type.sudo().employee_ids:
			raise NotFound()
		# Fetch next employee which is available
		available_employee = appointment_type.sudo().employee_ids.filtered(
			lambda e: e.user_partner_id.with_context(
				employee_appointment_limit=appointment_type.employee_appointment_limit).calendar_verify_availability(
				date_start, date_end)
		)

		if not available_employee:
			return request.redirect('/calendar/%s/appointment?state=failed-employee' % slug(appointment_type))

		Partner = self._get_customer_partner() or request.env['res.partner'].sudo().search([('email', '=like', email)],
		                                                                                   limit=1)
		if Partner:
			if not Partner.with_context(
					employee_appointment_limit=appointment_type.employee_appointment_limit).calendar_verify_availability(
				date_start, date_end):
				return request.redirect('/calendar/%s/appointment?state=failed-partner' % appointment_type.id)
			if not Partner.mobile:
				Partner.write({'mobile': phone})
			if not Partner.email:
				Partner.write({'email': email})
		else:
			Partner = Partner.create({
				'name': name,
				'mobile': Partner._phone_format(phone, country=self._get_customer_country()),
				'email': email,
			})

		description_bits = []
		description = ''

		if phone:
			description_bits.append(_('Mobile: %s', phone))
		if email:
			description_bits.append(_('Email: %s', email))

		for question in appointment_type.question_ids:
			key = 'question_' + str(question.id)
			if question.question_type == 'checkbox':
				answers = question.answer_ids.filtered(lambda x: (key + '_answer_' + str(x.id)) in kwargs)
				if answers:
					description_bits.append('%s: %s' % (question.name, ', '.join(answers.mapped('name'))))
			elif question.question_type == 'text' and kwargs.get(key):
				answers = [line for line in kwargs[key].split('\n') if line.strip()]
				description_bits.append('%s:<br/>%s' % (question.name, plaintext2html(kwargs.get(key).strip())))
			elif kwargs.get(key):
				description_bits.append('%s: %s' % (question.name, kwargs.get(key).strip()))
		if description_bits:
			description = '<ul>' + ''.join(['<li>%s</li>' % bit for bit in description_bits]) + '</ul>'

		# FIXME AWA/TDE double check this and/or write some tests to ensure behavior
		# The 'mail_notify_author' is only placed here and not in 'calendar.attendee#_send_mail_to_attendees'
		# Because we only want to notify the author in the context of Online Appointments
		# When creating a meeting from your own calendar in the backend, there is no need to notify yourself
		event = request.env['calendar.event'].with_context(
			mail_notify_author=True,
			allowed_company_ids=employee.user_id.company_ids.ids,
		).sudo().create(
			self._prepare_calendar_values(appointment_type, date_start, date_end, duration, description, name, employee,
			                              Partner)
		)
		event.attendee_ids.write({'state': 'accepted'})
		return request.redirect(
			'/calendar/view/%s?partner_id=%s&%s' % (event.access_token, Partner.id, keep_query('*', state='new')))
