from odoo import fields, models

class ReservationCancelWizard(models.TransientModel):
    _name = 'reservation.cancel.wizard'
    _description = 'Reservation Cancel Wizard'

    picking_id = fields.Many2one(
        'stock.picking', string='Picking', readonly=True,
        default=lambda self: self.env.context.get('default_picking_id')
    )
    option = fields.Selection(
        [
            ('delivered', 'Delivered to Customer'),
            ('cancelled', 'Customer Cancelled'),
        ],
        string='Action', required=True
    )

    def action_confirm(self):
        self.ensure_one()
        if self.option == 'delivered':
            self.picking_id.action_mark_delivered()
        else:
            self.picking_id.action_customer_cancel()
        return {'type': 'ir.actions.act_window_close'}
