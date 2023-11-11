# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta, time
import random
import pytz
from functools import reduce
import logging
from babel.dates import format_datetime
from dateutil.relativedelta import relativedelta
import calendar as cal

from odoo.tools.misc import get_lang

_logger = logging.getLogger(__name__)


class CalendarAppointmentType(models.Model):
	_inherit = "calendar.appointment.type"

	employee_appointment_limit = fields.Integer(string="Employee's Appointment Limit")

	def _slots_available(self, slots, first_day, last_day, employee=None):
		"""
			Override the method to check the slots available for the given slots
		"""

		def is_work_available(start_dt, end_dt, intervals):
			""" check if the slot is contained in the employee's work hours (defined by intervals)
			"""

			def find_start_index():
				""" find the highest index of intervals for which the start_date (element [0]) is before (or at) start_dt
				"""

				def recursive_find_index(lower_bound, upper_bound):
					if upper_bound - lower_bound <= 1:
						if intervals[upper_bound][0] <= start_dt:
							return upper_bound
						return lower_bound
					index = (upper_bound + lower_bound) // 2
					if intervals[index][0] <= start_dt:
						return recursive_find_index(index, upper_bound)
					else:
						return recursive_find_index(lower_bound, index)

				if start_dt <= intervals[0][0] - tolerance:
					return -1
				if end_dt >= intervals[-1][1] + tolerance:
					return -1
				return recursive_find_index(0, len(intervals) - 1)

			if not intervals:
				return False

			tolerance = timedelta(minutes=1)
			start_index = find_start_index()
			if start_index != -1:
				for index in range(start_index, len(intervals)):
					if intervals[index][1] >= end_dt - tolerance:
						return True
					if len(intervals) == index + 1 or intervals[index + 1][0] - intervals[index][1] > tolerance:
						return False
			return False

		workhours = {}
		meetings = {}

		# With context will be used in resource.calendar to force the referential user
		# for work interval computing to the *user linked to the employee*
		available_employees = [emp.with_context(tz=emp.user_id.tz) for emp in (employee or self.employee_ids)]
		random.shuffle(available_employees)

		for slot in slots:
			if available_employees:
				workhours[0] = [
					(interval[0].astimezone(pytz.UTC).replace(tzinfo=None),
					 interval[1].astimezone(pytz.UTC).replace(tzinfo=None))
					for key, interval_obj in available_employees[0].resource_calendar_id._work_intervals_batch(
						first_day, last_day, resources=[employee.resource_id for employee in
						                                [emp.with_context(tz=emp.user_id.tz) for emp in
						                                 self.employee_ids]],
						# first_day, last_day, resources=[employee.resource_id for employee in available_employees],
					).items()
					for interval in interval_obj
				]

				if is_work_available(slot['UTC'][0], slot['UTC'][1], workhours[0]):
					if 0 not in meetings:
						# note: no check is made on the attendee's status (accepted/declined/...)
						events = self.env['calendar.event'].search([
							('partner_ids.user_ids', 'in', [empl.user_id.id for empl in available_employees]),
							('start', '<', fields.Datetime.to_string(last_day.replace(hour=23, minute=59, second=59))),
							('stop', '>', fields.Datetime.to_string(first_day.replace(hour=0, minute=0, second=0)))
						])
						if len(events) >= self.employee_appointment_limit:
							meetings[0] = events

					if not slot.get('employee_id'):
						for emp in available_employees:
							if emp.user_partner_id.with_context(
									employee_appointment_limit=self.employee_appointment_limit).calendar_verify_availability(
								slot['UTC'][0], slot['UTC'][1]):
								slot['employee_id'] = emp
								break

	def _slots_generate(self, first_day, last_day, timezone, reference_date=None):
		"""
		Override to filter out slots if any employees are not available
		:param first_day: First day of the slot
		:param last_day: Last day of the slot
		:param timezone: TimeZone
		:param reference_date: Ref Date
		:return: Slots
		"""
		slots = super(CalendarAppointmentType, self)._slots_generate(first_day, last_day, timezone, reference_date)
		available_employees = [emp.with_context(tz=emp.user_id.tz) for emp in self.employee_ids]

		def is_slot_available(slot, next_employee_id):
			"""
			Return Slot If it's available in the slot's timeframe
			:param slot: Slot, Next employee id
			:return: Updated slots
			"""
			partner_ids = reduce(lambda x, y: x.union(y), [em.user_partner_id for em in next_employee_id])
			# partner_ids = reduce(lambda x, y: x.union(y), [em.user_partner_id for em in available_employees])
			return partner_ids.with_context(
				employee_appointment_limit=self.employee_appointment_limit,
				available_employees=next_employee_id).calendar_verify_same_slot_availability(
				slot['UTC'][0], slot['UTC'][1]
			), next_employee_id

		events = self.env['calendar.event'].search([('appointment_type_id', '=', self.id)], order="id desc")
		if events:
			last_event_employee_id = self.employee_ids.filtered(lambda e: e.user_id.id == events[0].user_id.id)
			if last_event_employee_id:
				last_event_employee_id = last_event_employee_id[0]
				employee_index = (available_employees.index(last_event_employee_id) + 1) % len(available_employees)
				next_employee_id = available_employees[employee_index]
			else:
				next_employee_id = available_employees and available_employees[0] or self.env['hr.employee']
		else:
			next_employee_id = available_employees and available_employees[0] or self.env['hr.employee']

		# Slot filtration by employee if available for the selected slot
		slots = list(map(
			lambda sl: {**sl} if sl[timezone][0] < first_day else {
				**sl, 'employee_id': self._set_employee_id(sl, timezone, is_slot_available(sl, next_employee_id))},
			slots
		))
		# Filter out those slots which have no employee's assigned
		slots = list(filter(
			lambda sl: sl.get('employee_id', False), slots
		))
		return slots

	def _set_employee_id(self, slot, timezone, avail_employee_id):
		"""
		Set the employee based on the availability of employee
		"""
		slot_employee_id = self.env['hr.employee']
		timezone = slot[timezone]
		is_available, employee_id = avail_employee_id
		employee_attendance = [
			d for d in employee_id.resource_calendar_id.attendance_ids if str(timezone[0].weekday()) == d.dayofweek
		]
		if is_available and employee_attendance:
			working_hour = [
				range(int(attendance.hour_from), int(attendance.hour_to)) for attendance in employee_attendance
			]
			is_employee_available = [True for hour in working_hour if timezone[0].hour in hour]
			slot_employee_id = employee_id if any(is_employee_available) else slot_employee_id
		return slot_employee_id

	def _get_appointment_slots(self, timezone, employee=None, reference_date=None):
		# Override method for filter out appointment slot based on employee working hours.
		""" Fetch available slots to book an appointment.

		:param str timezone: timezone string e.g.: 'Europe/Brussels' or 'Etc/GMT+1'
		:param <hr.employee> employee: if set will only check available slots for
		  this employee. Otherwise employee_ids fields is used to fetch availability;
		:param datetime reference_date: starting datetime to fetch slots. If not
		  given now (in UTC) is used instead. Note that minimum schedule hours
		  defined on appointment type is added to the beginning of slots;

		:returns: list of dicts (1 per month) containing available slots per week
		  and per day for each week (see ``_slots_generate()``), like
		  [
			{'id': 0,
			 'month': 'February 2022' (formatted month name),
			 'weeks': [
				[{'day': ''}],
				[{...}],
			 ],
			},
			{'id': 1,
			 'month': 'March 2022' (formatted month name),
			 'weeks': [ (...) ],
			},
			{...}
		  ]
		"""
		self.ensure_one()
		if not reference_date:
			reference_date = datetime.utcnow()

		appt_tz = pytz.timezone(self.appointment_tz)
		requested_tz = pytz.timezone(timezone)
		first_day = requested_tz.fromutc(reference_date + relativedelta(hours=self.min_schedule_hours))
		appointment_duration_days = self.max_schedule_days
		unique_slots = self.slot_ids.filtered(lambda slot: slot.slot_type == 'unique')
		if self.category == 'custom' and unique_slots:
			appointment_duration_days = (unique_slots[-1].end_datetime.date() - reference_date.date()).days
		last_day = requested_tz.fromutc(reference_date + relativedelta(days=appointment_duration_days))

		# Compute available slots (ordered)
		slots = self._slots_generate(
			first_day.astimezone(appt_tz),
			last_day.astimezone(appt_tz),
			timezone,
			reference_date=reference_date
		)

		# Commented these lines because we didn't want to filter the slots based on the employee's work schedule here
		# if not employee or employee in self.employee_ids:
		#     self._slots_available(slots, first_day.astimezone(pytz.UTC), last_day.astimezone(pytz.UTC), employee)

		# Compute calendar rendering and inject available slots
		today = requested_tz.fromutc(reference_date)
		start = today
		month_dates_calendar = cal.Calendar(0).monthdatescalendar
		months = []
		while (start.year, start.month) <= (last_day.year, last_day.month):
			dates = month_dates_calendar(start.year, start.month)
			for week_index, week in enumerate(dates):
				for day_index, day in enumerate(week):
					mute_cls = weekend_cls = today_cls = None
					today_slots = []
					if day.weekday() in (cal.SUNDAY, cal.SATURDAY):
						weekend_cls = 'o_weekend'
					if day == today.date() and day.month == today.month:
						today_cls = 'o_today'
					if day.month != start.month:
						mute_cls = 'text-muted o_mute_day'
					else:
						# slots are ordered, so check all unprocessed slots from until > day
						while slots and (slots[0][timezone][0].date() <= day):
							# Get employee working hours for filter out appointment slots.
							# employee_attendace = [d for d in slots[0].get('employee_id', self.env['hr.employee'].browse(1)).resource_calendar_id.attendance_ids if str(day.weekday()) == d.dayofweek]
							# working_hour = [range(int(attendace.hour_from),int(attendace.hour_to)) for attendace in employee_attendace]
							# is_employee_available = [True for hour in working_hour if slots[0][timezone][0].hour in hour]
							if (slots[0][timezone][0].date() == day) and ('employee_id' in slots[0]):
								if slots[0]['slot'].allday:
									today_slots.append({
										'employee_id': slots[0]['employee_id'],
										'datetime': slots[0][timezone][0].strftime('%Y-%m-%d %H:%M:%S'),
										'hours': _("All day"),
										'duration': 24,
									})
								else:
									start_hour = slots[0][timezone][0].strftime('%H:%M')
									end_hour = slots[0][timezone][1].strftime('%H:%M')
									today_slots.append({
										'employee_id': slots[0]['employee_id'].id,
										'datetime': slots[0][timezone][0].strftime('%Y-%m-%d %H:%M:%S'),
										'hours': "%s - %s" % (
										start_hour, end_hour) if self.category == 'custom' else start_hour,
										'duration': str(
											(slots[0][timezone][1] - slots[0][timezone][0]).total_seconds() / 3600),
									})
							else:
								a = 'a'
							slots.pop(0)
					today_slots = sorted(today_slots, key=lambda d: d['hours'])
					dates[week_index][day_index] = {
						'day': day,
						'slots': today_slots,
						'mute_cls': mute_cls,
						'weekend_cls': weekend_cls,
						'today_cls': today_cls
					}

			months.append({
				'id': len(months),
				'month': format_datetime(start, 'MMMM Y', locale=get_lang(self.env).code),
				'weeks': dates,
			})
			start = start + relativedelta(months=1)
		return months
