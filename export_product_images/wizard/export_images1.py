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

class ExportImages(models.TransientModel):
    _name = "export.images"
    _description = "Export Select record of product and Download in Location"
    
    name = fields.Char(string="Name")
    url = fields.Char(string="File Path")

    def action_confirm(self):
        for obj in self:
            active_ids = self._context.get("active_ids")
            product_ids = self.env["product.product"].browse(active_ids)
            user_name = getpass.getuser()

            downloads_folder = os.path.join('/tmp/user', user_name, 'Downloads')
            
            # downloads_folder = os.path.join('home', user_name, 'Downloads')
            folder_name = 'Images'
            full_path = os.path.join(downloads_folder, folder_name)
            if full_path:
                isExist = os.path.exists(full_path)
                if isExist:
                    os.rmdir(path)

                if not isExist:
                   os.makedirs(full_path)

                # if not os.path.isdir(full_path):
                #     os.mkdir(full_path)

                # if os.path.isdir(full_path) and not os.listdir(full_path): 
                #     os.rmdir(full_path)
                # if not os.path.isdir(full_path):
                #     os.mkdir(full_path)

                prod_count = '01'
                prod_img_count = 2
                for product in product_ids:
                    if product.image_1920:
                        if product.default_code:
                            file_name = '[' + product.default_code + ']'+ '-' + str(prod_count) + '-' + product.name
                        else:
                            file_name = str(prod_count) + '-' + product.name

                        full_path_file = os.path.join(full_path, file_name)
                        with open(full_path_file, 'wb') as f:
                            f.write(base64.b64decode(product.image_1920))

                        if product.product_template_image_ids:
                            for line in product.product_template_image_ids:
                                if line.image_1920:
                                    if len(str(prod_img_count)) == 1:
                                        prod_img_count = '0' + str(prod_img_count)
                                    else:
                                        prod_img_count = str(prod_img_count)


                                    if product.default_code:
                                        file_name = '[' + product.default_code + ']' + '-' + prod_img_count + '-' + line.name
                                    else:
                                        file_name = prod_img_count + '-' + line.name
                                    prod_img_count = int(prod_img_count) +  1

                                    full_path_file = os.path.join(full_path, file_name)

                                    with open(full_path_file, 'wb') as f:
                                        f.write(base64.b64decode(line.image_1920))

                # Compress the folder into a zip file
                zip_file_path = os.path.join(downloads_folder, f'{folder_name}.zip')
                with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for root, _, files in os.walk(full_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zip_file.write(file_path, os.path.relpath(file_path, full_path))
                # Remove the temporary folder after creating the zip file
                # os.rmdir(full_path)
                shutil.rmtree(full_path)
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Exported Productes Image Successfully.',
                        'type': 'rainbow_man',
                    }
                }
            else:
                return False
