from odoo import fields, models,api

class GenerateReport(models.TransientModel):
    _name= "generate.report"
    _description = "Download xlsx report generate"

    def generate_report_wizard(self):
        for obj in self:
            sale_ids = self.env['sale.order'].search([])
            order_report_ids = self.env['order.report'].search([])
            order_report_ids.unlink()
            for sale in sale_ids:
                purchase_id = sale.order_line.purchase_line_ids.filtered(lambda a: a.order_id.state == 'purchase')
                purchase_ids = sale._get_purchase_orders()
                invoice_ids = sale.invoice_ids
                picking_id = sale.picking_ids
                so_total = sum(line.price_unit * line.product_uom_qty for line in sale.order_line)
                qty_total = sum(line.product_uom_qty for line in sale.order_line)
                po_found = False
                freight = sale.freight
                if invoice_ids:
                    for invoice in invoice_ids:
                        if purchase_ids:
                            for purchase in purchase_ids:
                                self.env['order.report'].create({
                                    'sale_id': sale.id,
                                    'purchase_id':purchase.id,
                                    'invoice_id': invoice.id if invoice else False,
                                    'date':sale.date_order.date(),
                                    'booking':sale.booking,
                                    'truck_nm':sale.truck_nm,
                                    'vendor_id':purchase.partner_id.id,
                                    'partner_id':sale.partner_id.id,
                                    'delivery_id':sale.partner_shipping_id.id if sale.partner_shipping_id else False,
                                    'incoterms': invoice.invoice_incoterm_id.id if invoice and invoice.invoice_incoterm_id else False,
                                    'port_id':sale.port_id.id if sale.port_id else False,
                                    'price':so_total / qty_total,
                                    'amount':so_total,
                                    'etd':sale.expected_date.date() if sale.expected_date else False,
                                    'eta':sale.effective_date or False,
                                    'boxes':qty_total,
                                    'freight':freight,
                                    'percentage':1,
                                })
                        else:
                            self.env['order.report'].create({
                                    'sale_id': sale.id,
                                    'invoice_id': invoice.id if invoice else False,
                                    'date':sale.date_order.date(),
                                    'booking':sale.booking,
                                    'truck_nm':sale.truck_nm,
                                    'partner_id':sale.partner_id.id,
                                    'delivery_id':sale.partner_shipping_id.id if sale.partner_shipping_id else False,
                                    'incoterms': invoice.invoice_incoterm_id.id if invoice and invoice.invoice_incoterm_id else False,
                                    'port_id':sale.port_id.id if sale.port_id else False,
                                    'price':so_total / qty_total,
                                    'amount':so_total,
                                    'etd':sale.expected_date.date() if sale.expected_date else False,
                                    'eta':sale.effective_date or False,
                                    'boxes':qty_total,
                                    'freight':freight,
                                    'percentage':1,
                                })
                elif not invoice_ids:
                    if purchase_ids:
                        for purchase in purchase_ids:
                            self.env['order.report'].create({
                                'sale_id': sale.id,
                                'purchase_id':purchase.id,
                                'date':sale.date_order.date(),
                                'booking':sale.booking,
                                'truck_nm':sale.truck_nm,
                                'vendor_id':purchase.partner_id.id,
                                'partner_id':sale.partner_id.id,
                                'delivery_id':sale.partner_shipping_id.id if sale.partner_shipping_id else False,
                                'port_id':sale.port_id.id if sale.port_id else False,
                                'price':so_total / qty_total,
                                'amount':so_total,
                                'etd':sale.expected_date.date() if sale.expected_date else False,
                                'eta':sale.effective_date or False,
                                'boxes':qty_total,
                                'freight':freight,
                                'percentage':1,
                            })
                    else:
                        self.env['order.report'].create({
                                'sale_id': sale.id,
                                'date':sale.date_order.date(),
                                'booking':sale.booking,
                                'truck_nm':sale.truck_nm,
                                'partner_id':sale.partner_id.id,
                                'delivery_id':sale.partner_shipping_id.id if sale.partner_shipping_id else False,
                                'port_id':sale.port_id.id if sale.port_id else False,
                                'price':so_total / qty_total,
                                'amount':so_total,
                                'etd':sale.expected_date.date() if sale.expected_date else False,
                                'eta':sale.effective_date or False,
                                'boxes':qty_total,
                                'freight':freight,
                                'percentage':1,
                            })
                else:
                    self.env['order.report'].create({
                            'sale_id': sale.id,
                            'date':sale.date_order.date(),
                            'booking':sale.booking,
                            'truck_nm':sale.truck_nm,
                            'partner_id':sale.partner_id.id,
                            'delivery_id':sale.partner_shipping_id.id if sale.partner_shipping_id else False,
                            'port_id':sale.port_id.id if sale.port_id else False,
                            'price':so_total / qty_total,
                            'amount':so_total,
                            'etd':sale.expected_date.date() if sale.expected_date else False,
                            'eta':sale.effective_date or False,
                            'boxes':qty_total,
                            'freight':freight,
                            'percentage':1,
                        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'order.report',
            'view_mode': 'tree',
            'target': 'current',
        }


class OrderReport(models.TransientModel):
    _name= "order.report"
    _description = "Download xlsx report order"

    sale_id = fields.Many2one('sale.order',string='Sale Order')
    purchase_id = fields.Many2one('purchase.order',string='Purchase Order')
    invoice_id = fields.Many2one('account.move','Invoice')
    date = fields.Date('Date')
    booking = fields.Char('Booking')
    truck_nm = fields.Char('Truck')
    vendor_id = fields.Many2one('res.partner',string='Vendor')
    partner_id = fields.Many2one('res.partner',string='Customer')
    delivery_id = fields.Many2one('res.partner',string='Delivery')
    port_id = fields.Many2one('res.port','Port')
    boxes = fields.Integer('Boxes')
    price = fields.Float('Price')
    amount = fields.Float('Amount')
    incoterms = fields.Many2one('account.incoterms','Incoterms')
    freight = fields.Float('Freight')
    etd = fields.Date('ETD')
    eta = fields.Date('ETA')
    percentage = fields.Float('Percentage')
    profit = fields.Integer('Profit')
    claims = fields.Integer('Claims')

