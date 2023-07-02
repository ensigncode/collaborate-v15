# -*- coding: utf-8 -*-

from odoo import fields, models


class Partner(models.Model):

    _inherit = "res.partner"

    def calendar_verify_availability(self, date_start, date_end):
        """
            Override to check the limit of employee's appointment
        """
        employee_appointment_limit = self._context.get('employee_appointment_limit', 0)
        events = self.env['calendar.event'].search_count([
            ('partner_ids', 'in', self.ids),
            '|', '&', ('start', '<', fields.Datetime.to_string(date_end)),
                      ('stop', '>', fields.Datetime.to_string(date_start)),
                 '&', ('allday', '=', True),
                      '|', ('start_date', '=', fields.Date.to_string(date_end)),
                           ('start_date', '=', fields.Date.to_string(date_start))])
        if employee_appointment_limit:
            if (events/employee_appointment_limit) >= employee_appointment_limit:
                return False
            return True
        else:
            if bool(events):
                return False
            return True

    def get_available_next_employee(self, available_employees, appointment_type_id):
        """
        Method to get next available employee, ordering by meetings
        :return: Available Partner
        """
        employee_partner_dict = dict(map(lambda avl: (avl.user_partner_id.id, avl), available_employees))
        events = self.env['calendar.event'].search([('appointment_type_id', '=', appointment_type_id.id)])
        partner_wise_meeting = dict(events.mapped(lambda x: (x.partner_id.id, len(events.filtered(lambda ev: ev.partner_id.id == x.id)))))
        sorted_partner_meetings = sorted(partner_wise_meeting.items(), key=lambda x: x[1])
        remaining_employees = dict(filter(
            lambda remp: remp[0] not in list(map(
                lambda spm: spm[0], sorted_partner_meetings
            )), employee_partner_dict.items()))
        if remaining_employees:
            # If any employee is remaining to have a meeting please make that employee as in priority
            return list(remaining_employees.values())[0]
        if sorted_partner_meetings:
            # Get the employee from the partner
            return employee_partner_dict.get(sorted_partner_meetings[0][0])
        else:
            return available_employees[0]
