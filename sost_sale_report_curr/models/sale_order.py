# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def update_currency_amount(self):
        order_ids = self.env['sale.order'].sudo().search([])
        for order in order_ids:
            untaxed_amount_usd = 0
            usd_currency_id = self.env['res.currency'].sudo().search([('name','=','USD')])
            if usd_currency_id and usd_currency_id.active:
                so_currency_id = order.currency_id
                amount_currency = order.amount_untaxed
                untaxed_amount_usd = so_currency_id._convert(amount_currency, usd_currency_id, order.company_id,order.date_order or fields.Date.today())
            order.untaxed_amount_usd = untaxed_amount_usd

            untaxed_amount_eur = 0
            eur_currency_id = self.env['res.currency'].sudo().search([('name','=','EUR')])
            if eur_currency_id and eur_currency_id.active:
                so_currency_id = order.currency_id
                amount_currency = order.amount_untaxed
                untaxed_amount_eur = so_currency_id._convert(amount_currency, eur_currency_id, order.company_id,order.date_order or fields.Date.today())
            order.untaxed_amount_eur = untaxed_amount_eur

    invoice_no = fields.Char(string="Invoice No",compute="_compute_invoices",store=True)
    untaxed_amount_usd = fields.Float(string="Untaxed Amount USD",compute="_compute_untaxed_amount_usd",store=True)
    untaxed_amount_eur = fields.Float(string="Untaxed Amount EUR",compute="_compute_untaxed_amount_eur",store=True)

    @api.depends('invoice_ids','invoice_ids.state')
    def _compute_invoices(self):
        for order in self:
            invoice_no = ''
            if order.invoice_ids:
                invoice_no = ','.join(inv.name + str(inv.id) if inv.state == 'draft' else inv.name for inv in order.invoice_ids.filtered(lambda x:x.state != 'cancel'))
            order.invoice_no = invoice_no


    @api.depends('amount_untaxed','invoice_ids','invoice_ids.state')
    def _compute_untaxed_amount_usd(self):
        for order in self:
            untaxed_amount_usd = 0
            usd_currency_id = self.env['res.currency'].sudo().search([('name','=','USD')])
            if usd_currency_id and usd_currency_id.active:
                so_currency_id = order.currency_id
                amount_currency = order.amount_untaxed
                untaxed_amount_usd = so_currency_id._convert(amount_currency, usd_currency_id, order.company_id,order.date_order or fields.Date.context_today(self))
            order.untaxed_amount_usd = untaxed_amount_usd

    @api.depends('amount_untaxed','invoice_ids','invoice_ids.state')
    def _compute_untaxed_amount_eur(self):
        for order in self:
            untaxed_amount_eur = 0
            eur_currency_id = self.env['res.currency'].sudo().search([('name','=','EUR')])
            if eur_currency_id and eur_currency_id.active:
                so_currency_id = order.currency_id
                amount_currency = order.amount_untaxed
                untaxed_amount_eur = so_currency_id._convert(amount_currency, eur_currency_id, order.company_id,order.date_order or fields.Date.today())
            order.untaxed_amount_eur = untaxed_amount_eur
            