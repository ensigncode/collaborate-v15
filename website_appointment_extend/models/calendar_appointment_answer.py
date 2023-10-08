# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CalendarAppointmentAnswer(models.Model):
    _inherit = "calendar.appointment.answer"

    positive_answer = fields.Boolean(string="Positive Answer?")
