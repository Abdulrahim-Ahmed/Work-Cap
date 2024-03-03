# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.report'
    _description = 'Sale Report'

    tag_id = fields.Many2many('crm.tag', 'sale_order_tag_rel', 'order_id', 'tag_id', string='Tags')
    customer_tag_id = fields.Many2many('customer.tag', 'customer_tag_res_partner_rel')
    contact_tags = fields.Many2many('res.partner.category', string="Contact Tags")

    combined_tag_ids = fields.Many2many(
        'your.tag.model',  # Replace 'your.tag.model' with the actual model for your tags
        'sale_order_combined_tag_rel',  # Replace with a unique name for the relationship table
        'order_id',  # Replace with the appropriate field for your model
        'tag_id',  # Replace with the appropriate field for your model
        string='Combined Tags'
    )

    @api.depends('tag_id', 'customer_tag_id', 'contact_tags')
    def _compute_combined_tags(self):
        for record in self:
            record.combined_tag_ids = record.tag_id | record.customer_tag_id | record.contact_tags
