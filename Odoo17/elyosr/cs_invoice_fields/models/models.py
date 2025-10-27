from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    partner_vat = fields.Char(
        string="Tax ID",
        related="partner_id.vat",
        store=True
    )

    wh_source_document = fields.Char(
        string="WH Source Document",
        compute="_compute_wh_source_document",
        store=False
    )

    def _compute_wh_source_document(self):
        for move in self:
            picking = self.env['stock.picking'].search(
                [('origin', '=', move.invoice_origin)],
                limit=1
            )
            move.wh_source_document = picking.name if picking else False