# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, time
import random
import pytz
from functools import reduce
import logging

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
                        first_day, last_day, resources=[employee.resource_id for employee in available_employees],
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
                                    employee_appointment_limit=self.employee_appointment_limit).calendar_verify_availability(slot['UTC'][0], slot['UTC'][1]):
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

        def is_slot_available(slot):
            """
            Return Slot If it's available in the slot's timeframe
            :param slot: Slot
            :return: Updated slots
            """
            partner_ids = reduce(lambda x, y: x.union(y), [em.user_partner_id for em in available_employees])
            return partner_ids.with_context(
                    employee_appointment_limit=self.employee_appointment_limit,
                    available_employees=available_employees).calendar_verify_same_slot_availability(
                    slot['UTC'][0], slot['UTC'][1]
                )
        events = self.env['calendar.event'].search([('appointment_type_id', '=', self.id)], order="id desc")
        if events:
            last_event_employee_id = self.employee_ids.filtered(lambda e: e.user_id.id == events[0].user_id.id)
            if last_event_employee_id:
                last_event_employee_id = last_event_employee_id[0]
                employee_index = (available_employees.index(last_event_employee_id) + 1) % len(available_employees)
                next_employee_id = available_employees[employee_index]
            else:
                next_employee_id = available_employees[0]
        else:
            next_employee_id = available_employees[0]
        slots = list(map(
            lambda sl: {**sl} if sl[timezone][0] < first_day else {**sl, 'employee_id': next_employee_id},
            filter(lambda x: is_slot_available(x), slots)
        ))
        return slots
