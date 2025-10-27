from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosManualInventoryLine(models.Model):
    _name = 'pos.manual.inventory.line'
    _description = 'POS Manual Inventory Line'
    _rec_name = 'product_id'

    inventory_id = fields.Many2one(
        'pos.manual.inventory',
        string='Inventory Adjustment',
        required=True,
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )

    product_barcode = fields.Char(
        related='product_id.barcode',
        string='Barcode',
        readonly=True
    )

    product_uom_id = fields.Many2one(
        related='product_id.uom_id',
        string='Unit of Measure',
        readonly=True
    )

    theoretical_qty = fields.Float(
        string='Theoretical Quantity',
        compute='_compute_theoretical_qty',
        store=True,
        readonly=True
    )

    counted_qty = fields.Float(
        string='Counted Quantity',
        default=0.0,
        required=True
    )

    difference = fields.Float(
        string='Difference',
        compute='_compute_difference',
        store=True,
        readonly=True
    )

    location_id = fields.Many2one(
        related='inventory_id.location_id',
        string='Location',
        readonly=True
    )

    state = fields.Selection(
        related='inventory_id.state',
        string='Status',
        readonly=True
    )

    @api.depends('product_id', 'location_id')
    def _compute_theoretical_qty(self):
        """Compute theoretical quantity from stock quants"""
        for line in self:
            if line.product_id and line.location_id:
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.location_id.id)
                ], limit=1)
                line.theoretical_qty = quant.quantity if quant else 0.0
            else:
                line.theoretical_qty = 0.0

    @api.depends('theoretical_qty', 'counted_qty')
    def _compute_difference(self):
        """Compute difference between counted and theoretical quantities"""
        for line in self:
            line.difference = line.counted_qty - line.theoretical_qty

    @api.constrains('counted_qty')
    def _check_counted_qty(self):
        """Validate counted quantity"""
        for line in self:
            if line.counted_qty < 0:
                raise ValidationError(_("Counted quantity cannot be negative."))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Reset counted quantity when product changes"""
        if self.product_id:
            self.counted_qty = 0.0