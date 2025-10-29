# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'  # Inherit the sale.order model

    def action_confirm(self):
        """ Custom confirm action with additional checks """
        for order in self:
            # Check for any confirmation errors
            error_msg = order._confirmation_error_message()
            if error_msg:
                raise UserError(error_msg)

            # Validate the analytic distribution
            order.order_line._validate_analytic_distribution()

            # Ensure partner is subscribed to messages
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])

            # Write confirmation values
            order.write(order._prepare_confirmation_values())

            # Remove 'default_name' from context if it exists
            context = self._context.copy()
            context.pop('default_name', None)

            # Call the base action_confirm
            order.with_context(context)._action_confirm()

            # Lock order if user has the specific group
            user = order.create_uid
            if user and user.sudo().has_group('sale.group_auto_done_setting'):
                order.action_lock()

            # Send confirmation email if 'send_email' is in context
            if self.env.context.get('send_email'):
                order._send_order_confirmation_mail()

        return True
