# -*- coding: utf-8 -*-

from odoo import  models, fields, api, _
import xml.etree.ElementTree as ET
import base64

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
        document_root = ET.Element("Documents")
        for invoice in invoice_ids:
            # Create child elements and add data
            document = ET.SubElement(document_root, "Document")
            supplier_info = ET.SubElement(document, "SupplierInfo")
            
            seria = ET.SubElement(supplier_info, "Seria")
            seria.text = invoice.journal_id.code

            number = ET.SubElement(supplier_info, "Number")
            number.text = invoice.name


            issue_date = ET.SubElement(supplier_info, "IssuedDate")
            issue_date.text = invoice.invoice_date.strftime("%d/%m/%Y")

            delivery_date = ET.SubElement(supplier_info, "DeliveryDate")
            delivery_date.text = invoice.invoice_date.strftime("%d/%m/%Y")

            supplier =  ET.SubElement(supplier_info, "Supplier")
            supplier.set("IDNO", "1023600006055")
            supplier.set("Title", "MIRISTAR-DEAL S.R.L.")
            supplier.set("Address", "SEC.RISCANI Studentilor nr.7 bl.10 of.37")
            supplier.set("NResident", "false")
            supplier.set("IsSupplierOnly", "false")
            supplier.set("TaxpayerType", "1")


            bank_account =  ET.SubElement(supplier_info, "BankAccount")
            bank_account.set("BranchTitle", "BC'Moldindconbank'S.A. suc. 'Kiev' Chisinau")
            bank_account.set("BranchCode", "MOLDMD2X336")
            bank_account.set("Account", "MD67ML000000022516361772")

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

            buyer =  ET.SubElement(supplier_info, "Buyer")
            buyer.set("IDNO", "1023600009883")
            buyer.set("Title", "TENSA ART DESIGN S.R.L.")
            buyer.set("Address", "SEC.RISCANI A. Puskin nr.47/1 bl.C of.1")
            buyer.set("CodTVA", "0612817")
            buyer.set("NResident", "false")
            buyer.set("IsSupplierOnly", "false")
            buyer.set("TaxpayerType", "1")

            bank_account =  ET.SubElement(buyer, "BankAccount")
            bank_account.set("BranchTitle", "")
            bank_account.set("BranchCode", "")
            buyer.set("Address", "SEC.RISCANI A. Puskin nr.47/1 bl.C of.1")
            buyer.set("CodTVA", "0612817")
            buyer.set("NResident", "false")
            buyer.set("IsSupplierOnly", "false")
            buyer.set("TaxpayerType", "1")

            bank_account_manual =  ET.SubElement(bank_account, "IsManual")
            bank_account_manual.text = 'false'

            bank_account_risk_analysis =  ET.SubElement(buyer, "RiskAnalysisValid")
            bank_account_risk_analysis.text = 'false'

            bank_account_registed =  ET.SubElement(buyer, "IsRegistered")
            bank_account_registed.text = 'false'

            bank_account_valid =  ET.SubElement(buyer, "IsValid")
            bank_account_valid.text = 'false'
            
            bank_account_liquodated =  ET.SubElement(buyer, "IsLiquidated")
            bank_account_liquodated.text = 'true'
            
            bank_account_legal_person =  ET.SubElement(buyer, "IsLegalPerson")
            bank_account_legal_person.text = 'true'

            transporter =  ET.SubElement(supplier_info, "Transporter")
            transporter.set("IDNO",'1023600006055')
            transporter.set("Title",'MIRISTAR-DEAL S.R.L.')
            transporter.set("Address",'SEC.RISCANI Studentilor nr.7 bl.10 of.37')
            transporter.set("NResident",'false')
            transporter.set("IsSupplierOnly",'false')
            transporter.set("TaxpayerType",'1')

            transporter_bank_account =  ET.SubElement(transporter, "BankAccount")
            transporter_bank_account.set("BranchTitle",'')
            transporter_bank_account.set("BranchCode",'')
            transporter_bank_account.set("Account",'')

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
            transporter_bank_account_valid.text = 'false'



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

            un_loading_point =  ET.SubElement(supplier_info, "UnloadingPoint")
            un_loading_point.text = 'mun.Chisinau, str.Vlaicu Pircalab, nr.45'


            redirections =  ET.SubElement(supplier_info, "Redirections")
            redirections_total =  ET.SubElement(redirections, "Total")
            redirections_total.text = '100'
            redirections_tva =  ET.SubElement(redirections, "TotalTVA")
            redirections_tva.text = '0'

            merchandises =  ET.SubElement(supplier_info, "Merchandises")
            merchandises_row =  ET.SubElement(merchandises, "Row")
            merchandises_row.set('IsManualEdited','true')
            merchandises_row.set('CalculationScenario','-1')
            merchandises_row.set('Code','1')
            merchandises_row.set('Name','Servicii aromatizare')
            merchandises_row.set('UnitOfMeasure','luna')
            merchandises_row.set('Quantity','1')
            merchandises_row.set('UnitPriceWithoutTVA','1370.00')
            merchandises_row.set('TotalPriceWithoutTVA','1370.00')
            merchandises_row.set('TVA','-')
            merchandises_row.set('TotalTVA','0')
            merchandises_row.set('TotalPrice','1370.00')
            merchandises_row.set('OtherInfo','-')
            merchandises_row.set('PackageType','-')
            merchandises_row.set('NumberOfPlaces','-')
            merchandises_row.set('GrossWeight','-')
            dynamic_merchandises =  ET.SubElement(merchandises_row, "Dynamic")

            is_farma =  ET.SubElement(supplier_info, "IsFarma")
            is_farma.text = 'false'

            taxareainversa =  ET.SubElement(supplier_info, "TaxareaInversa")
            taxareainversa.text = 'false'

            creation_motiv =  ET.SubElement(supplier_info, "CreationMotiv")
            creation_motiv.text = '1'

            data_contract_mtender =  ET.SubElement(supplier_info, "DataContractMTender")
            data_contract_mtender.set('xmlns:p2','http://www.w3.org/2001/XMLSchema-instance')
            data_contract_mtender.set('p2:nil','true')

        xml_data = ET.tostring(document_root, encoding="utf-8")
        file_upoload = base64.b64encode(xml_data)
        file_name = "custom_data.xml"
        return {'file_upoload':file_upoload,'file_name':file_name}
        
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

