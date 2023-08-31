# -*- coding: utf-8 -*-

from odoo import fields, models,api


class AppointmentReason(models.Model):
    _name= "appointment.status"

    name = fields.Char(string="Name", translate=True)


class CalendarEventInherit(models.Model):

    _inherit = "calendar.event"

    appointment_status_id = fields.Many2one('appointment.status', string="Appointment Reason")
    
    @api.model
    def _get_custom_fields(self):
        res = super(CalendarEventInherit,self)._get_custom_fields()
        res.add('appointment_status_id')
        return res
