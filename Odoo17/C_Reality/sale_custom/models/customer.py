from odoo import api, fields, models
from odoo.osv import expression
from random import randint


class CustomerTag(models.Model):
    _name = 'customer.tag'
    _description = 'Customer Tag'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Tag Name', required=True, translate=True)
    partner_ids = fields.Many2many('res.partner', 'customer_tag_res_partner_rel', string='Customers')
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tag_ids = fields.Many2many('customer.tag', 'customer_tag_res_partner_rel', string='Know Us From')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tag_ids = fields.Many2many('customer.tag', string='Customer Know us', compute='_compute_tag_ids', readonly=False)

    @api.depends('partner_id.tag_ids')
    def _compute_tag_ids(self):
        for order in self:
            order.tag_ids = order.partner_id.tag_ids

    @api.model
    def create(self, vals):
        # Call the original create method first
        order = super(SaleOrder, self).create(vals)

        # Update the tags for the related customer if 'tag_ids' are present in vals
        if vals.get('tag_ids') and order.partner_id:
            order.partner_id.tag_ids = [(6, 0, vals['tag_ids'][0][2])]

        return order

    def write(self, vals):
        # Call the original write method first
        result = super(SaleOrder, self).write(vals)

        # Update the tags for the related customer if 'tag_ids' are present in vals
        if vals.get('tag_ids'):
            for order in self:
                if order.partner_id:
                    order.partner_id.tag_ids = [(6, 0, vals['tag_ids'][0][2])]

        return result
