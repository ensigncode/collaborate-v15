# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    subscribed_to_newsletter = fields.Boolean(string="Subscribed To Newsletter?",
                                              default=False,
                                              help="If it's checked then user will be subscribed for Newsletter.")
    subscribed_to_sms = fields.Boolean(string="Subscribed To SMS?",
                                       default=False,
                                       help="If it's checked then user will be subscribed for SMS.")
    account_deleted = fields.Boolean(string="Account Deleted", default=False)
