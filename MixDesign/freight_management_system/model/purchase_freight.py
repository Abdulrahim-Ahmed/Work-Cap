# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.float_utils import float_compare, float_round


class PurchaseFreightCycle(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    freight_order_id = fields.Many2one(
        'freight.order',
        string='Freight Order',
        help='Select the Freight Order associated with this Purchase Order'
    )
    freight_count = fields.Integer(compute='_compute_freight_count', string="Freight Orders")
    mix_design_ref = fields.Char(string="MixDesign UAE Ref", required=False, store=True)
    one_thousand = fields.Float(string="1/1000", related='freight_order_id.one_thousand', store=True, readonly=True)

    # def _compute_freight_count(self):
    #     for record in self:
    #         record.freight_count = self.env['freight.order'].search_count([('id', '=', record.freight_order_id.id)])

    def _compute_freight_count(self):
        for record in self:
            # Count ALL freight orders related to this purchase order (not just the main one)
            record.freight_count = self.env['freight.order'].search_count([
                '|',
                ('id', '=', record.freight_order_id.id),
                ('purchase_order_id', '=', record.id)
            ])

    def action_view_freight_orders(self):
        # Show ALL freight orders related to this purchase order
        freight_orders = self.env['freight.order'].search([
            '|',
            ('id', '=', self.freight_order_id.id),
            ('purchase_order_id', '=', self.id)
        ])

        return {
            'name': 'Freight Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'freight.order',
            'domain': [('id', 'in', freight_orders.ids)],
            'context': {'create': False},
        }

    # def action_view_freight_orders(self):
    #     return {
    #         'name': 'Freight Orders',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'list,form',
    #         'res_model': 'freight.order',
    #         'domain': [('id', '=', self.freight_order_id.id)],
    #         'context': {'create': False},  # Prevent creating new records from this view
    #     }

    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'

    def action_confirm_po(self):
        self.ensure_one()

        # Create wizard and its lines
        wizard = self.env['purchase.order.line.wizard'].create({
            'purchase_order_id': self.id,
            'line_ids': [  # <- Change made here
                (0, 0, {
                    'order_line_id': line.id,
                    'product_id': line.product_id.id,
                    'remaining_qty': line.remaining_qty,
                    'shipment_quantity': line.shipment_quantity,
                    'secondary_uom_id': line.secondary_uom_id.id,
                    'secondary_quantity': line.secondary_quantity,
                    'pre_quantity': line.pre_quantity,
                    'gross_weight': line.gross_weight,
                    'net_weight': line.net_weight,
                    'price_unit': line.price_unit,
                }) for line in self.order_line
            ]
        })

        # Return action to open the wizard
        return {
            'name': 'Confirm Purchase Order Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('freight_management_system.purchase_order_line_wizard_form').id,
            'target': 'new',
            'res_id': wizard.id,
        }


class PurchaseFreightCycleLine(models.Model):
    _inherit = 'purchase.order.line'

    pre_quantity = fields.Float(string="Pre Quantity", required=False)
    remaining_qty = fields.Float(string="Remaining Qty", compute="_compute_remaining_qty", required=False)
    shipment_quantity = fields.Float(string="Shipment Quantity", required=False)
    product_qty = fields.Float(string='Quantity', default=0, digits='Product Unit of Measure', required=True,
                               compute='_compute_product_qty', store=True, readonly=False)
    gross_weight = fields.Float(string="Gross Weight per Unit", store=True)
    net_weight = fields.Float(string="Net Weight per Unit", store=True)

    @api.onchange('product_id')
    def _onchange_product_id_set_weights(self):
        """Fetch gross & net weight from product when product is selected"""
        for line in self:
            if line.product_id:
                line.gross_weight = line.product_id.weight
                line.net_weight = line.product_id.net_weight

    @api.depends('product_packaging_qty')
    def _compute_product_qty(self):
        for line in self:
            if line.product_packaging_id:
                packaging_uom = line.product_packaging_id.product_uom_id
                qty_per_packaging = line.product_packaging_id.qty
                product_qty = packaging_uom._compute_quantity(line.product_packaging_qty * qty_per_packaging,
                                                              line.product_uom)
                if float_compare(product_qty, line.product_qty, precision_rounding=line.product_uom.rounding) != 0:
                    line.product_qty = product_qty

    @api.depends('product_qty', 'shipment_quantity')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.product_qty - (line.shipment_quantity or 0.0)
