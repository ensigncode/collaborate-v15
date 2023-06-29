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
            if events >= employee_appointment_limit:
                return False
            return True
        else:
            if bool(events):
                return False
            return True
