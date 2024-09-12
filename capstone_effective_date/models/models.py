# -*- coding: utf-8 -*-

from odoo import models, api, fields


class Picking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        self._check_company()
        todo_moves = self.move_ids.filtered(
            lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        for picking in self:
            if picking.owner_id:
                picking.move_ids.write({'restrict_partner_id': picking.owner_id.id})
                picking.move_line_ids.write({'owner_id': picking.owner_id.id})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': self.scheduled_date, 'priority': '0'})

        # if incoming/internal moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(
            lambda p: p.picking_type_id.code in ('incoming', 'internal')).move_ids.filtered(lambda m: m.state == 'done')
        done_incoming_moves._trigger_assign()

        self._send_confirmation_email()
        return True

    def button_validate(self):
        res = super(Picking, self).button_validate()
        if res:
            self.env.cr.execute(
                f"UPDATE stock_valuation_layer SET create_date = '{self.scheduled_date}' WHERE description LIKE '%{self.name}%'")
            # self.env.cr.execute(
            #     f"UPDATE account_move SET date = '{self.scheduled_date}' WHERE ref LIKE '%{self.name}%'")
            # update_date = self.env['stock.move'].search([('reference', '=', self.name)])[0]
            # print(update_date.date)
            # update_date.date = self.scheduled_date

        return res


class PickingDate(models.Model):
    _inherit = 'account.move'

    scheduled_date = fields.Datetime('Date', related='stock_move_id.picking_id.scheduled_date', store=True)

    @api.model
    def create(self, values):
        if values.get('ref') is not None and values['ref']:
            updated_date = self.env['stock.picking'].search([('name', 'like', values['ref'].split(' - ')[0])])
            if updated_date:
                values['date'] = updated_date[0].scheduled_date
        result = super(PickingDate, self).create(values)
        return result
