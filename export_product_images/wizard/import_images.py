# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import io
import zipfile
import base64
import getpass
import os
import re
split_data = [
    '-01-',
    '-02-',
    '-03-',
    '-04-',
    '-05-',
    '-06-',
    '-07-',
    '-08-',
    '-09-',
    '-10-',
    '-11-',
    '-12-',
    '-13-',
    '-14-',
]

class ImportImages(models.TransientModel):
    _name = "import.images"
    _description = "Import Select record of product and Download in Location"

    name = fields.Char(string="Name")
    image_zip_file = fields.Binary(string="Upload File")

    def action_confirm(self):
        for obj in self:
            buffer = {}
            if obj.image_zip_file:
                zip_data = io.BytesIO(base64.b64decode(obj.image_zip_file))
                with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                    for file_name in zip_ref.namelist():
                        with zip_ref.open(file_name) as file:
                            image = ''
                            product_name = file.name
                            product_name = product_name.split('images/')
                            if  len(product_name) == 1:
                                product_name = product_name[0]
                            else:
                                product_name = product_name[1]
                            substring = "-01-"
                            is_product = False
                            is_product_image = False

                            if substring in product_name:
                                is_product = True
                            else:
                                is_product_image = True


                            product_data_name = product_name
                            product_ref_name = ''
                            product_name = ''
                            product_id = False

                            if product_data_name.find('[') >= 0 and product_data_name.find(']') >= 0:
                                p_1 = product_data_name.find('[')
                                p_2 = product_data_name.find(']')
                                product_ref_name = product_data_name[p_1+1:p_2]
                                product_ref_name2 =  product_data_name[p_1:p_2+1]
                                product_name = product_data_name.split(product_ref_name2)

                                found_substring = False
                                substring = ''

                                match = re.search(r'-(\d+)-', product_name[-1])
                                if match:
                                    numeric_value = int(match.group(1))
                                    substring = '-' + str(numeric_value) + '-'
                                    content_found = product_name[-1].find(substring)
                                    if content_found == 0:
                                        found_substring = True

                                if found_substring:
                                    product_name = product_name[-1].split(substring)
                                else:
                                    product_name = product_name[-1].split('-')


                                product_name = product_name[-1]
                                product_name, extension = os.path.splitext(product_name)

                            else:
                                product_name = product_name.split('-')
                                product_name = product_name[-1]
                                product_name, extension = os.path.splitext(product_name)

                            product_name, extension = os.path.splitext(product_name)
                            if is_product:
                                if product_ref_name:
                                    product_id = self.env['product.product'].search([('default_code','ilike',product_ref_name)],limit=1)
                                if not product_id and product_name:
                                    product_id = self.env['product.product'].search([('name','ilike',product_name)],limit=1)
                                if product_id:
                                    file_contents = file.read()
                                    image = base64.b64encode(file_contents)
                                    product_id.image_1920 = image
                                    
                            image = ''
                            if is_product_image:
                                if product_ref_name:
                                    product_id = self.env['product.product'].search([('default_code','ilike',product_ref_name)],limit=1)
                                
                                product_image_id = False                                
                                if not product_id and product_name:
                                    product_image_id = self.env['product.image'].search([('name','ilike',product_name)],limit=1)
                                
                                if product_id:
                                    product_image_id = self.env['product.image'].search(['|',('product_variant_id','=',product_id.id),
                                                                                    ('product_tmpl_id','=',product_id.product_tmpl_id.id),
                                                                                    ('name','ilike',product_name)],limit=1)

                                file_contents = file.read()
                                image = base64.b64encode(file_contents)
                                if product_image_id and product_image_id.image_1920 and image and product_image_id.image_1920 != image:
                                    product_image_id = False

                                if product_image_id and image:
                                    product_image_id.image_1920 = image
                                    product_image_id.name = product_name

                                if not product_image_id and product_id:
                                    if image:
                                        vals = {
                                            'product_variant_id':product_id.id,
                                            'product_tmpl_id':product_id.product_tmpl_id.id,
                                            'name':product_name,
                                            'image_1920':image                                    
                                        }
                                        product_image_id = self.env['product.image'].create(vals)
            return {    

                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Imported Products Image Successfully.',
                        'type': 'rainbow_man',
                    }
                }
