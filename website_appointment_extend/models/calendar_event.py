# -*- coding: utf-8 -*-

from odoo import fields, models,api


class AppointmentReason(models.Model) :
    _name= "appointment.reason"

    name = fields.Char(string="Name")


class CalendarEventInherit(models.Model):

    _inherit = "calendar.event"

    appointment_reason_ids = fields.Many2many('appointment.reason', string="Appointment Reason", translate=True)
    appointment_reason_names = fields.Char(string='Appointment reason Names',
                                           compute='_compute_appointment_reason_names', store=True, translate=True)

    
    @api.model
    def _get_custom_fields(self):
        res = super(CalendarEventInherit,self)._get_custom_fields()
        res.add('appointment_reason_ids')
        res.add('appointment_reason_names')
        return res

    @api.depends('appointment_reason_ids')
    def _compute_appointment_reason_names(self):
        for record in self:
            record.appointment_reason_names = ', '.join(record.appointment_reason_ids.mapped('name'))
