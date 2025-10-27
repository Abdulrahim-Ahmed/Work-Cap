from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrderLineWizard(models.TransientModel):
    _name = 'purchase.order.line.wizard'
    _description = 'Purchase Order Line Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", readonly=True)
    line_ids = fields.One2many('purchase.order.line.wizard.line', 'wizard_id', string="Order Lines")
    existing_freight = fields.Selection([
        ('new', 'New Freight'),
        ('existing', 'Existing Freight'),
    ], string='New', tracking=True)
    freight_order_id = fields.Many2one(
        'freight.order',
        string='Freight Order',
        help='Select the Freight Order associated with this Purchase Order'
    )
    shipper_id = fields.Many2one('res.partner', string='Shipper', required=False,
                                 help="Shipper's Details")
    loading_port_id = fields.Many2one('freight.port', string="Loading Port",
                                      required=False,
                                      help="Loading port of the freight order")
    agent_id = fields.Many2one('res.partner', string='Agent',
                               required=False, help="Details of agent")
    type = fields.Selection([('import', 'Import'), ('export', 'Export')],
                            string='Import/Export', required=False,
                            help="Type of freight operation")
    import_type = fields.Selection(string="Import Type",
                                   selection=[('import_egypt_free_zone', 'Import Egypt Free Zone'),
                                              ('import_offshore', 'Import OffShore'), ], tracking=True, required=False)
    export_type = fields.Selection(string="Export Type",
                                   selection=[('export_free_zone', 'Export Free Zone'),
                                              ('export_temporary', 'Export Temporary'),
                                              ('export_local_market', 'Export Local Market'),
                                              ('export_global', 'Export Global'), ], tracking=True, required=False)
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water'), ('warehouse_pickup', 'Warehouse Pickup')],
                                      string='Transport',
                                      help='Type of transportation',
                                      required=False)
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port",
                                          required=False,
                                          help="Discharging port of freight"
                                               "order")
    plan_field = fields.Many2one('freight.management', string="Plan", required=False)

    def action_confirm_lines(self):
        """ Confirm the lines and update Purchase Order lines """
        FreightOrder = self.env['freight.order']
        FreightOrderLine = self.env['freight.order.line']

        new_freight = False

        if self.existing_freight == 'new':
            # Create a new freight order with purchase order reference
            new_freight = FreightOrder.create({
                'shipper_id': self.shipper_id.id,
                'agent_id': self.agent_id.id,
                'type': self.type,
                'import_type': self.import_type,
                'export_type': self.export_type,
                'transport_type': self.transport_type,
                'loading_port_id': self.loading_port_id.id,
                'discharging_port_id': self.discharging_port_id.id,
                'plan_field': self.plan_field.id,
                # Add purchase order reference to the freight order
                'purchase_order_id': self.purchase_order_id.id,  # Make sure your freight.order model has this field
            })

        elif self.existing_freight == 'existing' and self.freight_order_id:
            # Use the selected existing freight order
            new_freight = self.freight_order_id

        # ✅ Only link the Purchase Order to the FIRST freight order created (for main reference)
        if new_freight and not self.purchase_order_id.freight_order_id:
            self.purchase_order_id.freight_order_id = new_freight.id

        # Validate all lines before processing
        for line in self.line_ids:
            # Check if shipment quantity is set and greater than zero
            if not line.shipment_quantity or line.shipment_quantity <= 0:
                raise ValidationError(_(
                    "Shipment Quantity must be set and greater than zero for all lines before confirming."
                ))

            # Check if shipment quantity exceeds remaining quantity
            remaining_qty = line.order_line_id.product_qty - (line.order_line_id.shipment_quantity or 0)
            if line.shipment_quantity > remaining_qty:
                raise ValidationError(_(
                    "Shipment Quantity (%.2f) cannot exceed the remaining quantity (%.2f) for product '%s'."
                ) % (line.shipment_quantity, remaining_qty, line.order_line_id.product_id.name))

        # Process all lines after validation passes
        for line in self.line_ids:
            if line.shipment_quantity:
                # Update the related purchase order line's shipment quantity (accumulate, don't replace)
                line.order_line_id.shipment_quantity = (
                                                                   line.order_line_id.shipment_quantity or 0) + line.shipment_quantity
                line.order_line_id.gross_weight = line.gross_weight
                line.order_line_id.net_weight = line.net_weight
                line.order_line_id.pre_quantity = line.pre_quantity
                line.order_line_id.price_unit = line.price_unit
                line.order_line_id.secondary_uom_id = line.secondary_uom_id
                line.order_line_id.secondary_quantity = line.secondary_quantity

                if new_freight:
                    # Check if the product already exists in Freight Order Lines
                    existing_line = FreightOrderLine.search([
                        ('order_id', '=', new_freight.id),
                        ('product_id', '=', line.order_line_id.product_id.id)
                    ], limit=1)

                    if existing_line:
                        # Update the existing line's shipment quantity
                        existing_line.product_qty += line.shipment_quantity
                    else:
                        # Create a new freight order line if not found
                        FreightOrderLine.create({
                            'order_id': new_freight.id,
                            'product_id': line.order_line_id.product_id.id,
                            'product_qty': line.shipment_quantity,
                            'price': line.price_unit,
                            'weight': line.gross_weight,
                            'net_weight': line.net_weight,
                            'secondary_uom_id': line.secondary_uom_id.id,
                            'secondary_quantity': line.secondary_quantity,
                        })

    # def action_confirm_lines(self):
    #     """ Confirm the lines and update Purchase Order lines """
    #     FreightOrder = self.env['freight.order']
    #     FreightOrderLine = self.env['freight.order.line']
    #
    #     new_freight = False
    #
    #     if self.existing_freight == 'new':
    #         # Create a new freight order
    #         new_freight = FreightOrder.create({
    #             'shipper_id': self.shipper_id.id,
    #             'agent_id': self.agent_id.id,
    #             'type': self.type,
    #             'import_type': self.import_type,
    #             'export_type': self.export_type,
    #             'transport_type': self.transport_type,
    #             'loading_port_id': self.loading_port_id.id,
    #             'discharging_port_id': self.discharging_port_id.id,
    #             'plan_field': self.plan_field.id,
    #         })
    #         self.freight_order_id = new_freight.id
    #
    #     elif self.existing_freight == 'existing' and self.freight_order_id:
    #         # Use the selected existing freight order
    #         new_freight = self.freight_order_id
    #
    #     # ✅ Ensure the Purchase Order is linked to the Freight Order
    #     if new_freight:
    #         self.purchase_order_id.freight_order_id = new_freight.id
    #
    #     # Validate all lines before processing
    #     for line in self.line_ids:
    #         # Check if shipment quantity is set and greater than zero
    #         if not line.shipment_quantity or line.shipment_quantity <= 0:
    #             raise ValidationError(_(
    #                 "Shipment Quantity must be set and greater than zero for all lines before confirming."
    #             ))
    #
    #         # Check if shipment quantity exceeds remaining quantity
    #         remaining_qty = line.order_line_id.product_qty - (line.order_line_id.shipment_quantity or 0)
    #         if line.shipment_quantity > remaining_qty:
    #             raise ValidationError(_(
    #                 "Shipment Quantity (%.2f) cannot exceed the remaining quantity (%.2f) for product '%s'."
    #             ) % (line.shipment_quantity, remaining_qty, line.order_line_id.product_id.name))
    #
    #     # Process all lines after validation passes
    #     for line in self.line_ids:
    #         if line.shipment_quantity:
    #             # Update the related purchase order line's product_qty with pre_quantity
    #             # line.order_line_id.product_qty = line.shipment_quantity
    #             line.order_line_id.shipment_quantity = line.shipment_quantity
    #             line.order_line_id.pre_quantity = line.pre_quantity
    #             line.order_line_id.price_unit = line.price_unit
    #
    #             if new_freight:
    #                 # Check if the product already exists in Freight Order Lines
    #                 existing_line = FreightOrderLine.search([
    #                     ('order_id', '=', new_freight.id),
    #                     ('product_id', '=', line.order_line_id.product_id.id)
    #                 ], limit=1)
    #
    #                 if existing_line:
    #                     # Update the existing line's shipment quantity
    #                     existing_line.product_qty += line.shipment_quantity
    #                 else:
    #                     # Create a new freight order line if not found
    #                     FreightOrderLine.create({
    #                         'order_id': new_freight.id,
    #                         'product_id': line.order_line_id.product_id.id,
    #                         'product_qty': line.shipment_quantity,
    #                         'price': line.price_unit,
    #                     })

    # def action_confirm_lines(self):
    #     """ Confirm the lines and update Purchase Order lines """
    #     FreightOrder = self.env['freight.order']
    #     FreightOrderLine = self.env['freight.order.line']
    #
    #     new_freight = False
    #
    #     if self.existing_freight == 'new':
    #         # Create a new freight order
    #         new_freight = FreightOrder.create({
    #             'shipper_id': self.shipper_id.id,
    #             'agent_id': self.agent_id.id,
    #             'type': self.type,
    #             'import_type': self.import_type,
    #             'export_type': self.export_type,
    #             'transport_type': self.transport_type,
    #             'loading_port_id': self.loading_port_id.id,
    #             'discharging_port_id': self.discharging_port_id.id,
    #             'plan_field': self.plan_field.id,
    #         })
    #         self.freight_order_id = new_freight.id
    #
    #     elif self.existing_freight == 'existing' and self.freight_order_id:
    #         # Use the selected existing freight order
    #         new_freight = self.freight_order_id
    #
    #     # ✅ Ensure the Purchase Order is linked to the Freight Order
    #     if new_freight:
    #         self.purchase_order_id.freight_order_id = new_freight.id
    #
    #     for line in self.line_ids:
    #         if line.shipment_quantity:
    #             # Update the related purchase order line's product_qty with pre_quantity
    #             # line.order_line_id.product_qty = line.shipment_quantity
    #             line.order_line_id.shipment_quantity = line.shipment_quantity
    #             line.order_line_id.pre_quantity = line.pre_quantity
    #             line.order_line_id.price_unit = line.price_unit
    #
    #             if new_freight:
    #                 # Check if the product already exists in Freight Order Lines
    #                 existing_line = FreightOrderLine.search([
    #                     ('order_id', '=', new_freight.id),
    #                     ('product_id', '=', line.order_line_id.product_id.id)
    #                 ], limit=1)
    #
    #                 if existing_line:
    #                     # Update the existing line's shipment quantity
    #                     existing_line.product_qty += line.shipment_quantity
    #                 else:
    #                     # Create a new freight order line if not found
    #                     FreightOrderLine.create({
    #                         'order_id': new_freight.id,
    #                         'product_id': line.order_line_id.product_id.id,
    #                         'product_qty': line.shipment_quantity,
    #                         'price': line.price_unit,
    #                     })
    #         if not line.shipment_quantity or line.shipment_quantity <= 0:
    #             raise ValidationError(_(
    #                 "Shipment Quantity must be set and greater than zero for all lines before confirming."
    #             ))


class PurchaseOrderLineWizardLine(models.TransientModel):
    _name = 'purchase.order.line.wizard.line'
    _description = 'Purchase Order Line Wizard Line'

    wizard_id = fields.Many2one('purchase.order.line.wizard', string="Wizard", required=True, ondelete='cascade')
    order_line_id = fields.Many2one('purchase.order.line', string="Order Line", readonly=True)
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    # product_qty = fields.Float(string="Quantity", readonly=True)
    shipment_quantity = fields.Float(string="Shipment Quantity", required=False)
    pre_quantity = fields.Float(string="Pre Quantity", required=False)
    price_unit = fields.Float(string="Unit Price", required=True)
    remaining_qty = fields.Float(string="Remaining Qty", required=True)
    gross_weight = fields.Float(string="Gross Weight per Unit", store=True)
    net_weight = fields.Float(string="Net Weight per Unit", store=True)
    secondary_uom_id = fields.Many2one('uom.uom', string="ALT UOM")
    secondary_quantity = fields.Float('ALT Qty', digits='Product Unit of Measure')
