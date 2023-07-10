from odoo import http, fields, models, _


class YourController(http.Controller):
    @http.route('/download/prescription', type='http', auth="user")
    def download_report(self):
        model = request.env['your.model']
        report_data = model.generate_report()
        report_base64 = report_data

        # Convert the base64-encoded report back to binary data
        report_content = base64.b64decode(report_base64)

        # Create a file-like object for the report data
        report_file = werkzeug.datastructures.FileStorage(report_content)

        # Return the file for download
        return http.send_file(report_file, filename='report.pdf', as_attachment=True)