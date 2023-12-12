# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
import math
from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import groupby


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    option_type = fields.Selection([('is_modified','Modified'),('is_added','Supplementary')],string="Type")

    def action_create_invoice(self):
        """
            Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != 'to invoice':
                continue
            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            picking_ids = order.picking_ids
            move_ids = picking_ids.mapped('move_ids_without_package')
            extra_move_ids = move_ids.filtered(lambda x:not x.purchase_line_id)
            
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                original_qty = line.product_qty
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        line_vals = pending_section._prepare_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                        sequence += 1
                        pending_section = None
                    line_vals = line._prepare_account_move_line()
                    line_vals.update({'sequence': sequence})
                    if 'quantity' in line_vals and line_vals['quantity']:
                        quantity =  line_vals['quantity']
                        if original_qty != quantity:
                            line_vals.update({'option_type':'is_modified'})
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    sequence += 1
            for move in extra_move_ids:
                line_vals = {
                    'product_id':move.product_id.id,
                    'name':move.product_id.display_name,
                    'quantity':move.product_uom_qty,
                    'price_unit':1,
                    'option_type':'is_added',
                }
                invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
            
            for move in moves:
                account_move_lines = move.invoice_line_ids.filtered(lambda x:x.option_type and x.option_type == 'is_added')
                # for move_line in account_move_lines:
                #     move_line._onchange_product_id()

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()

        return self.action_view_invoice(moves)