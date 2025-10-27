# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PurchaseSingleApprovalCycle(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[
        ('waiting_approval', 'Approval'),
    ])

    def action_approval(self):
        for rec in self:
            rec.state = 'waiting_approval'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def button_confirm(self):
        for order in self:
            # Ensure the state is correct for confirmation
            if order.state not in ['waiting_approval', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def write(self, values):
        # Prevent changing the type of a purchase order line
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                _("You cannot change the type of a purchase order line. Instead, you should delete the current line and create a new line of the proper type."))

        # Track changes in 'product_qty'
        if 'product_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            for line in self:
                if (
                        line.order_id.state == "purchase"
                        and float_compare(line.product_qty, values["product_qty"], precision_digits=precision) != 0
                ):
                    line.order_id.message_post_with_view('purchase.track_po_line_template',
                                                         values={'line': line, 'product_qty': values['product_qty']},
                                                         subtype_id=self.env.ref('mail.mt_note').id)

        # Track changes in 'qty_received'
        if 'qty_received' in values:
            for line in self:
                line._track_qty_received(values['qty_received'])

        # Reset parent order state to 'draft' if in approval state
        if any(field in values for field in ['product_qty', 'product_id', 'price_unit', 'price_subtotal']):
            for line in self:
                if line.order_id.state in ['waiting_approval']:
                    line.order_id.state = 'draft'
                    line.order_id.message_post(body="Order state reset to draft due to changes in the order lines.")

        return super(PurchaseSingleApprovalCycle, self).write(values)
