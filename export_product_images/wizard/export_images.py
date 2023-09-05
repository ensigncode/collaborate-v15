# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import os
import base64
import getpass
import imghdr
import zipfile
import shutil
import io
from io import BytesIO
from odoo.modules.module import get_module_resource


class ExportImages(models.TransientModel):
    _name = "export.images"
    _description = "Export Select record of product and Download in Location"
    
    name = fields.Char(string="Name")
    url = fields.Char(string="File Path")
    zip_file = fields.Binary(string="Zip File")
    zip_name = fields.Char(string="Zip Name")


    def action_confirm(self):
        context = self.env.context
        product_ids = False
        if 'active_model' in context and context['active_model'] == 'product.product':
            active_ids = self._context.get("active_ids")
            product_ids = self.env["product.product"].browse(active_ids)
        else:
            active_ids = self._context.get("active_ids")
            product_temp_ids = self.env["product.template"].browse(active_ids)
            if product_temp_ids:
                product_temps = product_temp_ids.ids
                product_ids = self.env["product.product"].search([('product_tmpl_id','in',product_temps)])


        for obj in self:            
            user_name = getpass.getuser()
            file_path = get_module_resource('export_product_images')
            file_path = file_path + '/product_images'
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            os.mkdir(file_path)
            z_file_path = file_path
            file_path = file_path + '/product_images'
            os.mkdir(file_path)

            prod_count = '01'
            prod_img_count = 2

            for product in product_ids:
                product_image = ''
                website_image = ''

                if product.image_1920:
                    product_name = product.name
                    product_name = product_name.replace('/','-')


                    default_code = product.default_code
                    default_code = default_code.replace('/','-')

                    if default_code:
                        file_name = '[' + default_code + ']'+ '-' + str(prod_count) + '-' + product_name
                    else:
                        file_name = str(prod_count) + '-' + product_name
                    

                    image_path = file_path + '/' + file_name
                    fh = open(image_path, "wb")
                    fh.write(base64.decodebytes(product.image_1920))
                    fh.close()
                    # Set the Image Formate

                    image_formate = imghdr.what(image_path)
                    if image_formate:
                        new_path = file_path+'/'+file_name + '.'+str(image_formate)
                        os.rename(image_path,new_path)

                    if product.product_template_image_ids:
                        for line in product.product_template_image_ids:
                            if line.image_1920:
                                line_name  = line.name 
                                line_name = line_name.replace('/','-')
                                if len(str(prod_img_count)) == 1:
                                    prod_img_count = '0' + str(prod_img_count)
                                else:
                                    prod_img_count = str(prod_img_count)

                                if default_code:
                                    file_name = '[' + default_code + ']' + '-' + prod_img_count + '-' + line_name
                                else:
                                    file_name = prod_img_count + '-' + line_name

                                prod_img_count = int(prod_img_count) +  1
                                image_path = file_path + '/' + file_name
                                fh = open(image_path, "wb")
                                fh.write(base64.decodebytes(line.image_1920))
                                fh.close()

                                image_formate = imghdr.what(image_path)
                                if image_formate:
                                    new_path = file_path+'/'+file_name + '.'+str(image_formate)
                                    os.rename(image_path,new_path)


            m_zip  = shutil.make_archive(z_file_path, 'zip', z_file_path)
            shutil.rmtree(file_path)
            shutil.rmtree(z_file_path)
            with open(m_zip, "rb") as f:
                bytes = f.read()
                self.zip_file = base64.b64encode(bytes)
                self.zip_name = 'product_images.zip'
                
            if os.path.exists(m_zip):
                os.remove(m_zip)

            return {
                'type': 'ir.actions.act_url',
                'target':'new',
                'url': ('/web/content/?model=export.images&download=true&field=zip_file&id=%s&filename=%s'%(self.id, 'product_images.zip')),

            }


