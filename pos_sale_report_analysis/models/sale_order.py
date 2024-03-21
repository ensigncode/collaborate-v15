from odoo import api, fields, models

class PivotInheritReport(models.Model):
    _inherit = "sale.order.line"

    pos_cashed_in = fields.Float(string='Cashed-in', compute='_compute_pos_cashed', store=True)
    pos_cashed = fields.Boolean(string='Cashed-in', compute='_compute_pos_cashed', store=True)

    @api.depends('pos_order_line_ids.order_id', 'pos_order_line_ids.order_id.state')
    def _compute_pos_cashed(self):
        for line in self:
            order_ids = line.order_id.pos_order_line_ids.order_id.filtered(lambda m: m.state in ('done', 'paid', 'invoiced'))
            amount = sum(order_ids.mapped('amount_paid')) 
            line_id = self.env['sale.order.line'].search([('order_id', '=', line.order_id.id), ('pos_cashed', '=', True)])
            if line_id:
                line_id.pos_cashed_in = amount
                line_id.pos_cashed = True
            else:
                line.pos_cashed_in = amount
                line.pos_cashed = True
