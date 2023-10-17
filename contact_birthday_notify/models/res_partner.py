# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date 
from dateutil.relativedelta import relativedelta

class Partner(models.Model):
    _inherit = 'res.partner'

    birthday = fields.Date(string="Birthday")
    coupon_id = fields.Many2one('coupon.coupon',string="Coupon")
    coupon_valid_start_date = fields.Date(string="Coupon Valid Start Date")
    coupon_valid_end_date = fields.Date(string="Coupon Valid End Date")

    
    '''
        Cron Job to Send the Birthday greeting mail to employee
    '''
    @api.model
    def contact_birth_notify(self):
        start_date = date.today()
        end_date = date.today() - relativedelta(days=7)
        coupon_valid_start_date = end_date
        domain = [('birthday','<=',start_date),
                ('birthday','>=',end_date),
                ('coupon_id','=',False)]
        partner_ids = self.env['res.partner'].search(domain)
        template_id = self.env.ref('contact_birthday_notify.mail_template_bday_notification')
        coupon_domain = [('discount_type','=','percentage'),('discount_percentage','=',20),('reward_type','=','discount')]
        program_id = self.env['coupon.program'].search(coupon_domain,limit=1)
        if not program_id:
            program_vals = {
                'name':'Birthday Coupon',
                'reward_type':'discount',
                'discount_type':'percentage',
                'discount_percentage':20,
                'validity_duration':0,
            }
            program_id = self.env['coupon.program'].create(program_vals)
        for partner in partner_ids:
            coupon_valid_end_date = partner.birthday +  relativedelta(days=7)
            vals = {'partner_id':partner.id,'program_id': program_id.id}
            sale_coupon_template_id = self.env.ref('sale_coupon.mail_template_sale_coupon')
            coupon = self.env['coupon.coupon'].create(vals)
            subject = _('%s, a coupon has been generated for you') % (partner.name)
            if sale_coupon_template_id:
                email_values = {'email_from': self.env.user.email or '', 'subject': subject}
                template_id.send_mail(coupon.id, email_values=email_values, notif_layout='mail.mail_notification_light')

            partner.update({'coupon_valid_start_date':coupon_valid_start_date,
                            'coupon_valid_end_date':coupon_valid_end_date,
                            'coupon_id':coupon.id})

        contact_coupon_ids = self.env['res.partner'].search([('coupon_valid_end_date','<=',date.today() + relativedelta(days=1))])
        for contact_coupon in contact_coupon_ids.filtered(lambda x:x.coupon_id != False):
            contact_coupon.coupon_id.state = 'expired'
            contact_coupon.update({'coupon_id':False,'coupon_valid_start_date':False,'coupon_valid_end_date':False})
        return True