from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(string="Phone", required=True)

    @api.constrains('phone')
    def _check_unique_phone(self):
        for record in self:
            if record.phone:
                domain = [
                    ('phone', '=', record.phone),
                    ('id', '!=', record.id),
                ]
                if self.search_count(domain):
                    raise ValidationError("Phone must be unique.")
