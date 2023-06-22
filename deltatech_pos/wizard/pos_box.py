# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import base64

from odoo import _, api, fields

from odoo.addons.account.wizard.pos_box import CashBox

# Introducere numerar in sertar :
# I,1,______,_,__;0;10<suma>;;;;
#
# Retragere numerar din sertar :
# I,1,______,_,__;1;10<suma>;
#


class PosBoxExtended(CashBox):
    _register = False

    partner_id = fields.Many2one("res.partner", string="Partner")
    number = fields.Char("Number", default=lambda self: self.env["ir.sequence"].next_by_code("pos.box"))

    def _create_bank_statement_line(self, record):
        res = super(PosBoxExtended, self)._create_bank_statement_line(record)

        return res

    @api.model
    def create_and_run(self, values):
        obj = self.create(values)
        res = obj.run()
        return res

    def print_in_out(self, operation_type, records):
        res = False
        if operation_type == "in":
            report = self.env.ref("l10n_ro_invoice_report.action_report_statement_collection")
        else:
            report = self.env.ref("l10n_ro_invoice_report.action_report_statement_payment")
        if report:
            ids = []
            for record in records:
                ids += [max(record.line_ids.ids)]
            res = report.report_action(ids)
        return res

    def print_bf_in_out(self, operation_type, record):
        com_in = ""
        com_out = ""
        com_print = ""
        com = ""
        txt1 = ""
        txt2 = ""

        if record.config_id.ecr_type == "datecs18":
            com_print = "P,1,______,_,__;%s;;;;\r\n"
            com_in = "I,1,______,_,__;0;%s;;;;\r\n"
            com_out = "I,1,______,_,__;1;%s;;;;\r\n"
        elif record.config_id.ecr_type == "succes":
            com_print = 'R_TXT "{%s}"\r\n'
            com_in = 'R_TXT "{%s}"\r\n'
            com_out = 'R_TXT "{%s}"\r\n'
        elif record.config_id.ecr_type == "optima":
            com_print = "2;%s\r\n"
            com_in = "2;%s\r\n"
            com_out = "2;%s\r\n"
        elif record.config_id.ecr_type == "incotex":
            com_print = 'R_TXT "{%s}"\r\n'
            com_in = 'R_TXT "{%s}"\r\n'
            com_out = 'R_TXT "{%s}"\r\n'

        if operation_type == "in":
            com = com_in
            txt1 = _("*Cash collection*")
            txt2 = _("*It has been collected from the delegate*")
            txt3 = self.env.user.name
            if self.partner_id:
                txt3 += "          " + self.partner_id.name

        if operation_type == "out":
            com = com_out

            txt1 = _("*Payment disposal*")
            txt2 = _("*It was paid to the delegate*")
            txt3 = ""
            if self.partner_id:
                txt3 += self.partner_id.name
            txt3 += "          " + self.env.user.name

        amount = self.amount
        amount = -amount if amount < 0.0 else amount
        data_file = ""
        if self.partner_id:
            data_file += com_print % self.partner_id.name
            if self.partner_id.is_company:
                data_file += com_print % self.partner_id.vat
                data_file += com_print % self.partner_id.nrc
        data_file += com_print % ("{} :{}".format(txt1, self.number))
        data_file += com_print % "---------------------------------------"
        data_file += com_print % txt2
        data_file += com_print % (_("amount :%s") % amount)
        data_file += com_print % ("Ref :%s" % self.name or "")
        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"

        data_file += com_print % _("I received,")
        data_file += com_print % txt2
        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"
        data_file += com_print % _("I gave,")
        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"
        data_file = base64.encodebytes(data_file.encode())

        ext = record.config_id.file_ext
        name = record.name.replace("/", "_")
        file_name = "nf_cash_box_{}_{}_{}.{}".format(name, operation_type, self.id, ext)

        wizard = self.env["wizard.download.file"].create({"data_file": data_file, "file_name": file_name})

        return wizard.do_download_file()


# aceasta clasa nu mai exista in 13.
# class PosBoxIn(PosBoxExtended):
#     _inherit = 'cash.box.in'
#
#     def _calculate_values_for_statement_line(self, record):
#         values = super(PosBoxIn, self)._calculate_values_for_statement_line(record=record)
#
#
#         if self.partner_id:
#             values['partner_id'] = self.partner_id.id
#
#             active_model = self.env.context.get('active_model', False)
#             active_ids = self.env.context.get('active_ids', [])
#             if active_model == 'pos.session' and active_ids:
#                 session = self.env[active_model].browse(active_ids)
#
#             if session.config_id.transfer_account_id and
#             self.partner_id.commercial_partner_id != record.journal_id.company_id.partner_id:
#                 values['account_id'] = session.config_id.transfer_account_id.id
#
#         values['name'] = self.number
#         # values['ref'] = _('Put Money In Cash')
#         values['ref'] = self.ref or self.name
#
#         return values
#
#
#     def run(self):
#         active_model = self.env.context.get('active_model', False)
#         active_ids = self.env.context.get('active_ids', [])
#         res = super(PosBoxIn, self).run()
#         if active_model == 'pos.session':
#             sessions = self.env[active_model].browse(active_ids)
#             if sessions.config_id.ecr_cash_in_out:
#                 res = self.print_bf_in_out('in', sessions)
#             else:
#                 bank_statements = [session.cash_register_id for session in sessions if session.cash_register_id]
#                 res = self.print_in_out('in', bank_statements)
#         return res


class PosBoxOut(PosBoxExtended):
    _inherit = "cash.box.out"

    ref = fields.Char("Reference")

    def _calculate_values_for_statement_line(self, record):
        values = super(PosBoxOut, self)._calculate_values_for_statement_line(record=record)
        if self.partner_id:
            values["partner_id"] = self.partner_id.id

            active_model = self.env.context.get("active_model", False)
            active_ids = self.env.context.get("active_ids", [])
            if active_model == "pos.session" and active_ids:
                session = self.env[active_model].browse(active_ids)
            else:
                session = record.pos_session_id

            if (
                session.config_id.transfer_account_id
                and self.partner_id.commercial_partner_id != record.journal_id.company_id.partner_id
            ):
                values["counterpart_account_id"] = session.config_id.transfer_account_id.id

        # values["name"] = self.number
        # values['ref'] = _('Take Money From Cash')
        values["ref"] = self.ref or self.name
        return values

    def run(self):
        active_model = self.env.context.get("active_model", False)
        active_ids = self.env.context.get("active_ids", [])
        res = super(PosBoxOut, self).run()
        if active_model == "pos.session":
            sessions = self.env[active_model].browse(active_ids)
            if sessions.config_id.ecr_cash_in_out:
                if self.amount > 0:
                    res = self.print_bf_in_out("in", sessions)
                else:
                    res = self.print_bf_in_out("out", sessions)
            else:
                bank_statements = [session.cash_register_id for session in sessions if session.cash_register_id]
                if self.amount > 0:
                    res = self.print_in_out("in", bank_statements)
                else:
                    res = self.print_bf_in_out("out", sessions)
        return res
