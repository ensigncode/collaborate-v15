# -*- coding: utf-8 -*-

from odoo import fields, models


class Partner(models.Model):

    _inherit = "res.partner"

    def calendar_verify_availability(self, date_start, date_end):
        """
            Override to check the limit of employee's appointment
        """
        employee_appointment_limit = self._context.get('employee_appointment_limit', 0)
        available_employees = self._context.get('available_employees', [False])
        events = self.env['calendar.event'].search_count([
            ('partner_ids', 'in', self.ids),
            '|', '&', ('start', '<', fields.Datetime.to_string(date_end)),
                      ('stop', '>', fields.Datetime.to_string(date_start)),
                 '&', ('allday', '=', True),
                      '|', ('start_date', '=', fields.Date.to_string(date_end)),
                           ('start_date', '=', fields.Date.to_string(date_start))])
        if employee_appointment_limit:
            if events >= (employee_appointment_limit * len(available_employees)):
                return False
            return True
        else:
            if bool(events):
                return False
            return True

    def calendar_verify_same_slot_availability(self, date_start, date_end):
        """
            Check the slot is still available to book appointment
        """
        employee_appointment_limit = self._context.get('employee_appointment_limit', 0)
        available_employees = self._context.get('available_employees', False)
        events = self.env['calendar.event'].search_count([
            ('partner_ids', 'in', self.ids),
            ('start', '=', fields.Datetime.to_string(date_start)),
            ('stop', '=', fields.Datetime.to_string(date_end))
        ])
        if employee_appointment_limit:
            if events < (employee_appointment_limit * len(available_employees)):
                return True
            return False
        return True
