# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import base64, zipfile, os
from io import BytesIO
import binascii

MAX_FILE_SIZE = 100 * 1024 * 1024  # in megabytes


class ProductImportImageWizard(models.TransientModel):
    _name = 'product.import.image.wizard'
    _description = u'Product Import Image'

    file = fields.Binary(u'Zip File', required=True)

    # @api.multi
    def button_import(self):
        self.ensure_one()
        zip_data = binascii.a2b_base64(self.file)
        fp = BytesIO()
        fp.write(zip_data)
        if not fp:
            raise Exception(_("No file sent."))
        if not zipfile.is_zipfile(fp):
            raise UserError(_('Only zip files are supported.'))
        with zipfile.ZipFile(fp, "r") as z:
            for zf in z.filelist:
                if zf.file_size > MAX_FILE_SIZE:
                    raise UserError(_("File '%s' exceed maximum allowed file size") % zf.filename)

                (name, extension) = os.path.splitext(zf.filename)
                name = name.split('/')
                final_name = name[-1]
                product_ids = self.env['product.product'].search(
                    ['|', ('default_code', '=', final_name), ('barcode', '=', final_name)])
                if product_ids:
                    product_id = product_ids[0]
                    data = z.read(zf.filename)

                    product_id.image_1920 = base64.b64encode(data)
