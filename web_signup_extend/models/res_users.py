# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'

    subscribed_to_newsletter = fields.Boolean(string="Subscribed To Newsletter?",
                                              related="partner_id.subscribed_to_newsletter",
                                              help="If it's checked then user will be subscribed for Newsletter.",
                                              store=True)
    subscribed_to_sms = fields.Boolean(string="Subscribed To SMS?",
                                       related="partner_id.subscribed_to_sms",
                                       help="If it's checked then user will be subscribed for SMS.",
                                       store=True)