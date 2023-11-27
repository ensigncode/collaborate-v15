from odoo import _, fields, models


class PrintReportWizard(models.TransientModel):
    _name = 'print.report.wizard'
    _description = 'Print Report Wizard'

    file = fields.Binary('File')
