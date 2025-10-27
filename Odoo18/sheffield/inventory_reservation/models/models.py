from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    reservation_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('delivered', 'Delivered to Customer'),
            ('cancelled', 'Customer Cancelled'),
        ],
        string="Reservation Status",
        default='draft',
        copy=False,
        store=True, tracking=True,
    )
    
    is_reservation_picking = fields.Boolean(
        string="Is Reservation Picking",
        compute='_compute_is_reservation_picking',
        store=True,
        help="Technical field to identify if this picking is from Reservation operation type"
    )

    @api.depends('picking_type_id', 'picking_type_id.name')
    def _compute_is_reservation_picking(self):
        """Compute if this picking belongs to the Reservation operation type."""
        for picking in self:
            name = (picking.picking_type_id.name or '') if picking.picking_type_id else ''
            picking.is_reservation_picking = 'Reservation' in name

    def _is_reservation_picking(self):
        """Return True if this picking belongs to the Reservation operation type.

        We check the picking_type_id.name for the substring 'Reservation' which
        matches your operation type 'Operation Type Abbas Al Akkad: Reservation'.
        """
        self.ensure_one()
        return self.is_reservation_picking

    def action_open_reservation_cancel_wizard(self):
        self.ensure_one()
        if not self._is_reservation_picking():
            raise UserError(_("This action applies only to Reservation pickings."))
        return {
            'name': _('Cancel Reservation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reservation.cancel.wizard',
            'target': 'new',
            'context': {'default_picking_id': self.id},
        }

    def action_mark_delivered(self):
        """Used when choose 'Delivered to Customer' in the wizard."""
        for picking in self:
            if not picking._is_reservation_picking():
                raise UserError(_("This action applies only to Reservation pickings."))
            # Unreserve reserved quants so they return to on-hand.
            picking.move_ids_without_package._do_unreserve()
            # Uncomment below if customer wants to actually validate the picking
            # if picking.state not in ('done',):
            picking.action_cancel()
            picking.reservation_state = 'delivered'
        return True

    def action_customer_cancel(self):
        """Used when choose 'Customer Cancelled' in the wizard. Unreserve and cancel."""
        for picking in self:
            if not picking._is_reservation_picking():
                raise UserError(_("This action applies only to Reservation pickings."))
            # Unreserve reserved quants so they return to on-hand.
            picking.move_ids_without_package._do_unreserve()
            # Uncomment below if customer wants to actually cancel the picking
            picking.action_cancel()
            picking.reservation_state = 'cancelled'
        return True
