# -*- coding: utf-8 -*-

from odoo import  models, fields, api, _
import xml.etree.ElementTree as ET
import base64
import  random
from odoo.exceptions import UserError

class POSSelect(models.Model):
	_name = "pos.select"
	_description = "POS Select"

	name = fields.Char(default="POS Order")
	pos_order_ids = fields.Many2many('pos.order',string="Invoices")

	def get_main_location(self,main_destination_id):
		if main_destination_id:
			count = 0
			while count == 0:
				if main_destination_id.location_id and main_destination_id.location_id.usage == 'internal':
					main_destination_id = main_destination_id.location_id
				elif main_destination_id.location_id and main_destination_id.location_id.usage == 'view':
					main_destination_id = main_destination_id.location_id
					count = 1
				else:
					count = 1
		return main_destination_id


	@api.model
	def default_get(self,vals):
		res = super(POSSelect,self).default_get(vals)
		ctx = self.env.context
		active_ids = ctx['active_ids']
		res['pos_order_ids'] = [(6,0,active_ids)]
		return res

	def action_show_data(self,pos_order_ids):
		pos_order_ids = pos_order_ids
		document_root = ET.Element("Documents")

		pos_id = self.env['ir.sequence'].search([('code','=','pos.order')],limit=1)

		for pos_order in pos_order_ids:
			supplier_id = pos_order.company_id.partner_id
			buyer_id = pos_order.partner_id
			
			# Create child elements and add data
			document = ET.SubElement(document_root, "Document")
			supplier_info = ET.SubElement(document, "SupplierInfo")			

			# Serial Number 
			seria = ET.SubElement(supplier_info, "Seria")
			pos_code = ''
			if pos_id:
				prefix = pos_id.prefix
				for c_prefix in pos_id.prefix:
					if c_prefix.isalnum():
						pos_code += c_prefix
			seria.text = pos_code

			# POS Number
			number = ET.SubElement(supplier_info, "Number")
			number.text = pos_order.name 

			# Issued Date
			issue_date = ET.SubElement(supplier_info, "IssuedDate")
			issue_date.text = pos_order.date_order.date().strftime("%Y-%m-%d") if pos_order.date_order else ''

			# Delivery Date
			delivery_date = ET.SubElement(supplier_info, "DeliveryDate")
			delivery_date.text = pos_order.date_order.date().strftime("%Y-%m-%d") if pos_order.date_order else ''

			# Supplier Address
			IsSupplierOnly = 'false'
			if supplier_id and supplier_id.supplier_rank:
				IsSupplierOnly = 'true'
			supplier_address = supplier_id.street if supplier_id.street else '' + ' ,' + supplier_id.street2 if supplier_id.street else ''  + ' , ' + supplier_id.city if supplier_id.city else ''
			Supplier_BranchTitle = Supplier_BranchCode =  Supplier_Account = ''
			if supplier_id and supplier_id.bank_ids:
				Supplier_BranchTitle = supplier_id.bank_ids[0].bank_id.name
				Supplier_BranchCode = supplier_id.bank_ids[0].bank_id.bic
				Supplier_Account =  supplier_id.bank_ids[0].acc_number

			supplier =  ET.SubElement(supplier_info, "Supplier")
			supplier.set("IDNO", supplier_id.vat or '')
			supplier.set("Title", supplier_id.name or '')
			supplier.set("Address", supplier_address)
			supplier.set("NResident", "false")
			supplier.set("IsSupplierOnly", IsSupplierOnly)
			supplier.set("TaxpayerType", "1")

			bank_account =  ET.SubElement(supplier_info, "BankAccount")
			bank_account.set("BranchTitle",Supplier_BranchTitle)
			bank_account.set("BranchCode", Supplier_BranchCode)
			bank_account.set("Account", Supplier_Account)
			bank_account_manual =  ET.SubElement(bank_account, "IsManual")
			bank_account_manual.text = 'false'
			
			is_registered =  ET.SubElement(supplier_info, "IsRegistered")
			is_registered.text = 'false'

			is_valid =  ET.SubElement(supplier_info, "IsValid")
			is_valid.text = 'false'

			is_liquidated =  ET.SubElement(supplier_info, "IsLiquidated")
			is_liquidated.text = 'false'


			bank_account_legal_person =  ET.SubElement(supplier_info, "IsLegalPerson")
			if supplier_id and supplier_id.company_type == 'company':
				bank_account_legal_person.text = 'true'
			else:
				bank_account_legal_person.text = 'false'

			address = buyer_id.street if buyer_id.street else '' + ' ,' + buyer_id.street2 if buyer_id.street else ''  + ' , ' + buyer_id.city if buyer_id.city else ''
			BranchTitle = BranchCode =  Account = ''
			if buyer_id and buyer_id.bank_ids:
				BranchTitle = buyer_id.bank_ids[0].bank_id.name
				BranchCode = buyer_id.bank_ids[0].bank_id.bic
				Account =  buyer_id.bank_ids[0].acc_number

			buyer =  ET.SubElement(supplier_info, "Buyer")
			buyer.set("IDNO", buyer_id.vat or "")
			buyer.set("Title", buyer_id.name or "")
			buyer.set("Address", address)
			buyer.set("CodTVA", "0612817")
			buyer.set("NResident", "false")
			buyer.set("IsSupplierOnly", "false")
			buyer.set("TaxpayerType", "1")

			bank_account =  ET.SubElement(buyer, "BankAccount")
			bank_account.set("BranchTitle", BranchTitle)
			bank_account.set("BranchCode", BranchCode)
			bank_account.set("Account", Account)

			bank_account_manual =  ET.SubElement(bank_account, "IsManual")
			bank_account_manual.text = 'false'

			bank_account_risk_analysis =  ET.SubElement(buyer, "RiskAnalysisValid")
			bank_account_risk_analysis.text = 'false'

			bank_account_registed =  ET.SubElement(buyer, "IsRegistered")
			bank_account_registed.text = 'false'

			bank_account_valid =  ET.SubElement(buyer, "IsValid")
			bank_account_valid.text = 'false'
			
			bank_account_liquodated =  ET.SubElement(buyer, "IsLiquidated")
			bank_account_liquodated.text = 'false'
			
			bank_account_legal_person =  ET.SubElement(buyer, "IsLegalPerson")
			if buyer_id and buyer_id.company_type == 'company':
				bank_account_legal_person.text = 'true'
			else:
				bank_account_legal_person.text = 'false'


			vehicle_log_book =  ET.SubElement(supplier_info, "VehicleLogbook")
			vehicle_log_book_issue_date =  ET.SubElement(vehicle_log_book, "IssuedDate")
			vehicle_log_book_issue_date.set("xmlns:p3","http://www.w3.org/2001/XMLSchema-instance")
			vehicle_log_book_issue_date.set("p3:nil","true")
			vehicle_log_book_seria =  ET.SubElement(vehicle_log_book, "Seria")
			vehicle_log_book_number =  ET.SubElement(vehicle_log_book, "Number")
			picking_type_id = self.env['stock.picking.type'].search([('sequence_code','=','POS'),('company_id','=',self.env.company.id)],limit=1)
			warehouse_id = False
			if picking_type_id:
				location_src_id = picking_type_id.default_location_src_id
				main_destination_id = self.get_main_location(location_src_id)
				location_name = main_destination_id.name
				warehouse_id = self.env['stock.warehouse'].search([('code','=',location_name)])
			if warehouse_id:
				warehouse_partner_id = warehouse_id.partner_id
				loading_point_text = warehouse_partner_id.street if warehouse_partner_id.street else '' + ' ,' + warehouse_partner_id.street2 if warehouse_partner_id.street else ''  + ' , ' + warehouse_partner_id.city if warehouse_partner_id.city else ''
			else:
				loading_point_text = 'mun.Chisinau, str.Podul Inalt, nr.18/1, of.31'

			loading_point =  ET.SubElement(supplier_info, "LoadingPoint")
			loading_point.text = loading_point_text
			redirections =  ET.SubElement(supplier_info, "Redirections")
			redirections_total =  ET.SubElement(redirections, "Total")
			redirections_total.text = str(pos_order.amount_total) or 0.0 
			redirections_tva =  ET.SubElement(redirections, "TotalTVA")
			redirections_tva.text = str(pos_order.amount_tax) or 0.0
			merchandises =  ET.SubElement(supplier_info, "Merchandises")
			
			for line in pos_order.lines:
				if line.price_unit > line.price_subtotal:
					price_unit = line.price_subtotal
				else:
					price_unit = line.price_unit
				per_unit_tax = 0
				total_tax = line.price_subtotal_incl - line.price_subtotal
				if total_tax and line.qty:
					per_unit_tax = total_tax / line.qty

				# price_unit = pos_order.pricelist_id.get_product_price(line.product_id, line.qty or 1.0, pos_order.partner_id)
				merchandises_row =  ET.SubElement(merchandises, "Row")
				merchandises_row.set('IsManualEdited','true')
				merchandises_row.set('CalculationScenario','-1')
				merchandises_row.set('Code',line.product_id.default_code if line.product_id and line.product_id.default_code else '')
				merchandises_row.set('Name',line.product_id.display_name if line.product_id else '')
				merchandises_row.set('UnitOfMeasure',line.product_uom_id.name if line.product_uom_id else '')
				merchandises_row.set('Quantity',str(line.qty))
				# merchandises_row.set('UnitPriceWithoutTVA',str(line.price_unit) or str(0.0))
				# merchandises_row.set('TotalPriceWithoutTVA',str(line.price_subtotal) or str(0.0))
				merchandises_row.set('UnitPriceWithoutTVA',str(price_unit) or str(0.0))
				merchandises_row.set('TotalPriceWithoutTVA',str(price_unit * line.qty) or str(0.0))
				merchandises_row.set('TVA',str(per_unit_tax) or str(0.0))
				merchandises_row.set('TotalTVA',str(total_tax) or str(0.0))
				merchandises_row.set('TotalPrice',str(line.price_subtotal_incl) or str(0.0))
				dynamic_merchandises =  ET.SubElement(merchandises_row, "Dynamic")
				dynamic_merchandises =  ET.SubElement(merchandises_row, "Dynamic")

			is_farma =  ET.SubElement(supplier_info, "IsFarma")
			is_farma.text = 'false'

			TaxareaInversa = 'false'
			tax_ids = pos_order.lines.mapped('tax_ids')
			if tax_ids:
				tax_ids = tax_ids.filtered(lambda x: 'Inversa' in x.name)
				if tax_ids:
					TaxareaInversa = 'true'

			taxareainversa =  ET.SubElement(supplier_info, "TaxareaInversa")
			taxareainversa.text = TaxareaInversa

			creation_motiv =  ET.SubElement(supplier_info, "CreationMotiv")
			creation_motiv.text = '1'

			data_contract_mtender =  ET.SubElement(supplier_info, "DataContractMTender")
			data_contract_mtender.set('xmlns:p2','http://www.w3.org/2001/XMLSchema-instance')
			data_contract_mtender.set('p2:nil','true')

		xml_data = ET.tostring(document_root, encoding="utf-8")
		file_upload = base64.b64encode(xml_data)
		file_name = "custom_data.xml"
		return {'file_upload':file_upload,'file_name':'pos_order_' + str(random.randint(0,99999)) + '.xml'}
	
	def action_proceed(self):
		pos_order_ids = self.pos_order_ids
		vals = self.action_show_data(pos_order_ids)
		vals = {'file_name':vals['file_name'],'file_upload':vals['file_upload']}
		pos_export_id = self.env['pos.export'].create({'file_name':vals['file_name'],'file_upload':vals['file_upload']})
		return {
			'type': 'ir.actions.act_window',
			'name': _('POS Export'),
			'res_model': 'pos.export',
			'target': 'new',
			'view_mode': 'form',
			'view_id': self.env.ref('pos_export_scheme.view_pos_export_form').id,
			'res_id':pos_export_id.id,
		}

class POSExport(models.Model):
	_name = "pos.export"
	_description = "POS Export"

	file_upload = fields.Binary(string="Upload File")
	file_name = fields.Char(string="Upload File")

