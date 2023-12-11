# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime, time
from odoo.exceptions import UserError
from collections import defaultdict
from odoo.tools import float_round
import ast


class MRPConsumeReport(models.TransientModel):
    _name = "mrp.consume.report"
    _description = "MRP Consume Report"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    operation_type_ids = fields.Many2many('stock.picking.type',string="Operation Type")
    state_ids = fields.Many2many('mrp.status',string="State")

    def get_states(self,state_ids):
        states = []
        for state in state_ids:
            states.append(state.state)
            if state.state == 'confirmed':
                states.append('progress')
        return states

    def get_lines(self, productions):
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        res = []
        currency_table = self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}})
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            total_cost = 0.0
            # variables to calc cost share (i.e. between products/byproducts) since MOs can have varying distributions
            total_cost_by_mo = defaultdict(float)
            component_cost_by_mo = defaultdict(float)
            operation_cost_by_mo = defaultdict(float)

            # Get operations details + cost
            operations = []
            Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
            if Workorders:
                query_str = """SELECT
                                    wo.production_id,
                                    wo.id,
                                    op.id,
                                    wo.name,
                                    partner.name,
                                    sum(t.duration),
                                    CASE WHEN wo.costs_hour = 0.0 THEN wc.costs_hour ELSE wo.costs_hour END AS costs_hour,
                                    currency_table.rate
                                FROM mrp_workcenter_productivity t
                                LEFT JOIN mrp_workorder wo ON (wo.id = t.workorder_id)
                                LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id)
                                LEFT JOIN res_users u ON (t.user_id = u.id)
                                LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                LEFT JOIN mrp_routing_workcenter op ON (wo.operation_id = op.id)
                                LEFT JOIN {currency_table} ON currency_table.company_id = t.company_id
                                WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                GROUP BY wo.production_id, wo.id, op.id, wo.name, wc.costs_hour, partner.name, t.user_id, currency_table.rate
                                ORDER BY wo.name, partner.name
                            """.format(currency_table=currency_table,)
                self.env.cr.execute(query_str, (tuple(Workorders.ids), ))
                for mo_id, dummy_wo_id, op_id, wo_name, user, duration, cost_hour, currency_rate in self.env.cr.fetchall():
                    cost = duration / 60.0 * cost_hour * currency_rate
                    total_cost_by_mo[mo_id] += cost
                    operation_cost_by_mo[mo_id] += cost
                    operations.append([user, op_id, wo_name, duration / 60.0, cost_hour * currency_rate])

            # Get the cost of raw material effectively used
            raw_material_moves = []
            query_str = """SELECT
                                sm.product_id,
                                mo.id,
                                abs(SUM(svl.quantity)),
                                abs(SUM(svl.value)),
                                currency_table.rate
                             FROM stock_move AS sm
                       INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
                       LEFT JOIN mrp_production AS mo on sm.raw_material_production_id = mo.id
                       LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                            WHERE sm.raw_material_production_id in %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
                         GROUP BY sm.product_id, mo.id, currency_table.rate""".format(currency_table=currency_table,)
            self.env.cr.execute(query_str, (tuple(mos.ids), ))
            for product_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
                cost *= currency_rate
                raw_material_moves.append({
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                })
                total_cost_by_mo[mo_id] += cost
                component_cost_by_mo[mo_id] += cost
                total_cost += cost

            # Get the cost of scrapped materials
            scraps = StockMove.search([('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])

            # Get the byproducts and their total + avg per uom cost share amounts
            total_cost_by_product = defaultdict(float)
            qty_by_byproduct = defaultdict(float)
            qty_by_byproduct_w_costshare = defaultdict(float)
            component_cost_by_product = defaultdict(float)
            operation_cost_by_product = defaultdict(float)
            # tracking consistent uom usage across each byproduct when not using byproduct's product uom is too much of a pain
            # => calculate byproduct qtys/cost in same uom + cost shares (they are MO dependent)
            byproduct_moves = mos.move_byproduct_ids.filtered(lambda m: m.state != 'cancel')
            for move in byproduct_moves:
                qty_by_byproduct[move.product_id] += move.product_qty
                # byproducts w/o cost share shouldn't be included in cost breakdown
                if move.cost_share != 0:
                    qty_by_byproduct_w_costshare[move.product_id] += move.product_qty
                    cost_share = move.cost_share / 100
                    total_cost_by_product[move.product_id] += total_cost_by_mo[move.production_id.id] * cost_share
                    component_cost_by_product[move.product_id] += component_cost_by_mo[move.production_id.id] * cost_share
                    operation_cost_by_product[move.product_id] += operation_cost_by_mo[move.production_id.id] * cost_share

            # Get product qty and its relative total + avg per uom cost share amount
            uom = product.uom_id
            mo_qty = 0
            for m in mos:
                cost_share = float_round(1 - sum(m.move_finished_ids.mapped('cost_share')) / 100, precision_rounding=0.0001)
                total_cost_by_product[product] += total_cost_by_mo[m.id] * cost_share
                component_cost_by_product[product] += component_cost_by_mo[m.id] * cost_share
                operation_cost_by_product[product] += operation_cost_by_mo[m.id] * cost_share
                qty = sum(m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped('product_uom_qty'))
                if m.product_uom_id.id == uom.id:
                    mo_qty += qty
                else:
                    mo_qty += m.product_uom_id._compute_quantity(qty, uom)
            res.append({
                'product': product,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'operations': operations,
                'currency': self.env.company.currency_id,
                'raw_material_moves': raw_material_moves,
                'total_cost': total_cost,
                'scraps': scraps,
                'mocount': len(mos),
                'byproduct_moves': byproduct_moves,
                'component_cost_by_product': component_cost_by_product,
                'operation_cost_by_product': operation_cost_by_product,
                'qty_by_byproduct': qty_by_byproduct,
                'qty_by_byproduct_w_costshare': qty_by_byproduct_w_costshare,
                'total_cost_by_product': total_cost_by_product
            })
        return res



    def action_confirm(self):
        start_date = datetime.combine(self.start_date, time.min)
        end_date = datetime.combine(self.end_date, time.max)
        state_ids = self.state_ids
        states = self.get_states(state_ids)
        domain = [('date_planned_start','>',start_date),
                ('date_planned_start','<',end_date),
                ('picking_type_id','in',self.operation_type_ids.ids),
                ('state','in',states)]
        mrp_ids = self.env['mrp.production'].search(domain)
        if not mrp_ids:
            raise UserError(_('No record found.'))
        data = []
        res_ids = []
        for mrp in mrp_ids:
            values = self.get_lines(mrp)
            if values and len(values) > 0:
                mrp_vals = values[0]
                if 'raw_material_moves' in mrp_vals and mrp_vals['raw_material_moves']:
                    raw_material_moves = mrp_vals['raw_material_moves']
                    new_raw_material_moves = {}
                    currency_id = False
                    if 'currency' in mrp_vals and mrp_vals['currency']:
                        currency_id = mrp_vals['currency']
                        currency_id = currency_id.id 
                    for r_move in raw_material_moves:
                        product_id = r_move['product_id']
                        qty =    r_move['qty']
                        new_key = str(product_id.id) + '_' + str(qty)
                        new_raw_material_moves.update({new_key:r_move})
                    for line in mrp.move_raw_ids:
                        product_id = line.product_id
                        qty =    line.product_uom_qty
                        new_key = str(product_id.id) + '_' + str(qty)
                        cost_value = 0 
                        unit_price = 0
                        if new_key and new_key in new_raw_material_moves:
                            line_raw_material_moves = new_raw_material_moves[new_key]
                            if 'cost' in line_raw_material_moves:
                                cost_value = line_raw_material_moves['cost']
                            if 'qty' in line_raw_material_moves and cost_value:
                                unit_price =  cost_value / line_raw_material_moves['qty']
                            
                            if not unit_price:
                                unit_price = line.price_unit

                        if mrp.state == 'done':
                            producting_qty = mrp.product_qty
                        else:
                            producting_qty = mrp.qty_producing
                        vals = {
                            'origin':mrp.origin,
                            'producting_qty':producting_qty,
                            'company_id':mrp.company_id.id,
                            'src_location_id':line.location_id.id,
                            'scheduled_date':mrp.date_planned_start.date() or False,
                            'mrp_name':mrp.name,
                            'product_code':mrp.product_id.default_code,
                            'product_id':mrp.product_id.name,
                            'material_code':line.product_id.default_code,
                            'material_id':line.product_id.name,
                            'material_uom_id':line.product_id.uom_id.id,
                            'consumed_qty':line.product_uom_qty,
                            'mrp_id':mrp.id,
                            'unit_price':unit_price,
                            'cost_value':cost_value, 
                            'currency_id':currency_id,
                        }
                        mrp_report_id = self.env["mrp.consume"].create(vals)
                        if mrp_report_id:
                            res_ids.append(mrp_report_id.id)
        if res_ids:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': "mrp.consume",
                'target': 'current',
                'name':'MRP Consumption',
                'domain': [('id','in',res_ids)],
            }

class MRPConsume(models.TransientModel):
    _name = "mrp.consume"
    _description = "MRP Consume"

    company_id = fields.Many2one('res.company',string="Company")
    src_location_id = fields.Many2one('stock.location',string="From Location")
    scheduled_date = fields.Date(string="Scheduled Date")
    mrp_name = fields.Char(string="MRP")
    origin = fields.Char(string="Source")
    product_code = fields.Char(string="Product Code")
    product_id = fields.Char(string="Product")
    product_qty = fields.Float(string="Produced Qty")
    material_id = fields.Char(string="Material")
    material_code = fields.Char(string="Material Code")
    material_uom_id  = fields.Many2one('uom.uom',string="UOM ")
    mrp_id = fields.Many2one('mrp.production',string="MRP")
    consumed_qty = fields.Float(string="Consumed Qty")
    producting_qty = fields.Float(string="Producing Qty")
    unit_price = fields.Float(string="Unit Price")
    cost_value = fields.Float(string="Cost Value")
    currency_id  = fields.Many2one('res.currency',string="Currency")
