# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class MergePOLine(models.Model):
    _name = 'merge.po.line'
    _description = 'Merge PO Line'

    po_ids = fields.Many2many('purchase.order',string="Purchase Order")
    merge_po_ids = fields.One2many('merge.po','merge_po_id')

    @api.model
    def default_get(self,vals):
        res = super(MergePOLine,self).default_get(vals)
        ctx = self.env.context
        active_ids = ctx['active_ids']
        po_ids = self.env['purchase.order'].browse(active_ids)
        merge_pos = []
        for po_id in po_ids.filtered(lambda x:x.state in ('draft','sent')):
            merge_pos.append((0,0,{'po_id':po_id.id,'partner_id':po_id.partner_id.id}))
        res['merge_po_ids'] = merge_pos
        res['po_ids'] = [(6,0,po_ids.ids)]
        return res

    def merge_pos(self):
        partner_ids = self.merge_po_ids.mapped('partner_id')
        for partner in partner_ids:
            po_line_ids = self.merge_po_ids.filtered(lambda x:x.partner_id.id == partner.id)
            po_ids = po_line_ids.mapped('po_id')
            if len(po_ids) > 1:
                last_po_id = po_ids[0]
                for po in po_ids.filtered(lambda x:x.id != last_po_id.id):
                    for line in po.order_line:
                        line.order_id = last_po_id.id
                    po.active = False
        return True


class MergePO(models.Model):
    _name = 'merge.po'
    _description = 'Merge PO'

    po_id = fields.Many2one('purchase.order',string="Purchase Order")
    state = fields.Selection(related="po_id.state")
    partner_id = fields.Many2one('res.partner',string="Vendor")
    merge_po_id = fields.Many2one('merge.po.line',string="Merge PO")
