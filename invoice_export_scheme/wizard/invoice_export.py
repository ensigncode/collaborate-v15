# -*- coding: utf-8 -*-

from odoo import  models, fields, api, _
import xml.etree.ElementTree as ET
import base64
import  random
from odoo.exceptions import UserError

class InvoiceSelect(models.Model):
    _name = "invoice.select"
    _description = "Invoice Select"

    name = fields.Char(default="Invoice Export")
    invoice_ids = fields.Many2many('account.move',string="Invoices")

    @api.model
    def default_get(self,vals):
        res = super(InvoiceSelect,self).default_get(vals)
        ctx = self.env.context
        active_ids = ctx['active_ids']
        res['invoice_ids'] = [(6,0,active_ids)]
        return res


    def action_show_data(self,invoice_ids):
        extra_invoice_ids = invoice_ids.filtered(lambda x:x.move_type not in ('out_invoice','in_invoice'))
        if extra_invoice_ids:
            raise UserError(_('Invoice Export Scheme will be done only on Customer Invoice and Vendor Bills'))

        document_root = ET.Element("Documents")
        for invoice in invoice_ids:
            if invoice.move_type == 'in_invoice':
                supplier_id = invoice.partner_id
                buyer_id = invoice.company_id.partner_id
            else:
                supplier_id = invoice.company_id.partner_id
                buyer_id = invoice.partner_id
                

            # Create child elements and add data
            document = ET.SubElement(document_root, "Document")
            supplier_info = ET.SubElement(document, "SupplierInfo")
            
            seria = ET.SubElement(supplier_info, "Seria")
            seria.text = invoice.journal_id.code

            number = ET.SubElement(supplier_info, "Number")
            number.text = invoice.name

            IsSupplierOnly = 'false'
            if supplier_id and supplier_id.supplier_rank:
                IsSupplierOnly = 'true'

            # supplier_address = supplier_id.street or '' + ' ,' + supplier_id.street2  or '' + ' , ' + supplier_id.city or ''
            supplier_address = supplier_id.street if supplier_id.street else '' + ' ,' + supplier_id.street2 if supplier_id.street else ''  + ' , ' + supplier_id.city if supplier_id.city else ''
            issue_date = ET.SubElement(supplier_info, "IssuedDate")
            issue_date.text = invoice.invoice_date.strftime("%Y-%m-%d") if invoice.invoice_date else ''

            delivery_date = ET.SubElement(supplier_info, "DeliveryDate")
            delivery_date.text = invoice.invoice_date.strftime("%Y-%m-%d") if invoice.invoice_date else ''

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

            is_legalperson =  ET.SubElement(supplier_info, "IsLegalPerson")
            is_legalperson.text = 'false'

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

            if invoice.move_type == 'in_invoice':
                transporter =  ET.SubElement(supplier_info, "Transporter")
                transporter.set("IDNO", supplier_id.vat or "")
                transporter.set("Title",supplier_id.name or "")
                transporter.set("Address",supplier_address)
                transporter.set("NResident",'false')
                transporter.set("IsSupplierOnly",'false')
                transporter.set("TaxpayerType",'1')

                transporter_bank_account =  ET.SubElement(transporter, "BankAccount")
                transporter_bank_account.set("BranchTitle",Supplier_BranchTitle)
                transporter_bank_account.set("BranchCode",Supplier_BranchCode)
                transporter_bank_account.set("Account",Supplier_Account)

                transporter_bank_account_manual =  ET.SubElement(transporter_bank_account, "IsManual")
                transporter_bank_account_manual.text = 'true'


                transporter_bank_account_risk =  ET.SubElement(transporter, "RiskAnalysisValid")
                transporter_bank_account_risk.text = 'false'

                transporter_bank_account_registered =  ET.SubElement(transporter, "IsRegistered")
                transporter_bank_account_registered.text = 'false'

                transporter_bank_account_valid =  ET.SubElement(transporter, "IsValid")
                transporter_bank_account_valid.text = 'false'

                transporter_bank_account_liquidate =  ET.SubElement(transporter, "IsLiquidated")
                transporter_bank_account_liquidate.text = 'false'

                transporter_bank_account_legal_person =  ET.SubElement(transporter, "IsLegalPerson")
                if supplier_id and supplier_id.company_type == 'company':
                    transporter_bank_account_legal_person.text = 'true'
                else:
                    transporter_bank_account_legal_person.text = 'false'

                attached_documents =  ET.SubElement(supplier_info, "AttachedDocuments")
                attached_documents.text = 'act servicii'

            delegate_date =  ET.SubElement(supplier_info, "DelegateDate")
            delegate_date.set("xmlns:p2",'http://www.w3.org/2001/XMLSchema-instance')
            delegate_date.set("p2:nil",'true')

            vehicle_log_book =  ET.SubElement(supplier_info, "VehicleLogbook")

            vehicle_log_book_issue_date =  ET.SubElement(vehicle_log_book, "IssuedDate")
            vehicle_log_book_issue_date.set("xmlns:p3","http://www.w3.org/2001/XMLSchema-instance")
            vehicle_log_book_issue_date.set("p3:nil","true")
            vehicle_log_book_seria =  ET.SubElement(vehicle_log_book, "Seria")
            vehicle_log_book_number =  ET.SubElement(vehicle_log_book, "Number")

            loading_point =  ET.SubElement(supplier_info, "LoadingPoint")
            loading_point.text = 'mun.Chisinau, str.Podul Inalt, nr.18/1, of.31'

            if invoice.move_type == 'in_invoice':
                un_loading_point =  ET.SubElement(supplier_info, "UnloadingPoint")
                un_loading_point.text = 'mun.Chisinau, str.Vlaicu Pircalab, nr.45'

            redirections =  ET.SubElement(supplier_info, "Redirections")
            redirections_total =  ET.SubElement(redirections, "Total")
            redirections_total.text = '100'
            redirections_tva =  ET.SubElement(redirections, "TotalTVA")
            redirections_tva.text = '0'

            merchandises =  ET.SubElement(supplier_info, "Merchandises")

            
            for line in invoice.invoice_line_ids:
                merchandises_row =  ET.SubElement(merchandises, "Row")
                merchandises_row.set('IsManualEdited','true')
                merchandises_row.set('CalculationScenario','-1')
                merchandises_row.set('Code',line.product_id.default_code if line.product_id and line.product_id.default_code else '')
                merchandises_row.set('Name',line.product_id.display_name if line.product_id else '')
                merchandises_row.set('UnitOfMeasure',line.product_uom_id.name if line.product_uom_id else '')
                merchandises_row.set('Quantity',str(line.quantity))
                merchandises_row.set('UnitPriceWithoutTVA',str(line.price_unit) or str(0.0))
                merchandises_row.set('TotalPriceWithoutTVA',str(line.price_subtotal) or str(0.0))
                merchandises_row.set('TVA','-')
                merchandises_row.set('TotalTVA',str(line.price_total - line.price_subtotal) or str(0.0))
                merchandises_row.set('TotalPrice',str(line.price_total) or str(0.0))
                if invoice.move_type == 'in_invoice':
                    merchandises_row.set('OtherInfo','-')
                    merchandises_row.set('PackageType','-')
                    merchandises_row.set('NumberOfPlaces','-')
                    merchandises_row.set('GrossWeight','-')
                dynamic_merchandises =  ET.SubElement(merchandises_row, "Dynamic")
                dynamic_merchandises =  ET.SubElement(merchandises_row, "Dynamic")


            is_farma =  ET.SubElement(supplier_info, "IsFarma")
            is_farma.text = 'false'

            TaxareaInversa = 'false'
            tax_ids = invoice.invoice_line_ids.mapped('tax_ids')
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
        file_upoload = base64.b64encode(xml_data)
        file_name = "custom_data.xml"

        journal_code = ''
        if invoice_ids and invoice_ids[0] and invoice_ids[0].journal_id:
            journal_code = invoice_ids[0].journal_id.code + '__'

        return {'file_upoload':file_upoload,'file_name':journal_code + str(random.randint(0,99999)) + '.xml'}
        
    def action_proceed(self):
        invoice_ids = self.invoice_ids
        vals = self.action_show_data(invoice_ids)
        invoice_export_id = self.env['invoice.export'].create({'file_name':vals['file_name'],'file_upoload':vals['file_upoload']})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Taxes'),
            'res_model': 'invoice.export',
            'target': 'new',
            'view_mode': 'form',
            'view_id': self.env.ref('invoice_export_scheme.view_invoice_export_form').id,
            'res_id':invoice_export_id.id,
        }

class InvoiceExport(models.Model):
    _name = "invoice.export"
    _description = "Invoice Export"

    file_upoload = fields.Binary(string="Upload File")
    file_name = fields.Char(string="Upload File")

