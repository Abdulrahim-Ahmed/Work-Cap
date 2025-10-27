from odoo import models, fields, api
from datetime import timedelta


class StockPickingClearanceCycle(models.Model):
    _inherit = 'stock.picking'

    is_export_temporary = fields.Boolean(string='Export Temporary', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('pending_custom', 'Pending Custom'),
        ('received_custom', 'Received Custom'),
        ('received_gafi', 'Received Gafi'),
        ('received_final_declaration', 'Received Final Declaration'),
        ('finished', 'Finished'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True)
    received_custom = fields.Binary(string="Upload Custom", store=True)
    received_final_declaration = fields.Binary(string="Upload Final Declaration", store=True)
    pending_custom_start_date = fields.Datetime(string="Custom Clearance Start", readonly=True)
    custom_clearance_deadline = fields.Datetime(string="Custom Clearance Deadline", compute="_compute_deadline",
                                                store=True)
    days_remaining = fields.Integer(string="Clearance Days Remaining", compute="_compute_deadline", store=True)
    is_expired = fields.Boolean(string="Is Expired", compute="_compute_deadline", store=True)

    def action_pending_custom(self):
        for rec in self:
            rec.state = 'pending_custom'
            rec.pending_custom_start_date = fields.Datetime.now()

    def action_received_custom(self):
        for rec in self:
            rec.state = 'received_custom'

    def action_received_gafi(self):
        for rec in self:
            rec.state = 'received_gafi'

    def action_received_final_declaration(self):
        for rec in self:
            rec.state = 'received_final_declaration'

    @api.depends('pending_custom_start_date')
    def _compute_deadline(self):
        for rec in self:
            if rec.pending_custom_start_date:
                rec.custom_clearance_deadline = rec.pending_custom_start_date + timedelta(days=90)
                delta = rec.custom_clearance_deadline - fields.Datetime.now()
                rec.days_remaining = delta.days
                rec.is_expired = delta.total_seconds() < 0
            else:
                rec.custom_clearance_deadline = False
                rec.days_remaining = 0
                rec.is_expired = False
