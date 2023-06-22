# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import base64

from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    # todo: de pus un buton in ecran prin care se poate tipari Zetul
    def action_print_z(self):
        data_file = False
        if self.config_id.ecr_type in ["succes", "incotex"]:
            data_file = "C_DYZ"

        if self.config_id.ecr_type == "datecs18":
            data_file = "Z,1,______,_,__;;;;;;;"

        if self.config_id.ecr_type == "fiscalnet":
            data_file = "Z^"

        if not data_file:
            return

        data_file = base64.encodebytes(data_file.encode())
        ext = self.config_id.file_ext
        name = self.name.replace("/", "_")
        file_name = "cash_box_{}_close.{}".format(name, ext)
        wizard = self.env["wizard.download.file"].create({"data_file": data_file, "file_name": file_name})

        return wizard.do_download_file()

    def action_print_x(self):
        data_file = False
        if self.config_id.ecr_type in ["succes", "incotex"]:
            data_file = "C_DYZ"

        if self.config_id.ecr_type == "datecs18":
            data_file = "X,1,______,_,__;;;;;;;"

        if self.config_id.ecr_type == "fiscalnet":
            data_file = "X^"

        if not data_file:
            return

        data_file = base64.encodebytes(data_file.encode())
        ext = self.config_id.file_ext
        name = self.name.replace("/", "_")
        file_name = "cash_box_{}_close.{}".format(name, ext)
        wizard = self.env["wizard.download.file"].create({"data_file": data_file, "file_name": file_name})

        return wizard.do_download_file()
