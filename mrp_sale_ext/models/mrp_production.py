# -*- coding: utf-8 -*-

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.addons.stock.models.stock_rule import ProcurementException

class Production(models.Model):
    _inherit = 'mrp.production'

    @api.depends('origin','state',
                'procurement_group_id',
                'procurement_group_id.mrp_production_ids',
                'procurement_group_id.mrp_production_ids',
                'procurement_group_id.mrp_production_ids.move_dest_ids',
                'procurement_group_id.mrp_production_ids.move_dest_ids.group_id',
                'procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id',
                )
    def _compute_orders(self):
        for production in self:
            order_id = False
            if production.procurement_group_id and production.procurement_group_id.mrp_production_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id and production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id:
                order_id =  production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.id
            
            if not order_id and production.origin:
                origins = production.origin.split('S')
                origin_data = []
                for origin in origins:
                    if origin:
                        order_name = 'S'
                        for letter in origin:
                            if letter.isalnum() and len(order_name) < 6:
                                order_name += letter
                            else:
                                break
                        if order_name:
                            origin_data.append(order_name)
                for ord_name in origin_data:
                    order = self.env['sale.order'].search([('name','=',ord_name)])
                    if order:
                        order_id = order.id
            production.order_id = order_id

    order_id = fields.Many2one('sale.order',compute="_compute_orders",store=True)
    expected_date = fields.Datetime(string="Delivery Date",related='order_id.expected_date',store=True)
    partner_id = fields.Many2one('res.partner',related='order_id.partner_id',store=True)
    initial_qty = fields.Float(string="Initial Quantity")
    client_order_ref =  fields.Char(related='order_id.client_order_ref',store=True)

    @api.model
    def create(self,vals):
        res = super(Production,self).create(vals)
        if res.origin and not res.initial_qty:
            res.initial_qty = res.product_qty
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_manufacture(self, procurements):
        productions_values_by_company = defaultdict(list)
        errors = []
        for procurement, rule in procurements:
            bom = rule._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values)
            if not bom:
                msg = _('There is no Bill of Material of type manufacture or kit found for the product %s. Please define a Bill of Material for this product.') % (procurement.product_id.display_name,)
                errors.append((procurement, msg))
            productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))
        if errors:
            raise ProcurementException(errors)
        for company_id, productions_values in productions_values_by_company.items():
            productions_vals = productions_values[0]
            productions_vals.update({'initial_qty':productions_vals.get('product_qty') or 0.0})
            productions_values = [productions_vals]
            # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            productions = self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(productions_values)
            self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
            self.env['stock.move'].sudo().create(productions._get_moves_finished_values())
            productions._create_workorder()
            productions.filtered(lambda p: not p.orderpoint_id and p.move_raw_ids).action_confirm()

            for production in productions:
                origin_production = production.move_dest_ids and production.move_dest_ids[0].raw_material_production_id or False
                orderpoint = production.orderpoint_id
                if orderpoint:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self': production, 'origin': orderpoint},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
                if origin_production:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self': production, 'origin': origin_production},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
        return True
