# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class CustomStockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=False,
                                          index=True,
                                          states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    # is_updated = fields.Boolean(string="Is Updated")

    def button_validate(self):
        picking = super(CustomStockPickingInherit, self).button_validate()
        for rec in self:
            if rec.analytic_account_id:
                account_move = self.env['account.move'].search(
                    ['|', '|', ('name', '=', rec.name), ('ref', 'ilike', rec.name),
                     ('partner_id', '=', rec.name)])
                if account_move:
                    # Check if this is a dropship delivery
                    if rec.is_dropship:
                        sorted_moves = account_move.sorted('id')

                        # Get the number of move lines in the picking to determine the pattern
                        move_line_count = len(rec.move_line_ids)

                        # Assign analytic to every other journal entry 2nd, 4th, 6th, etc
                        # This corresponds to the second journal entry of each product
                        for index in range(1, len(sorted_moves), 2):
                            if index < len(sorted_moves):
                                move_to_update = sorted_moves[index]
                                if move_to_update.line_ids:
                                    for l in move_to_update.line_ids:
                                        l.analytic_distribution = {
                                            rec.analytic_account_id.id: 100,
                                        } if l.debit > 0 and not rec.picking_type_id.is_return or l.credit > 0 and rec.picking_type_id.is_return else False
                                move_to_update.button_draft()
                                move_to_update.action_post()
                    else:
                        # For non-dropship: keep existing logic (assign to all journal entries)
                        for acc in account_move:
                            if acc.line_ids:
                                for l in acc.line_ids:
                                    l.analytic_distribution = {
                                        rec.analytic_account_id.id: 100,
                                    } if l.debit > 0 and not rec.picking_type_id.is_return or l.credit > 0 and rec.picking_type_id.is_return else False
                            acc.button_draft()
                            acc.action_post()
        return picking

    is_updated = fields.Boolean()

    # def button_validate(self):
    #     picking = super(CustomStockPickingInherit, self).button_validate()
    #     for rec in self:
    #         if rec.analytic_account_id:
    #             account_move = self.env['account.move'].search(
    #                 ['|', '|', ('name', '=', rec.name), ('ref', 'ilike', rec.name),
    #                  ('partner_id', '=', rec.name)])
    #             if account_move:
    #                 # Check if this is a dropship delivery
    #                 if rec.is_dropship:
    #                     # For dropship: only assign analytic account to the second journal entry
    #                     if len(account_move) >= 2:
    #                         second_move = account_move[0]  # Get the second journal entry
    #                         if second_move.line_ids:
    #                             for l in second_move.line_ids:
    #                                 l.analytic_distribution = {
    #                                     rec.analytic_account_id.id: 100, } if l.debit > 0 and not rec.picking_type_id.is_return or l.credit > 0 and rec.picking_type_id.is_return else False
    #                         second_move.button_draft()
    #                         second_move.action_post()
    #                 else:
    #                     # For non-dropship: keep existing logic (assign to all journal entries)
    #                     for acc in account_move:
    #                         if acc.line_ids:
    #                             for l in acc.line_ids:
    #                                 l.analytic_distribution = {
    #                                     rec.analytic_account_id.id: 100, } if l.debit > 0 and not rec.picking_type_id.is_return or l.credit > 0 and rec.picking_type_id.is_return else False
    #                     account_move.button_draft()
    #                     account_move.action_post()
    #     return picking
    #
    # is_updated = fields.Boolean()

    def button_update_analytic_account(self):
        for rec in self:
            if rec.analytic_account_id:
                account_move = self.env['account.move'].search(
                    ['|', '|', ('name', 'ilike', rec.name), ('ref', 'ilike', rec.name),
                     ('partner_id', 'ilike', rec.name)])
                print("#######################  ", account_move)

                if account_move:
                    # print('account_move', account_move)
                    for acc in account_move:
                        if acc.line_ids:
                            for l in acc.line_ids:
                                if l.debit > 0:
                                    # l.analytic_account_id = rec.analytic_account_id.id
                                    l.analytic_distribution = {rec.analytic_account_id.id: 100, }

                    account_move.button_draft()
                    account_move.action_post()
                    rec.is_updated = True
                else:
                    raise UserError('there is no journal entry for this Delivery.!')


class AccountAsset(models.Model):
    _inherit = 'account.asset'
