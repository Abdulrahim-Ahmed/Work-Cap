from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLineWizard(models.TransientModel):
    _name = 'sale.order.line.wizard'
    _description = 'Sales Order Line Wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    line_ids = fields.One2many('sale.order.line.wizard.line', 'wizard_id', string="Order Lines")
    existing_freight = fields.Selection([
        ('new', 'New Freight'),
        ('existing', 'Existing Freight'),
    ], string='Freight Option', tracking=True)
    freight_order_id = fields.Many2one('freight.order', string='Freight Order')
    shipper_id = fields.Many2one('res.partner', string='Shipper', required=False)
    loading_port_id = fields.Many2one('freight.port', string="Loading Port", required=False)
    agent_id = fields.Many2one('res.partner', string='Agent', required=False)
    type = fields.Selection([('import', 'Import'), ('export', 'Export')], string='Import/Export', required=False)
    import_type = fields.Selection(string="Import Type",
                                   selection=[('import_egypt_free_zone', 'Import Egypt Free Zone'),
                                              ('import_offshore', 'Import OffShore'), ], tracking=True, required=False)
    export_type = fields.Selection(string="Export Type",
                                   selection=[('export_free_zone', 'Export Free Zone'),
                                              ('export_temporary', 'Export Temporary'),
                                              ('export_local_market', 'Export Local Market'),
                                              ('export_global', 'Export Global'), ], tracking=True, required=False)
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'), ('water', 'Water'),
                                       ('warehouse_pickup', 'Warehouse Pickup')], string='Transport',
                                      required=False)
    discharging_port_id = fields.Many2one('freight.port', string="Discharging Port", required=False)
    plan_field = fields.Many2one('freight.management', string="Plan", required=False)
    incoterm = fields.Many2one('account.incoterms', 'Incoterm',
                               help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    incoterm_location = fields.Char(string='Incoterm Location')

    def action_confirm_lines(self):
        """ Confirm and update Sales Order Lines """
        FreightOrder = self.env['freight.order']
        FreightOrderLine = self.env['freight.order.line']

        new_freight = False

        if self.existing_freight == 'new':
            # Create a new freight order with sales order reference
            new_freight = FreightOrder.create({
                'shipper_id': self.shipper_id.id,
                'agent_id': self.agent_id.id,
                'type': self.type,
                'import_type': self.import_type,
                'export_type': self.export_type,
                'transport_type': self.transport_type,
                'loading_port_id': self.loading_port_id.id,
                # 'product_display_name': self.product_display_name,
                'incoterm': self.incoterm.id,
                'incoterm_location': self.incoterm_location,
                'discharging_port_id': self.discharging_port_id.id,
                'plan_field': self.plan_field.id,
                # Add sales order reference to the freight order
                'sale_order_id': self.sale_order_id.id,  # Make sure your freight.order model has this field
            })
            # Don't automatically link to sales order anymore - allow multiple freights
            # self.freight_order_id = new_freight.id

        elif self.existing_freight == 'existing' and self.freight_order_id:
            new_freight = self.freight_order_id

        # ✅ Only link the Sales Order to the FIRST freight order created (for main reference)
        if new_freight and not self.sale_order_id.freight_order_id:
            self.sale_order_id.freight_order_id = new_freight.id

        # Validate all lines before processing
        for line in self.line_ids:
            # Check if shipment quantity is set and greater than zero
            if not line.shipment_quantity or line.shipment_quantity <= 0:
                raise ValidationError(_(
                    "Shipment Quantity must be set and greater than zero for all lines before confirming."
                ))

            # Check if shipment quantity exceeds remaining quantity (if you have remaining_qty field)
            # Adjust this validation based on your sales order line fields
            remaining_qty = line.order_line_id.product_uom_qty - (line.order_line_id.shipment_quantity or 0)
            if line.shipment_quantity > remaining_qty:
                raise ValidationError(_(
                    "Shipment Quantity (%.2f) cannot exceed the remaining quantity (%.2f) for product '%s'."
                ) % (line.shipment_quantity, remaining_qty, line.order_line_id.product_id.name))

        # Process all lines after validation passes
        for line in self.line_ids:
            if line.shipment_quantity:
                # Update the related sales order line's shipment quantity (accumulate, don't replace)
                line.order_line_id.shipment_quantity = (
                                                               line.order_line_id.shipment_quantity or 0) + line.shipment_quantity
                line.order_line_id.gross_weight = line.gross_weight
                line.order_line_id.net_weight = line.net_weight
                line.order_line_id.secondary_uom_id = line.secondary_uom_id
                line.order_line_id.secondary_quantity = line.secondary_quantity
                line.order_line_id.pre_quantity = line.pre_quantity
                line.order_line_id.price_unit = line.price_unit

                existing_line = FreightOrderLine.search([
                    ('order_id', '=', new_freight.id),
                    ('product_id', '=', line.order_line_id.product_id.id)
                ], limit=1)

                if existing_line:
                    existing_line.product_qty += line.shipment_quantity
                else:
                    FreightOrderLine.create({
                        'order_id': new_freight.id,
                        'product_id': line.order_line_id.product_id.id,
                        'product_display_name': line.product_display_name,
                        'secondary_uom_id': line.secondary_uom_id.id,
                        'secondary_quantity': line.secondary_quantity,
                        'product_qty': line.shipment_quantity,
                        'price': line.price_unit,
                        'weight': line.gross_weight,
                        'net_weight': line.net_weight,
                    })

    # def action_confirm_lines(self):
    #     """ Confirm and update Sales Order Lines """
    #     FreightOrder = self.env['freight.order']
    #     FreightOrderLine = self.env['freight.order.line']
    #
    #     new_freight = False
    #
    #     if self.existing_freight == 'new':
    #         new_freight = FreightOrder.create({
    #             'shipper_id': self.shipper_id.id,
    #             'agent_id': self.agent_id.id,
    #             'type': self.type,
    #             'import_type': self.import_type,
    #             'export_type': self.export_type,
    #             'transport_type': self.transport_type,
    #             'loading_port_id': self.loading_port_id.id,
    #             # 'product_display_name': self.product_display_name,
    #             'incoterm': self.incoterm.id,
    #             'incoterm_location': self.incoterm_location,
    #             'discharging_port_id': self.discharging_port_id.id,
    #             'plan_field': self.plan_field.id,
    #         })
    #         self.freight_order_id = new_freight.id
    #     elif self.existing_freight == 'existing' and self.freight_order_id:
    #         new_freight = self.freight_order_id
    #
    #     if new_freight:
    #         self.sale_order_id.freight_order_id = new_freight.id
    #
    #     for line in self.line_ids:
    #         if line.shipment_quantity:
    #             # line.order_line_id.product_uom_qty = line.shipment_quantity
    #             line.order_line_id.shipment_quantity = line.shipment_quantity
    #             line.order_line_id.gross_weight = line.gross_weight
    #             line.order_line_id.net_weight = line.net_weight
    #             line.order_line_id.pre_quantity = line.pre_quantity
    #             line.order_line_id.price_unit = line.price_unit
    #
    #             existing_line = FreightOrderLine.search([
    #                 ('order_id', '=', new_freight.id),
    #                 ('product_id', '=', line.order_line_id.product_id.id)
    #             ], limit=1)
    #
    #             if existing_line:
    #                 existing_line.product_qty += line.shipment_quantity
    #             else:
    #                 FreightOrderLine.create({
    #                     'order_id': new_freight.id,
    #                     'product_id': line.order_line_id.product_id.id,
    #                     'product_display_name': line.product_display_name,
    #                     'product_qty': line.shipment_quantity,
    #                     'price': line.price_unit,
    #                     'weight': line.gross_weight,
    #                     'net_weight': line.net_weight,
    #                 })

    # self.sale_order_id.state = 'confirmed_so'


class SaleOrderLineWizardLine(models.TransientModel):
    _name = 'sale.order.line.wizard.line'
    _description = 'Sales Order Line Wizard Line'

    wizard_id = fields.Many2one('sale.order.line.wizard', string="Wizard", required=True, ondelete='cascade')
    order_line_id = fields.Many2one('sale.order.line', string="Order Line", readonly=True)
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    shipment_quantity = fields.Float(string="Shipment Quantity")
    pre_quantity = fields.Float(string="Pre Quantity")
    price_unit = fields.Float(string="Unit Price", required=True)
    gross_weight = fields.Float(string="Gross Weight per Unit", store=True)
    net_weight = fields.Float(string="Net Weight per Unit", store=True)
    product_display_name = fields.Char(string="Product Description")
    remaining_qty = fields.Float(string="Remaining Qty", required=False)
    secondary_uom_id = fields.Many2one('uom.uom', string="ALT UOM", readonly=False, store=True)
    secondary_quantity = fields.Float('ALT Qty', digits='Product Unit of Measure', readonly=False, store=True)


class SaleOrderFreightCycle(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    freight_order_id = fields.Many2one('freight.order', string='Freight Order')
    freight_count = fields.Integer(compute='_compute_freight_count', string="Freight Orders")
    freight_line_ids = fields.One2many('sale.order.freight.line', 'sale_order_id', string="Freight Details")
    is_export_temporary = fields.Boolean('Export Temporary')

    def _prepare_delivery_vals(self):
        res = super()._prepare_delivery_vals()
        res['is_export_temporary'] = self.is_export_temporary
        return res

    def _compute_freight_count(self):
        for record in self:
            # Count ALL freight orders related to this sales order (not just the main one)
            record.freight_count = self.env['freight.order'].search_count([
                '|',
                ('id', '=', record.freight_order_id.id),
                ('sale_order_id', '=', record.id)
            ])

    # def _compute_freight_count(self):
    #     for record in self:
    #         record.freight_count = self.env['freight.order'].search_count([('id', '=', record.freight_order_id.id)])

    def action_confirm_so(self):
        """ Open the wizard for confirming Sales Order Lines """
        wizard = self.env['sale.order.line.wizard'].create({
            'sale_order_id': self.id,
            'line_ids': [
                (0, 0, {
                    'order_line_id': line.id,
                    'product_id': line.product_id.id,
                    'shipment_quantity': line.product_uom_qty,
                    'remaining_qty': line.remaining_qty,
                    'product_display_name': line.name,
                    'gross_weight': line.gross_weight,
                    'secondary_uom_id': line.secondary_uom_id.id,
                    'secondary_quantity': line.secondary_quantity,
                    'net_weight': line.net_weight,
                    'pre_quantity': line.pre_quantity,
                    'price_unit': line.price_unit,
                }) for line in self.order_line
            ]
        })

        return {
            'name': 'Confirm Sales Order Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('freight_management_system.view_sale_order_line_wizard_form').id,
            'target': 'new',
            'res_id': wizard.id,
        }

    def action_view_freight_orders(self):
        # Show ALL freight orders related to this sales order
        freight_orders = self.env['freight.order'].search([
            '|',
            ('id', '=', self.freight_order_id.id),
            ('sale_order_id', '=', self.id)
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

    # def action_reset_to_draft(self):
    #     for record in self:
    #         record.state = 'draft'


class SaleOrderFreightCycleLine(models.Model):
    _inherit = 'sale.order.line'

    pre_quantity = fields.Float(string="Pre Quantity")
    shipment_quantity = fields.Float(string="Shipment Quantity")
    remaining_qty = fields.Float(string="Remaining Qty", compute="_compute_remaining_qty", required=False)
    gross_weight = fields.Float(string="Gross Weight per Unit", store=True)
    net_weight = fields.Float(string="Net Weight per Unit", store=True)

    @api.depends('product_uom_qty', 'shipment_quantity')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.product_uom_qty - (line.shipment_quantity or 0.0)

    # Adding Wight To Sale order line inorder to inherit it to freight via sale wizard
    @api.onchange('product_id')
    def _onchange_product_id_set_weights(self):
        for line in self:
            tmpl = line.product_id.product_tmpl_id
            line.gross_weight = tmpl.weight or 0.0
            line.net_weight = tmpl.net_weight or 0.0


class SaleOrderFreightLine(models.Model):
    _name = 'sale.order.freight.line'
    _description = 'Sale Order Freight Line'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", ondelete="cascade")
    product_template_id = fields.Many2one('product.template', string="Product", required=True,
                                          domain="[('id', 'in', available_product_templates)]",
                                          help="Select a product from the order lines")
    available_product_templates = fields.Many2many(
        'product.template',
        compute="_compute_available_products",
        store=False)
    outgoing_number = fields.Char(string="Outgoing Number")
    incoming_number = fields.Char(string="Incoming Number")
    date_field = fields.Date(string="Date")

    @api.depends('sale_order_id')
    def _compute_available_products(self):
        """Compute available product templates based on sale order lines"""
        for record in self:
            if record.sale_order_id:
                product_templates = record.sale_order_id.order_line.mapped('product_id.product_tmpl_id')
                record.available_product_templates = product_templates
            else:
                record.available_product_templates = False
