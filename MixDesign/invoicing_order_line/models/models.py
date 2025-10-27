# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import UserError


class SaleOrderLineInv(models.Model):
    _inherit = 'sale.order.line'

    is_uninvoiced = fields.Boolean(compute='_compute_is_uninvoiced', store=True)
    grn = fields.Char(
        string='GRN',
        store=True,
        readonly=False
    )
    grn_to_invoice = fields.Char(string="GRN To Invoice")
    delivery_reference = fields.Char(
        string='Delivery Reference',
        compute='_compute_delivery_reference',
        store=True
    )

    @api.depends('move_ids', 'move_ids.picking_id', 'move_ids.picking_id.name')
    def _compute_delivery_reference(self):
        for line in self:
            # Get stock moves related to this specific line
            moves = line.move_ids.filtered(lambda m: m.state not in ['cancel'])
            # Get unique picking references from these moves
            pickings = moves.mapped('picking_id').filtered(lambda p: p.state not in ['cancel'])
            delivery_names = pickings.mapped('name')
            line.delivery_reference = ', '.join(delivery_names) if delivery_names else ''

    # @api.depends('order_id.picking_ids')
    # def _compute_delivery_reference(self):
    #     for line in self:
    #         pickings = line.order_id.picking_ids.filtered(lambda p: p.state not in ['cancel'])
    #         delivery_names = pickings.mapped('name')
    #         line.delivery_reference = ', '.join(delivery_names) if delivery_names else ''

    @api.depends('qty_invoiced', 'product_uom_qty')
    def _compute_is_uninvoiced(self):
        for line in self:
            line.is_uninvoiced = line.qty_invoiced < line.product_uom_qty

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res['grn'] = self.grn  # assuming 'grn' is on sale.order.line
        return res

    @api.model
    def action_invoice_selected_lines(self, line_ids):
        selected_lines = self.browse(line_ids).filtered(lambda l: l.is_uninvoiced)

        # Group by customer (partner_id)
        invoices = self.env['account.move']
        partner_lines_map = {}
        for line in selected_lines:
            partner = line.order_id.partner_id
            partner_lines_map.setdefault(partner, self.env['sale.order.line'])
            partner_lines_map[partner] |= line

        for partner, lines in partner_lines_map.items():
            # Create one invoice per partner
            first_order = lines[0].order_id
            invoice_vals = first_order._prepare_invoice()
            invoice_vals.update({'partner_id': partner.id})
            invoice = self.env['account.move'].create(invoice_vals)

            # Add all eligible lines for this partner
            for line in lines:
                invoice_line_vals = line._prepare_invoice_line()
                invoice_line_vals['move_id'] = invoice.id
                self.env['account.move.line'].create(invoice_line_vals)

            invoice._compute_amount()
            invoices |= invoice

        return {
            'name': 'Customer Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', invoices.ids)],
        }

    @api.model
    def action_invoice_grn_matched_lines(self, line_ids):
        matched_lines = self.browse(line_ids).filtered(
            lambda l: (
                    l.is_uninvoiced and
                    l.qty_delivered > 0 and
                    l.grn and
                    l.grn_to_invoice and
                    l.grn.strip() == l.grn_to_invoice.strip()
            )
        )

        if not matched_lines:
            raise UserError("No lines found with matching GRN.")

        return self.action_invoice_selected_lines(matched_lines.ids)


class InvoiceOrderLineGRN(models.Model):
    _inherit = 'account.move.line'

    grn = fields.Char(string='GRN', required=False)
