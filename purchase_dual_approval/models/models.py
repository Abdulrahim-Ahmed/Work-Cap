# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class PurchaseApprovalCycle(models.Model):
    _inherit = 'purchase.order'

    changes_pending_approval = fields.Boolean(string="Changes Pending Approval", default=False)
    state = fields.Selection(selection_add=[
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
    ])

    def action_first_approval(self):
        for rec in self:
            rec.state = 'first_approval'

    def action_second_approval(self):
        for rec in self:
            rec.state = 'second_approval'

    # def action_reset_to_draft(self):
    #     for rec in self:
    #         rec.state = 'draft'

    # def button_confirm(self):
    #     for order in self:
    #         if order.state not in ['second_approval', 'sent']:
    #             continue
    #         order._add_supplier_to_product()
    #         # Deal with double validation process
    #         if order._approval_allowed():
    #             order.button_approve()
    #         else:
    #             order.write({'state': 'to approve'})
    #         if order.partner_id not in order.message_partner_ids:
    #             order.message_subscribe([order.partner_id.id])
    #     return True

    def button_confirm(self):
        for order in self:
            # Check if changes were made in 'second_approval' state and are pending approval
            if order.state == 'second_approval' and order.changes_pending_approval:
                raise exceptions.UserError('Changes were made and need approval before confirming the order.')

            # Proceed with the normal flow if there are no pending changes or not in 'second_approval'
            if order.state not in ['second_approval', 'sent']:
                continue

            order._add_supplier_to_product()

            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})

            # Subscribe the partner if they are not already subscribed
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])

        return True

    # @api.model
    # def create(self, vals):
    #     if 'state' in vals and vals['state'] == 'second_approval':
    #         raise exceptions.UserError('You cannot create a purchase order in the second approval state.')
    #     return super(PurchaseApprovalCycle, self).create(vals)
    #
    # def write(self, vals):
    #     # Allow transition from 'second_approval' to 'purchase' or 'draft' without restrictions
    #     if 'state' in vals and self.state == 'second_approval' and vals.get('state') in ['purchase', 'draft']:
    #         return super(PurchaseApprovalCycle, self).write(vals)
    #
    #     # Check if any other fields are being modified
    #     if self.state == 'second_approval' and any(field != 'state' for field in vals):
    #         raise exceptions.UserError('You cannot modify a purchase order in the second approval state.')
    #
    #     return super(PurchaseApprovalCycle, self).write(vals)
    #
    # def unlink(self):
    #     if self.state == 'second_approval':
    #         raise exceptions.UserError('You cannot delete a purchase order in the second approval state.')
    #     return super(PurchaseApprovalCycle, self).unlink()
    #
    # def action_reset_to_draft(self):
    #     # Reset the state to 'draft'
    #     self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        if 'state' in vals and vals['state'] == 'second_approval':
            raise exceptions.UserError('You cannot create a purchase order in the second approval state.')
        return super(PurchaseApprovalCycle, self).create(vals)

    def write(self, vals):
        # Allow state transitions without restrictions
        if 'state' in vals and vals.get('state') in ['purchase', 'draft']:
            return super(PurchaseApprovalCycle, self).write(vals)

        # If the state is 'second_approval', track changes and set the flag
        if self.state == 'second_approval' and any(field != 'state' for field in vals):
            vals['changes_pending_approval'] = True
        return super(PurchaseApprovalCycle, self).write(vals)

    def unlink(self):
        if self.state == 'second_approval':
            raise exceptions.UserError('You cannot delete a purchase order in the second approval state.')
        return super(PurchaseApprovalCycle, self).unlink()

    def action_reset_to_draft(self):
        # Reset the state to 'draft' and clear the changes_pending_approval flag
        self.write({
            'state': 'draft',
            'changes_pending_approval': False
        })

    # @api.model
    # def create(self, vals):
    #     if 'state' in vals and vals['state'] == 'second_approval':
    #         raise exceptions.UserError('You cannot create a purchase order in the second approval state.')
    #     return super(PurchaseApprovalCycle, self).create(vals)
    #
    # def write(self, vals):
    #     # Allow transition from 'second_approval' to 'purchase' without restrictions
    #     if 'state' in vals and self.state == 'second_approval' and vals.get('state') == 'purchase':
    #         return super(PurchaseApprovalCycle, self).write(vals)
    #
    #     if 'state' in vals and self.state == 'second_approval' and vals.get('state') == 'draft':
    #         return super(PurchaseApprovalCycle, self).write(vals)
    #
    #     # If in 'second_approval' state and trying to modify anything else, raise an error
    #     if self.state == 'second_approval':
    #         raise exceptions.UserError('You cannot modify a purchase order in the second approval state.')
    #
    #     return super(PurchaseApprovalCycle, self).write(vals)
    #
    # def unlink(self):
    #     if self.state == 'second_approval':
    #         raise exceptions.UserError('You cannot delete a purchase order in the second approval state.')
    #     return super(PurchaseApprovalCycle, self).unlink()
