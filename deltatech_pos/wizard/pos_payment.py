# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import base64

from odoo import _, models


class PosMakePayment(models.TransientModel):
    _inherit = "pos.make.payment"

    def check(self):
        res = super(PosMakePayment, self).check()
        if self.payment_method_id.is_cash_count:
            res = self.print_bf_out()
        return res

    def print_bf_out(self):
        order = self.env["pos.order"].browse(self.env.context.get("active_id", False))
        if not order.config_id.ecr_cash_in_out:
            return False
        com_out = ""
        com_print = ""

        if order.config_id.ecr_type == "datecs18":
            com_print = "P,1,______,_,__;%s;;;;\r\n"
            com_out = "I,1,______,_,__;1;%s;;;;\r\n"
        elif order.config_id.ecr_type == "succes":
            com_print = 'R_TXT "{%s}"\r\n'
            com_out = 'R_TXT "{%s}"\r\n'
        elif order.config_id.ecr_type == "optima":
            com_print = "2;%s\r\n"
            com_out = "2;%s\r\n"
        elif order.config_id.ecr_type == "incotex":
            com_print = 'R_TXT "{%s}"\r\n'
            com_out = 'R_TXT "{%s}"\r\n'

        doc_type = "out"

        txt1 = _("Payment disposal")
        txt2 = _("It was paid to:")
        if order.partner_id:
            txt2 += order.partner_id.name
        else:
            txt2 += "__________"

        txt3 = ""

        if order.partner_id:
            txt3 += order.partner_id.name
        else:
            txt3 = "__________"
        txt3 += "          " + self.env.user.name

        amount = self.amount
        amount = -amount if amount < 0.0 else amount
        amount = round(amount, 2)
        data_file = ""
        data_file += com_out % amount
        data_file += com_print % ("{} :{}".format(txt1, order.name))
        data_file += com_print % "---------------------------------------"
        data_file += com_print % txt2
        data_file += com_print % (_("amount :%s") % amount)
        data_file += com_print % ("Ref :%s" % self.payment_name or "")
        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"

        data_file += com_print % _("I received,            I gave,")
        data_file += com_print % txt2

        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"
        data_file += com_print % "---------------------------------------"

        if order.config_id.print_duplicate_in_out:
            data_file += com_print % "***************************************"
            data_file += com_print % "***************************************"
            data_file += com_print % "***************************************"
            data_file += com_print % ("{} :{}".format(txt1, order.name))
            data_file += com_print % "---------------------------------------"
            data_file += com_print % txt2
            data_file += com_print % (_("amount :%s") % amount)
            data_file += com_print % ("Ref :%s" % self.payment_name or "")
            data_file += com_print % "---------------------------------------"
            data_file += com_print % "---------------------------------------"

            data_file += com_print % _("I received,            I gave,")
            data_file += com_print % txt2

            data_file += com_print % "---------------------------------------"
            data_file += com_print % "---------------------------------------"
            data_file += com_print % "---------------------------------------"
            data_file += com_print % "---------------------------------------"
            data_file += com_print % "---------------------------------------"

        data_file = base64.encodebytes(data_file.encode())

        ext = order.config_id.file_ext
        name = order.name.replace("/", "_")
        file_name = "cash_box_{}_{}_{}.{}".format(name, doc_type, self.id, ext)

        wizard = self.env["wizard.download.file"].create({"data_file": data_file, "file_name": file_name})

        return wizard.do_download_file()
