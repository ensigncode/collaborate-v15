# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime, time
from odoo.exceptions import UserError

class OperationTypeReport(models.TransientModel):
    _name = "operation.type.report"
    _description = "Operation Type Report"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    operation_type_ids = fields.Many2many('stock.picking.type',string="Operation Type")
    state_ids = fields.Many2many('mrp.state',string="State")

    def get_states(self,state_ids):
        states = []
        for state in state_ids:
            states.append(state.state)
        return states

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
            for line in mrp.move_raw_ids:
                vals = {
                    'product_id':mrp.product_id.id,
                    'product_qty':mrp.product_qty,
                    'uom_id':mrp.product_id.uom_id.id,
                    'mrp_date':mrp.date_planned_start.date() or False, 
                    'material_id':line.product_id.id,
                    'consumed_qty':line.product_uom_qty,
                    'material_uom_id':line.product_id.uom_id.id,
                    'mrp_name':mrp.name,
                    'mrp_id':mrp.id,            
                }
                weight = line.product_id.weight * line.product_uom_qty
                weight_uom_name = line.product_id.weight_uom_name
                if weight != 0:
                    weight_uom_name = line.product_id.weight_uom_name
                    vals.update({'weight':str(weight),'weight_uom_name':weight_uom_name})
                
                mrp_report_id = self.env["mrp.report.wizard"].create(vals)
                if mrp_report_id:
                    res_ids.append(mrp_report_id.id)
        if res_ids:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': "mrp.report.wizard",
                'target': 'current',
                'name':'MRP Report',
                'domain': [('id','in',res_ids)],
            }

class MRPReport(models.TransientModel):
    _name = "mrp.report.wizard"
    _description = "MRP Report Wizard"

    product_id = fields.Many2one('product.product',string="Product")
    product_qty = fields.Float(string="Produced Quantity")
    uom_id  = fields.Many2one('uom.uom',string="UOM")
    mrp_date = fields.Date(string="Date")
    material_id = fields.Many2one('product.product',string="Material")
    consumed_qty = fields.Float(string="Consumed Quantity")
    packaging_type_id = fields.Many2one('packaging.type',string="Packaging Type")
    material_uom_id  = fields.Many2one('uom.uom',string="UOM ")
    weight = fields.Char(string="Weight")
    weight_uom_name  = fields.Char(string=" UOM   ")
    mrp_name =  fields.Char(string="MRP")
    mrp_id =  fields.Many2one('mrp.production',string="Production")