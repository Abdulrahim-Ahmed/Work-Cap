# -*- coding: utf-8 -*-
from email.policy import default
from odoo.exceptions import UserError
from odoo import models, fields, api
from odoo.tools import float_compare
from datetime import timedelta
from odoo.addons.sale_stock.models.sale_order_line import SaleOrderLine
from odoo.tools.misc import groupby
from odoo.addons.stock.models.stock_move import StockMove
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    grn = fields.Char(string="GRN", related="picking_id.grn_inv", readonly=False, required=False)

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a
        new picking to assign them to. """
        grouped_moves = groupby(self, key=lambda m: m._key_assign_picking())
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*moves)
            new_picking = False
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            picking = moves[0]._search_picking_for_assignation()
            if picking:
                # If a picking is found, we'll append `move` to its move list
                # and thus its `partner_id` and `ref` field will refer to
                # multiple records.
                # In this case, we chose to wipe them.
                vals = {}
                if any(picking.partner_id.id != m.partner_id.id
                       for m in moves):
                    vals['partner_id'] = False
                if any(picking.origin != m.origin for m in moves):
                    vals['origin'] = False
                if vals:
                    picking.write(vals)
            else:
                # Don't create picking for negative moves since they will be
                # reverse and assign to another picking
                moves = moves.filtered(lambda m: float_compare(
                    m.product_uom_qty, 0.0, precision_rounding=
                    m.product_uom.rounding) >= 0)
                if not moves:
                    continue
                new_picking = True
                pick_values = moves._get_new_picking_values()
                sale_order = self.env['sale.order'].search([
                    ('name', '=', pick_values['origin'])])
                if sale_order.delivery_split and not sale_order.is_consolidate:
                    for move in moves:
                        picking = picking.create(
                            move._get_new_picking_values())
                        move.write({'picking_id': picking.id})
                        move._assign_picking_post_process(new=new_picking)
                elif sale_order.delivery_split and sale_order.is_consolidate:
                    move_line = sorted(moves,
                                       key=lambda x: x.partner_id.id)
                    for partner_id, lines in groupby(move_line,
                                                     key=lambda
                                                             x: x.partner_id):
                        new_moves = self.env['stock.move'].concat(*lines)
                        picking = picking.create(
                            new_moves._get_new_picking_values())
                        new_moves.write({'picking_id': picking.id})
                        new_moves._assign_picking_post_process(new=new_picking)

                else:
                    picking = picking.create(moves._get_new_picking_values())
                    moves.write({'picking_id': picking.id,
                                 'partner_id': sale_order.partner_id.id})
                    moves._assign_picking_post_process(new=new_picking)
        return True

    StockMove._assign_picking = _assign_picking


class StockPickingAddingField(models.Model):
    _inherit = 'stock.picking'

    grn_inv = fields.Char(string="GRN", required=False)
    is_multi_line = fields.Boolean(string="Is Multi Line", default=False, compute="_compute_is_multi_line", store=True)

    @api.depends('move_ids')
    def _compute_is_multi_line(self):
        for picking in self:
            picking.is_multi_line = len(picking.move_ids) > 1


# class SaleOrderLineWizard(models.TransientModel):
#     _inherit = 'sale.advance.payment.inv'
#
#     order_line = fields.One2many(
#         comodel_name='sale.order.line',
#         inverse_name='order_id', readonly=False,
#         string="Order Lines", compute="_compute_order_lines")
#     currency_id = fields.Many2one(
#         comodel_name='res.currency',
#         compute='_compute_currency_id')
#
#     product_template_id = fields.Many2one(
#         string="Product",
#         comodel_name='product.template',
#         compute='_compute_product',
#         readonly=False,
#         search='_search_product_template_id',
#         domain=[('sale_ok', '=', True)])
#     grn = fields.Char(string="GRN", compute='_compute_grn')
#     sale_check = fields.Boolean(string="Box", default=False, store=True)
#
#     # @api.depends('sale_order_ids')
#     # def _compute_box(self):
#     #     for wizard in self:
#     #         wizard.sale_check = wizard.sale_order_ids.sale_check
#
#     @api.depends('sale_order_ids')
#     def _compute_grn(self):
#         for wizard in self:
#             wizard.grn = wizard.sale_order_ids.grn
#
#     @api.depends('sale_order_ids')
#     def _compute_product(self):
#         for wizard in self:
#             wizard.product_template_id = wizard.sale_order_ids.product_template_id
#
#     @api.depends('sale_order_ids')
#     def _compute_currency_id(self):
#         self.currency_id = False
#         for wizard in self:
#             if wizard.count == 1:
#                 wizard.currency_id = wizard.sale_order_ids.currency_id
#
#     @api.depends('sale_order_ids')
#     def _compute_order_lines(self):
#         """Compute order lines based on selected sale orders."""
#         for wizard in self:
#             sale_orders = wizard.sale_order_ids
#             if sale_orders:
#                 wizard.order_line = [(6, 0, sale_orders.mapped('order_line').ids)]
#             else:
#                 wizard.order_line = [(5,)]
#
#     def create_invoices(self):
#         """Save `sale_check` in `sale.order.line` before creating invoices."""
#         self._check_amount_is_positive()
#
#         for wizard in self:
#             for line in wizard.order_line:
#                 sale_order_line = self.env['sale.order.line'].browse(line.id)
#                 if sale_order_line:
#                     # Save the `sale_check` value to the database
#                     sale_order_line.write({'sale_check': line.sale_check})
#                     _logger.info(
#                         f"Updated sale.order.line {sale_order_line.id} with sale_check={sale_order_line.sale_check}"
#                     )
#
#         # Create invoices for the selected lines
#         invoices = self._create_invoices(self.sale_order_ids)
#         if invoices:
#             return self.sale_order_ids.action_view_invoice(invoices=invoices)
#         else:
#             raise UserError("No eligible lines found to create an invoice.")
#
#     def _create_invoices(self, sale_orders=None):
#         """Create invoices only for lines where `sale_check=True`."""
#         invoices = self.env['account.move']
#
#         if sale_orders is None:
#             sale_orders = self.sale_order_ids
#
#         for order in sale_orders:
#             # Filter lines where sale_check is True
#             eligible_lines = order.order_line.filtered(lambda line: line.sale_check)
#
#             _logger.info(f"Processing Order: {order.name}, Eligible Lines: {eligible_lines.ids}")
#
#             if not eligible_lines:
#                 _logger.warning(f"No eligible lines found for order {order.name}, skipping invoice creation.")
#                 continue
#
#             # Prepare and create the invoice
#             invoice_vals = order._prepare_invoice()
#             invoice = self.env['account.move'].create(invoice_vals)
#
#             # Add invoice lines for the eligible lines
#             for line in eligible_lines:
#                 invoice_line_vals = line._prepare_invoice_line()
#                 invoice_line_vals['move_id'] = invoice.id
#                 self.env['account.move.line'].create(invoice_line_vals)
#
#             invoices |= invoice
#             _logger.info(f"Invoice {invoice.name} created for order {order.name} with {len(eligible_lines)} lines.")
#
#         return invoices


class SaleOrderLineCreatingDelivery(models.Model):
    _inherit = 'sale.order'

    grn = fields.Char(string="GRN")
    delivery_split = fields.Boolean(string='Delivery Split',
                                    help='Enable the option to add recipients '
                                         'to each sale order line to split '
                                         'delivery')
    is_consolidate = fields.Boolean(string='Consolidate Orders',
                                    help='Enable the option to consolidate '
                                         'orders if choose same recipients in '
                                         'split delivery')

    def action_confirm(self):
        res = super().action_confirm()

        # Set is_export_temporary on generated pickings
        for order in self:
            for picking in order.picking_ids:
                picking.is_export_temporary = order.is_export_temporary

        return res

    @api.onchange("partner_id")
    def _onchange_product_template_id(self):
        """ Update recipients in order lines with the customer of sale order
        is changed """
        if self.delivery_split:
            for line in self.order_line:
                line.recipient_id = self.partner_id.id

    # def action_confirm(self):
    #     res = super(SaleOrderLineCreatingDelivery, self).action_confirm()
    #
    #     for order in self:
    #         if not order.warehouse_id:
    #             continue
    #
    #         picking_type = order.warehouse_id.out_type_id
    #
    #         for line in order.order_line:
    #             new_picking = self.env['stock.picking'].create({
    #                 'partner_id': order.partner_shipping_id.id,
    #                 'picking_type_id': picking_type.id,
    #                 'location_id': picking_type.default_location_src_id.id,
    #                 'location_dest_id': order.partner_shipping_id.property_stock_customer.id,
    #                 'origin': order.name,
    #                 'move_type': 'direct',
    #                 'state': 'draft',  # Start with draft to confirm later
    #                 'sale_id': order.id,
    #             })
    #
    #             self.env['stock.move'].create({
    #                 'name': line.name,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_qty': line.product_uom_qty,
    #                 'product_uom': line.product_uom.id,
    #                 'picking_id': new_picking.id,
    #                 'location_id': new_picking.location_id.id,
    #                 'location_dest_id': new_picking.location_dest_id.id,
    #                 'sale_line_id': line.id,
    #                 'state': 'draft',  # Start with draft to confirm later
    #             })

    #         new_picking.action_confirm()
    #
    # return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    grn = fields.Char(string="GRN", compute='_compute_grn', readonly=False, required=False)
    # sale_check = fields.Boolean(string="Box", store=True)
    recipient_id = fields.Many2one('res.partner', string='Recipient',
                                   help='Choose a recipient for splitting '
                                        'delivery',
                                   domain=['|', ('company_id', '=', lambda
                                       self: self.env.company.id),
                                           ('company_id', '=', False)])

    @api.onchange("product_template_id")
    def _onchange_product_template_id(self):
        """Update recipients in order lines with the customer of sale order as
        default recipient"""
        if self.order_id.delivery_split:
            for line in self:
                if not line.recipient_id:
                    line.recipient_id = self.order_id.partner_id.id

    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be
        created from a stock rule coming from a sale order line. This method
        could be override in order to add other custom key that could be used
        in move/po creation."""
        date_deadline = self.order_id.commitment_date or (
                self.order_id.date_order + timedelta(
            days=self.customer_lead or 0.0))
        date_planned = date_deadline - timedelta(
            days=self.order_id.company_id.security_lead)
        values = {
            'group_id': group_id,
            'sale_line_id': self.id,
            'date_planned': date_planned,
            'date_deadline': date_deadline,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'product_description_variants': self.with_context(
                lang=self.order_id.partner_id.lang).
            _get_sale_order_line_multiline_description_variants(),
            'company_id': self.order_id.company_id,
            'product_packaging_id': self.product_packaging_id,
            'sequence': self.sequence,
        }
        if not self.recipient_id:
            self.recipient_id = self.order_id.partner_id.id
        if self.order_id.delivery_split:
            values.update({"partner_id": self.recipient_id.id})
        return values

    SaleOrderLine._prepare_procurement_values = _prepare_procurement_values

    @api.depends('move_ids')
    def _compute_grn(self):
        """Copy the value from stock.move to sale.order.line."""
        for line in self:
            # Get the stock moves linked to this sale order line
            moves = line.move_ids.filtered(lambda m: m.state not in ['cancel'])
            if moves:
                line.grn = moves[0].grn  # Copy value from the first move
            else:
                line.grn = False  # Reset if no moves exist
