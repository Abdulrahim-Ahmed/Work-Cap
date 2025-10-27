from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosManualInventory(models.Model):
    _name = 'pos.manual.inventory'
    _description = 'POS Manual Inventory Adjustment'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now,
        readonly=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='Created by',
        required=True,
        default=lambda self: self.env.user,
        readonly=True
    )

    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        domain=lambda self: self._get_location_domain(),
        default=lambda self: self._get_default_location(),
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('counted', 'Counted'),
        ('submitted', 'Submitted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', readonly=True)

    line_ids = fields.One2many(
        'pos.manual.inventory.line',
        'inventory_id',
        string='Inventory Lines',
        readonly=False
    )

    notes = fields.Text(
        string='Notes',
        readonly=False
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        readonly=True
    )
    verified_sheet = fields.Binary(string="Verified Sheet")

    products_in_location_ids = fields.Many2many(
        'product.product',
        string='Products in Location',
        compute='_compute_products_in_location',
        store=False
    )

    def _get_pos_default_location(self):
        """Return the default source location from POS picking type."""
        # Get the picking type used for POS operations
        pos_config = self.env['pos.config'].search([], limit=1)
        return pos_config.picking_type_id.default_location_src_id if pos_config.picking_type_id else False

    def _get_location_domain(self):
        """Return domain for location_id field based on user's assigned locations and permissions."""
        user = self.env.user
        
        # Check if user is admin for manual inventory
        is_admin = user.has_group('pos_manual_inventory_adjustment.group_manual_inventory_admin')
        
        if is_admin:
            # Admin can see all internal locations
            return [('usage', '=', 'internal')]
        else:
            # Regular user - check if user has assigned stock locations from dvit_warehouse_stock_restrictions
            if hasattr(user, 'stock_location_ids') and user.stock_location_ids:
                # Filter locations based on user's assigned locations
                return [('id', 'in', user.stock_location_ids.ids)]
            else:
                # Fallback to POS default location if no restrictions
                pos_location = self._get_pos_default_location()
                if pos_location:
                    return [('id', '=', pos_location.id)]
                else:
                    # No restrictions, allow all stock locations (fallback)
                    return [('usage', '=', 'internal')]

    def _get_default_location(self):
        """Return default location based on user's assigned locations, permissions, or POS config."""
        user = self.env.user
        
        # Check if user is admin for manual inventory
        is_admin = user.has_group('pos_manual_inventory_adjustment.group_manual_inventory_admin')
        
        if is_admin:
            # Admin - use POS default location or first internal location
            pos_location = self._get_pos_default_location()
            if pos_location:
                return pos_location.id
            else:
                # Get first internal location as fallback
                internal_location = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
                return internal_location.id if internal_location else False
        else:
            # Regular user - check if user has assigned stock locations
            if hasattr(user, 'stock_location_ids') and user.stock_location_ids:
                # Return the first assigned location as default
                return user.stock_location_ids[0].id if user.stock_location_ids else False
            else:
                # Fallback to POS default location
                pos_location = self._get_pos_default_location()
                return pos_location.id if pos_location else False

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pos.manual.inventory') or _('New')
        return super().create(vals)

    def action_count(self):
        """Mark the inventory as counted"""
        if not self.line_ids:
            raise ValidationError(_("Please add at least one product line before marking as counted."))
        self.state = 'counted'

    def action_print_sheet(self):
        """Print the inventory count sheet"""
        return self.env.ref('pos_manual_inventory_adjustment.report_inventory_count_sheet').report_action(self)

    def action_submit(self):
        """Submit the inventory and create standard inventory adjustments"""
        if self.state != 'counted':
            raise ValidationError(_("Inventory must be counted before submitting."))

        if not self.line_ids:
            raise ValidationError(_("Cannot submit inventory without any lines."))

        # Create inventory adjustments through stock.quant
        for line in self.line_ids.filtered(lambda l: l.counted_qty != l.theoretical_qty):
            quant = self.env['stock.quant'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id', '=', self.location_id.id)
            ], limit=1)

            if not quant:
                # Create new quant if it doesn't exist
                quant = self.env['stock.quant'].create({
                    'product_id': line.product_id.id,
                    'location_id': self.location_id.id,
                    'quantity': 0.0,
                })

            # Set inventory quantity and apply
            quant.inventory_quantity = line.counted_qty
            quant.inventory_quantity_set = True
            quant.with_context(inventory_name=f"POS Manual Count - {self.name}").action_apply_inventory()

        self.state = 'submitted'

    def action_cancel(self):
        """Cancel the inventory"""
        if self.state == 'submitted':
            raise ValidationError(_("Cannot cancel a submitted inventory."))
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        """Reset to draft state"""
        if self.state == 'submitted':
            raise ValidationError(_("Cannot reset a submitted inventory to draft."))
        self.state = 'draft'

    @api.depends('location_id')
    def _compute_products_in_location(self):
        """Compute products that have stock in the specified location"""
        for record in self:
            if record.location_id:
                # Get products that have stock quants in this location (including zero quantities for complete inventory)
                quants = self.env['stock.quant'].search([
                    ('location_id', '=', record.location_id.id),
                ])
                record.products_in_location_ids = quants.mapped('product_id')
            else:
                record.products_in_location_ids = False

    def _get_products_in_location(self, location_id):
        """Get products that have stock in the specified location"""
        if not location_id:
            return []

        # Get products that have stock quants in this location (including zero quantities for complete inventory)
        quants = self.env['stock.quant'].search([
            ('location_id', '=', location_id),
        ])
        return quants.mapped('product_id').ids
