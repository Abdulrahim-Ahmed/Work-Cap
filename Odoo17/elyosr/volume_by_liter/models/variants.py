# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VolumeInProduct(models.Model):
    _inherit = 'product.product'

    volume_by_liter = fields.Float(string="Volume By Liter", store=True, required=False)
    volume = fields.Float(
        'Volume', digits='Volume', store=True)

    @api.onchange('volume_by_liter')
    def _onchange_volume_by_liter(self):
        """ Convert liters to cubic meters (divide by 1000) and update the volume field. """
        for record in self:
            if record.volume_by_liter:
                record.volume = record.volume_by_liter / 1000

    @api.onchange('volume')
    def _onchange_volume(self):
        """ Convert cubic meters to liters (multiply by 1000) and update the volume_by_liter field. """
        for record in self:
            if record.volume:
                record.volume_by_liter = record.volume * 1000

