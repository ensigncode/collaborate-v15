import base64
import re

from odoo import models, fields, api, _
import werkzeug
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Border, Side, Alignment, Font
from io import BytesIO


class Event(models.Model):
	_inherit = 'calendar.event'

	prescription_code = fields.Char(string="Prescription code")
	optometrist_id = fields.Many2one('hr.employee', string="Optometrist")
	receipt_printed = fields.Boolean(string="Receipt Printed?", default=False)
	receipt_attachment = fields.Binary(string="Attachment Receipt", attachment=False)

	def _get_sf_selection(self):
		return [
			('-20.0', '-20.0'), ('-19.75', '-19.75'), ('-19.5', '-19.5'), ('-19.25', '-19.25'), ('-19.0', '-19.0'),
			('-18.75', '-18.75'), ('-18.5', '-18.5'), ('-18.25', '-18.25'), ('-18.0', '-18.0'), ('-17.75', '-17.75'),
			('-17.5', '-17.5'), ('-17.25', '-17.25'), ('-17.0', '-17.0'), ('-16.75', '-16.75'), ('-16.5', '-16.5'),
			('-16.25', '-16.25'), ('-16.0', '-16.0'), ('-15.75', '-15.75'), ('-15.5', '-15.5'), ('-15.25', '-15.25'),
			('-15.0', '-15.0'), ('-14.75', '-14.75'), ('-14.5', '-14.5'), ('-14.25', '-14.25'), ('-14.0', '-14.0'),
			('-13.75', '-13.75'), ('-13.5', '-13.5'), ('-13.25', '-13.25'), ('-13.0', '-13.0'), ('-12.75', '-12.75'),
			('-12.5', '-12.5'), ('-12.25', '-12.25'), ('-12.0', '-12.0'), ('-11.75', '-11.75'), ('-11.5', '-11.5'),
			('-11.25', '-11.25'), ('-11.0', '-11.0'), ('-10.75', '-10.75'), ('-10.5', '-10.5'), ('-10.25', '-10.25'),
			('-10.0', '-10.0'), ('-9.75', '-9.75'), ('-9.5', '-9.5'), ('-9.25', '-9.25'), ('-9.0', '-9.0'),
			('-8.75', '-8.75'), ('-8.5', '-8.5'), ('-8.25', '-8.25'), ('-8.0', '-8.0'), ('-7.75', '-7.75'),
			('-7.5', '-7.5'), ('-7.25', '-7.25'), ('-7.0', '-7.0'), ('-6.75', '-6.75'), ('-6.5', '-6.5'),
			('-6.25', '-6.25'), ('-6.0', '-6.0'), ('-5.75', '-5.75'), ('-5.5', '-5.5'), ('-5.25', '-5.25'),
			('-5.0', '-5.0'), ('-4.75', '-4.75'), ('-4.5', '-4.5'), ('-4.25', '-4.25'), ('-4.0', '-4.0'),
			('-3.75', '-3.75'), ('-3.5', '-3.5'), ('-3.25', '-3.25'), ('-3.0', '-3.0'), ('-2.75', '-2.75'),
			('-2.5', '-2.5'), ('-2.25', '-2.25'), ('-2.0', '-2.0'), ('-1.75', '-1.75'), ('-1.5', '-1.5'),
			('-1.25', '-1.25'), ('-1.0', '-1.0'), ('-0.75', '-0.75'), ('-0.5', '-0.5'), ('-0.25', '-0.25'),
			('0.0', '0.0'),
			('0.25', '0.25'), ('0.5', '0.5'), ('0.75', '0.75'), ('1.0', '1.0'), ('1.25', '1.25'), ('1.5', '1.5'),
			('1.75', '1.75'), ('2.0', '2.0'), ('2.25', '2.25'), ('2.5', '2.5'), ('2.75', '2.75'), ('3.0', '3.0'),
			('3.25', '3.25'), ('3.5', '3.5'), ('3.75', '3.75'), ('4.0', '4.0'), ('4.25', '4.25'), ('4.5', '4.5'),
			('4.75', '4.75'), ('5.0', '5.0'), ('5.25', '5.25'), ('5.5', '5.5'), ('5.75', '5.75'), ('6.0', '6.0'),
			('6.25', '6.25'), ('6.5', '6.5'), ('6.75', '6.75'), ('7.0', '7.0'), ('7.25', '7.25'), ('7.5', '7.5'),
			('7.75', '7.75'), ('8.0', '8.0'), ('8.25', '8.25'), ('8.5', '8.5'), ('8.75', '8.75'), ('9.0', '9.0'),
			('9.25', '9.25'), ('9.5', '9.5'), ('9.75', '9.75'), ('10.0', '10.0'), ('10.25', '10.25'), ('10.5', '10.5'),
			('10.75', '10.75'), ('11.0', '11.0'), ('11.25', '11.25'), ('11.5', '11.5'), ('11.75', '11.75'),
			('12.0', '12.0'), ('12.25', '12.25'), ('12.5', '12.5'), ('12.75', '12.75'), ('13.0', '13.0'),
			('13.25', '13.25'), ('13.5', '13.5'), ('13.75', '13.75'), ('14.0', '14.0'), ('14.25', '14.25'),
			('14.5', '14.5'), ('14.75', '14.75'), ('15.0', '15.0'), ('15.25', '15.25'), ('15.5', '15.5'),
			('15.75', '15.75'), ('16.0', '16.0'), ('16.25', '16.25'), ('16.5', '16.5'), ('16.75', '16.75'),
			('17.0', '17.0'), ('17.25', '17.25'), ('17.5', '17.5'), ('17.75', '17.75'), ('18.0', '18.0'),
			('18.25', '18.25'), ('18.5', '18.5'), ('18.75', '18.75'), ('19.0', '19.0'), ('19.25', '19.25'),
			('19.5', '19.5'), ('19.75', '19.75'), ('20.0', '20.0')]

	def _get_cil_selection(self):
		return [
			('-6.0', '-6.0'), ('-5.75', '-5.75'), ('-5.5', '-5.5'), ('-5.25', '-5.25'), ('-5.0', '-5.0'),
			('-4.75', '-4.75'), ('-4.5', '-4.5'), ('-4.25', '-4.25'), ('-4.0', '-4.0'), ('-3.75', '-3.75'),
			('-3.5', '-3.5'), ('-3.25', '-3.25'), ('-3.0', '-3.0'), ('-2.75', '-2.75'), ('-2.5', '-2.5'),
			('-2.25', '-2.25'), ('-2.0', '-2.0'), ('-1.75', '-1.75'), ('-1.5', '-1.5'), ('-1.25', '-1.25'),
			('-1.0', '-1.0'), ('-0.75', '-0.75'), ('-0.5', '-0.5'), ('-0.25', '-0.25'), ('0.0', '0.0'),
			('0.25', '0.25'),
			('0.5', '0.5'), ('0.75', '0.75'), ('1.0', '1.0'), ('1.25', '1.25'), ('1.5', '1.5'), ('1.75', '1.75'),
			('2.0', '2.0'), ('2.25', '2.25'), ('2.5', '2.5'), ('2.75', '2.75'), ('3.0', '3.0'), ('3.25', '3.25'),
			('3.5', '3.5'), ('3.75', '3.75'), ('4.0', '4.0'), ('4.25', '4.25'), ('4.5', '4.5'), ('4.75', '4.75'),
			('5.0', '5.0'), ('5.25', '5.25'), ('5.5', '5.5'), ('5.75', '5.75'), ('6.0', '6.0')]

	def _get_ax_selection(self):
		return [(str(i), str(i)) for i in range(0, 181)]

	def _get_dp_selection(self):
		return [(str(j), str(j)) for j in range(45, 76)]

	def _get_av_selection(self):
		return [(str(round(x * 0.1, 2)), str(round(x * 0.1, 2))) for x in range(1, 11)]

	varsta = fields.Selection([
		('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
		('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
		('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'),
		('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'),
		('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31'),
		('32', '32'), ('33', '33'), ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37'),
		('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'),
		('44', '44'), ('45', '45'), ('46', '46'), ('47', '47'), ('48', '48'), ('49', '49'),
		('50', '50'), ('51', '51'), ('52', '52'), ('53', '53'), ('54', '54'), ('55', '55'),
		('56', '56'), ('57', '57'), ('58', '58'), ('59', '59'), ('60', '60'), ('61', '61'),
		('62', '62'), ('63', '63'), ('64', '64'), ('65', '65'), ('66', '66'), ('67', '67'),
		('68', '68'), ('69', '69'), ('70', '70'), ('71', '71'), ('72', '72'), ('73', '73'),
		('74', '74'), ('75', '75'), ('76', '76'), ('77', '77'), ('78', '78'), ('79', '79'),
		('80', '80'), ('81', '81'), ('82', '82'), ('83', '83'), ('84', '84'), ('85', '85'),
		('86', '86'), ('87', '87'), ('88', '88'), ('89', '89'), ('90', '90'), ('91', '91'),
		('92', '92'), ('93', '93'), ('94', '94'), ('95', '95'), ('96', '96'), ('97', '97'),
		('98', '98'), ('99', '99'), ('100', '100')], string="Varsta")

	# SF Field variations
	vd_od_sf = fields.Selection(_get_sf_selection, string="V.D. O.D. SF")
	vd_os_sf = fields.Selection(_get_sf_selection, string="V.D. O.S. SF")
	va_od_sf = fields.Selection(_get_sf_selection, string="V.A. O.D. SF")
	va_os_sf = fields.Selection(_get_sf_selection, string="V.A. O.S. SF")

	# CIL Field variations
	vd_od_cil = fields.Selection(_get_cil_selection, string="V.D. O.D. CIL")
	vd_os_cil = fields.Selection(_get_cil_selection, string="V.D. O.S. CIL")
	va_od_cil = fields.Selection(_get_cil_selection, string="V.A. O.D. CIL")
	va_os_cil = fields.Selection(_get_cil_selection, string="V.A. O.S. CIL")

	# AX Field Variations
	vd_od_ax = fields.Selection(_get_ax_selection, string="V.D. O.D. AX")
	vd_os_ax = fields.Selection(_get_ax_selection, string="V.D. O.S. AX")
	va_od_ax = fields.Selection(_get_ax_selection, string="V.A. O.D. AX")
	va_os_ax = fields.Selection(_get_ax_selection, string="V.A. O.S. AX")

	# DP Field Variations
	vd_dp = fields.Selection(_get_ax_selection, string="V.D. DP")
	va_dp = fields.Selection(_get_ax_selection, string="V.A. DP")

	av_fc_od = fields.Selection(_get_av_selection, string="A.V. FC OD")
	av_fc_os = fields.Selection(_get_av_selection, string="A.V. FC OS")
	av_cc_od = fields.Selection(_get_av_selection, string="A.V. C.C. OD")
	av_cc_os = fields.Selection(_get_av_selection, string="A.V. C.C. O.S.")
	recomandare = fields.Selection([
		("Protectie monitor", "Protectie monitor"),
		("Antireflex", "Antireflex"),
		("Fotocromatic", "Fotocromatic"),
		("Bifocal", "Bifocal"),
		("Progresiv", "Progresiv"),
		("Necesita medic oftalmolog", "Necesita medic oftalmolog")]
		, string="Recomandare")
	diagnostic = fields.Selection([
		("Miopie", "Miopie"), ("Hipermetropie", "Hipermetropie"), ("Presbiopie", "Presbiopie"),
		("Astigmatism miopic", "Astigmatism miopic"), ("Astigmatism hipermetropic", "Astigmatism hipermetropic")
	], string="Diagnostic")
	prescription_date = fields.Date(string="Date", compute="_compute_prescription_date")
	attendee_id = fields.Many2one(
		'res.partner', string="Attendee", compute="_compute_single_attendee", inverse="_inverse_single_attendee",
		compute_sudo=True, readonly=False, store=True)
	observation = fields.Text(string="Observatii")

	@api.depends('partner_ids')
	def _compute_single_attendee(self):
		for rec in self._origin:
			attendees = rec.partner_ids._origin.filtered(lambda p: p.id != rec.user_id.partner_id.id)
			rec.attendee_id = attendees[0]._origin.id if attendees else False

	def _inverse_single_attendee(self):
		for rec in self:
			rec.sudo().attendee_id = rec.attendee_id

	def _compute_prescription_date(self):
		for rec in self:
			rec.prescription_date = rec.start.date()

	@api.model
	def create(self, vals):
		if not vals.get('prescription_code'):
			vals['prescription_code'] = self.env['ir.sequence'].sudo().next_by_code('calendar.event') or _('New')
		return super(Event, self).create(vals)

	def print_prescription(self):
		"""
			Print Prescription Method
		"""
		pdf = self.env.ref("appointment_receipt.calendar_event_print_prescription_receipt")._render_qweb_pdf(
			res_ids=self.ids)[0]
		pdf = base64.b64encode(pdf).decode()
		attachment_name = 'PRESCRIPTIE OPTOMETRICA - %s' % (self.prescription_code or '').replace('#', '')
		attachment = self.env['ir.attachment'].sudo().create({
			'name': attachment_name + '.pdf',
			'datas': pdf,
			'mimetype': 'application/pdf',
			'res_model': 'calendar.event',
			'res_id': self.id,
		})
		# For portal
		attachment.generate_access_token()
		self.message_post(attachment_ids=[attachment.id])

		self.write({
			'receipt_printed': True,
			'receipt_attachment': pdf,
			'appointment_status_id': self.env.ref('website_appointment_extend.appointment_status_7').id,
		})

	def calender_event_data(self):
		query = """
				SELECT
					ce.start AS start_date,
					ce.location AS location,
					count(*) AS total_no_of_appointments,
					SUM(CASE WHEN receipt_printed IS TRUE THEN 1 ELSE 0 END) AS no_of_finished_appointments,
					CASE WHEN COUNT(*) = 0 THEN NULL ELSE (SUM(CASE WHEN receipt_printed IS TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100 END AS finalisation_rate,
					(SELECT COUNT(*) FROM calendar_event event 
						LEFT JOIN crm_lead cl ON cl.id = event.opportunity_id 
						LEFT JOIN sale_order so ON so.opportunity_id = cl.id 
						WHERE so.opportunity_id IS NOT NULL AND event.opportunity_id IS NOT NULL
					) AS no_of_appointments_with_so,
					(
						(
							(SELECT COUNT(*) FROM calendar_event WHERE receipt_printed IS TRUE) - 
							(
								SELECT COUNT(*) FROM calendar_event event 
								LEFT JOIN crm_lead cl ON cl.id = event.opportunity_id 
								LEFT JOIN sale_order so ON so.opportunity_id = cl.id 
								WHERE so.opportunity_id IS NOT NULL AND event.opportunity_id IS NOT NULL
							)
						) / 
						CASE 
							WHEN (SELECT COUNT(*) FROM calendar_event WHERE receipt_printed IS TRUE) > 0
							THEN (SELECT COUNT(*) FROM calendar_event WHERE receipt_printed IS TRUE)
							ELSE 1 -- This prevents division by zero
						END
					) * 100 AS appointments_with_so_tf_appointments
				
				FROM
					calendar_event ce
				
				GROUP BY
					ce.id
			"""
		self.env.cr.execute(query)
		data = self.env.cr.dictfetchall()
		data_dict = self.group_events_by_month(data)

		# Create a new workbook
		wb = Workbook()

		# Create a worksheet
		wrksht = wb.active
		f_name = 'output'
		wrksht.title = 'test'

		table_header_alignment = Alignment(horizontal='left', vertical='top', text_rotation=0, wrap_text=True)
		bold_text = Font(name="Calibri", size=11, bold=True)
		border_bottom = Border(bottom=Side(style='thin'))

		table_header = 1
		# row_indexs = table_header + 1

		wrksht.cell(row=1, column=1).value = 'Appointment month'
		wrksht.cell(row=1, column=1).font = bold_text
		wrksht.cell(row=1, column=1).alignment = table_header_alignment
		wrksht.cell(row=1, column=1).border = border_bottom

		wrksht.cell(row=1, column=2).value = 'Appointment location'
		wrksht.cell(row=1, column=2).font = bold_text
		wrksht.cell(row=1, column=2).alignment = table_header_alignment
		wrksht.cell(row=1, column=2).border = border_bottom

		wrksht.cell(row=1, column=3).value = 'Total no of appointments'
		wrksht.cell(row=1, column=3).font = bold_text
		wrksht.cell(row=1, column=3).alignment = table_header_alignment
		wrksht.cell(row=1, column=3).border = border_bottom

		wrksht.cell(row=1, column=4).value = 'No of finished appointments'
		wrksht.cell(row=1, column=4).font = bold_text
		wrksht.cell(row=1, column=4).alignment = table_header_alignment
		wrksht.cell(row=1, column=4).border = border_bottom

		wrksht.cell(row=1, column=5).value = 'Finalization rate'
		wrksht.cell(row=1, column=5).font = bold_text
		wrksht.cell(row=1, column=5).alignment = table_header_alignment
		wrksht.cell(row=1, column=5).border = border_bottom

		wrksht.cell(row=1, column=6).value = 'No of aapointments with SO'
		wrksht.cell(row=1, column=6).font = bold_text
		wrksht.cell(row=1, column=6).alignment = table_header_alignment
		wrksht.cell(row=1, column=6).border = border_bottom

		wrksht.cell(row=1, column=7).value = '"%" apointments with SO from total finished appointments'
		wrksht.cell(row=1, column=7).font = bold_text
		wrksht.cell(row=1, column=7).alignment = table_header_alignment
		wrksht.cell(row=1, column=7).border = border_bottom

		table_col = 1
		table_row = table_header + 1
		for month in data_dict:
			wrksht.cell(row=table_row, column=table_col).value = month
			for d in data_dict.get(month)['events']:
				wrksht.cell(row=table_row, column=table_col+1).value = d.get('location')
				wrksht.cell(row=table_row, column=table_col+2).value = d.get('total_no_of_appointments')
				wrksht.cell(row=table_row, column=table_col+3).value = d.get('no_of_finished_appointments')
				wrksht.cell(row=table_row, column=table_col+4).value = d.get('finalisation_rate')
				wrksht.cell(row=table_row, column=table_col+5).value = d.get('no_of_appointments_with_so')
				wrksht.cell(row=table_row, column=table_col+6).value = d.get('appointments_with_so_tf_appointments')
				table_row += 1
			wrksht.cell(row=table_row, column=table_col+1).value = 'Total'
			wrksht.cell(row=table_row, column=table_col+1).font = bold_text

			wrksht.cell(row=table_row, column=table_col+2).value = data_dict.get(month)['total_total_no_of_appointments']
			wrksht.cell(row=table_row, column=table_col+2).font = bold_text

			wrksht.cell(row=table_row, column=table_col+3).value = data_dict.get(month)['total_no_of_finished_appointments']
			wrksht.cell(row=table_row, column=table_col+3).font = bold_text

			wrksht.cell(row=table_row, column=table_col+4).value = sum(data_dict.get(month)['total_finalisation_rate'])/len(data_dict.get(month)['total_finalisation_rate'])
			wrksht.cell(row=table_row, column=table_col+4).font = bold_text

			wrksht.cell(row=table_row, column=table_col+5).value = data_dict.get(month)['total_no_of_appointments_with_so']
			wrksht.cell(row=table_row, column=table_col+5).font = bold_text

			wrksht.cell(row=table_row, column=table_col+6).value = sum(data_dict.get(month)['total_appointments_with_so_tf_appointments'])/len(data_dict.get(month)['total_appointments_with_so_tf_appointments'])
			wrksht.cell(row=table_row, column=table_col+6).font = bold_text

			table_row += 1

		wrksht.column_dimensions['A'].width = 10
		wrksht.column_dimensions['B'].width = 14
		wrksht.column_dimensions['C'].width = 14
		wrksht.column_dimensions['D'].width = 14
		wrksht.column_dimensions['E'].width = 14
		wrksht.column_dimensions['F'].width = 14
		wrksht.column_dimensions['G'].width = 14
		

		fp = BytesIO()
		wb.save(fp)
		fp.seek(0)
		data = fp.read()
		fp.close()

		wiz_id = self.env['print.report.wizard'].create({'file':base64.b64encode(data)})

		return {
			'type': 'ir.actions.act_url',
			'url': 'web/content/?model=print.report.wizard&download=true&field=file&id=%s&filename=%s.xlsx' % (wiz_id.id, f_name),
			'target': 'self',
		}

	def group_events_by_month(self,data):
		grouped_events = {}
		
		for event in data:
			start_date = event['start_date']
			month_year_key = f"{start_date.strftime('%b')}-{start_date.year}"

			if month_year_key not in grouped_events:
				grouped_events[month_year_key] = {
					'events': [], 
					'total_total_no_of_appointments': 0,
					'total_no_of_finished_appointments':0, 
					'total_finalisation_rate': [],
					'total_no_of_appointments_with_so':0,
					'total_appointments_with_so_tf_appointments':[]
				}

			grouped_events[month_year_key]['events'].append(event)
			grouped_events[month_year_key]['total_total_no_of_appointments'] += event['total_no_of_appointments']
			grouped_events[month_year_key]['total_no_of_finished_appointments'] += event['no_of_finished_appointments']
			grouped_events[month_year_key]['total_finalisation_rate'].append(event['finalisation_rate'])
			grouped_events[month_year_key]['total_no_of_appointments_with_so'] += event['no_of_appointments_with_so']
			grouped_events[month_year_key]['total_appointments_with_so_tf_appointments'].append(event['appointments_with_so_tf_appointments'])

		return grouped_events
