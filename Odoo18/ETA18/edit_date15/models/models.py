# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from collections import defaultdict
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).', self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'invoice_date': self.date_order,
            'l10n_sa_delivery_date': self.date_order,
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids.filtered(lambda bank: bank.company_id.id in (self.company_id.id, False))[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals



class stock_scrap(models.Model):
    _inherit = 'stock.scrap'

    is_old_date_access = fields.Boolean(string='Is Old Date Access', compute='_compute_is_old_date_access')

    def _compute_is_old_date_access(self):
        for scrap in self:
            scrap.is_old_date_access = False
            if self.env.user.has_group('edit_date.group_scrap_old_date'):
                scrap.is_old_date_access = True

    date_old = fields.Datetime('Previous Date')

    def do_scrap(self):
        self._check_company()
        for scrap in self:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            move = self.env['stock.move'].create(scrap._prepare_move_values())
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            scrap.write({'move_id': move.id, 'state': 'done'})
            print('move_line: ',move.move_line_ids)
            scrap.date_done = fields.Datetime.now()
            if self.env.user.has_group('edit_date.group_scrap_old_date') and scrap.date_old:
                move.update({'date': scrap.date_old})
                move.move_line_ids.update({'date': scrap.date_old})
                scrap.date_done = scrap.date_old
        return True


class stock_quant(models.Model):
    _inherit = 'stock.quant'

    date = fields.Date(string="", required=False, )

    @api.model
    def _get_inventory_fields_write(self):
        res=super(stock_quant, self)._get_inventory_fields_write()
        res.append('date')
        return res

    def _apply_inventory(self):
        move_vals = []
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
        for quant in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:
                move_vals.append(
                    quant._get_inventory_move_values(quant.inventory_diff_quantity,
                                                     quant.product_id.with_company(
                                                         quant.company_id).property_stock_inventory,
                                                     quant.location_id))
            else:
                move_vals.append(
                    quant._get_inventory_move_values(-quant.inventory_diff_quantity,
                                                     quant.location_id,
                                                     quant.product_id.with_company(
                                                         quant.company_id).property_stock_inventory,
                                                     out=True))

        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves.update({'date':self.date})
        moves.move_line_ids.update({'date':self.date})
        moves._action_done()
        self.location_id.write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
        moves.move_line_ids.update({'date':self.date})
        self.write({'inventory_quantity': 0, 'user_id': False})
        self.write({'inventory_diff_quantity': 0})

class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                   cost):
        res = super(StockMove, self)._prepare_account_move_vals(credit_account_id, debit_account_id, journal_id, qty,
                                                                description, svl_id, cost)
        self.picking_id.edit_date()
        res['date'] = self.date
        return res

    def edit_stock_valuation_layer_date(self):
        for rec in self:
            valuation = self.env['stock.valuation.layer'].search([('stock_move_id', '=', rec.id)])
            valuation.sudo().write({"create_date": rec.date})

    def _action_done(self, cancel_backorder=False):
        valued_moves = {valued_type: self.env['stock.move'] for valued_type in self._get_valued_types()}
        for move in self:
            if float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding):
                continue
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move

        # AVCO application
        valued_moves['in'].product_price_update_before_done()

        self.filtered(lambda move: move.state == 'draft')._action_confirm()  # MRP allows scrapping draft moves
        moves = self.exists().filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_ids_todo = OrderedSet()

        # Cancel moves where necessary ; we should do it before creating the extra moves because
        # this operation could trigger a merge of moves.
        for move in moves:
            if move.quantity_done <= 0 and not move.is_inventory:
                if float_compare(move.product_uom_qty, 0.0, precision_rounding=move.product_uom.rounding) == 0 or cancel_backorder:
                    move._action_cancel()

        # Create extra moves where necessary
        for move in moves:
            if move.state == 'cancel' or (move.quantity_done <= 0 and not move.is_inventory):
                continue

            moves_ids_todo |= move._create_extra_move().ids

        moves_todo = self.browse(moves_ids_todo)
        moves_todo._check_company()
        # Split moves where necessary and move quants
        backorder_moves_vals = []
        for move in moves_todo:
            # To know whether we need to create a backorder or not, round to the general product's
            # decimal precision and not the product's UOM.
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(move.quantity_done, move.product_uom_qty, precision_digits=rounding) < 0:
                # Need to do some kind of conversion here
                qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity_done, move.product_id.uom_id, rounding_method='HALF-UP')
                new_move_vals = move._split(qty_split)
                backorder_moves_vals += new_move_vals
        backorder_moves = self.env['stock.move'].create(backorder_moves_vals)
        # The backorder moves are not yet in their own picking. We do not want to check entire packs for those
        # ones as it could messed up the result_package_id of the moves being currently validated
        backorder_moves.with_context(bypass_entire_pack=True)._action_confirm(merge=False)
        if cancel_backorder:
            backorder_moves.with_context(moves_todo=moves_todo)._action_cancel()
        moves_todo.mapped('move_line_ids').sorted()._action_done()
        # Check the consistency of the result packages; there should be an unique location across
        # the contained quants.
        for result_package in moves_todo\
                .mapped('move_line_ids.result_package_id')\
                .filtered(lambda p: p.quant_ids and len(p.quant_ids) > 1):
            if len(result_package.quant_ids.filtered(lambda q: not float_is_zero(abs(q.quantity) + abs(q.reserved_quantity), precision_rounding=q.product_uom_id.rounding)).mapped('location_id')) > 1:
                raise UserError(_('You cannot move the same package content more than once in the same transfer or split the same package into two location.'))
        picking = moves_todo.mapped('picking_id')
        moves_todo.write({'state': 'done'})

        new_push_moves = moves_todo.filtered(lambda m: m.picking_id.immediate_transfer)._push_apply()
        if new_push_moves:
            new_push_moves._action_confirm()
        move_dests_per_company = defaultdict(lambda: self.env['stock.move'])
        for move_dest in moves_todo.move_dest_ids:
            move_dests_per_company[move_dest.company_id.id] |= move_dest
        for company_id, move_dests in move_dests_per_company.items():
            move_dests.sudo().with_company(company_id)._action_assign()

        # We don't want to create back order for scrap moves
        # Replace by a kwarg in master
        if self.env.context.get('is_scrap'):
            return moves_todo

        if picking and not cancel_backorder:
            backorder = picking._create_backorder()
            if any([m.state == 'assigned' for m in backorder.move_ids]):
               backorder._check_entire_pack()
        for move in moves_todo - self:
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move

        stock_valuation_layers = self.env['stock.valuation.layer'].sudo()
        # Create the valuation layers in batch by calling `moves._create_valued_type_svl`.
        for valued_type in self._get_valued_types():
            todo_valued_moves = valued_moves[valued_type]
            if todo_valued_moves:
                todo_valued_moves._sanity_check_for_valuation()
                stock_valuation_layers |= getattr(todo_valued_moves, '_create_%s_svl' % valued_type)()

        stock_valuation_layers._validate_accounting_entries()
        stock_valuation_layers._validate_analytic_accounting_entries()

        stock_valuation_layers._check_company()

        # For every in move, run the vacuum for the linked product.
        products_to_vacuum = valued_moves['in'].mapped('product_id')
        company = valued_moves['in'].mapped('company_id') and valued_moves['in'].mapped('company_id')[0] or self.env.company
        for product_to_vacuum in products_to_vacuum:
            product_to_vacuum._run_fifo_vacuum(company)
        return moves_todo

    run_compute = fields.Boolean(compute='_compute_run_compute')

    def _compute_run_compute(self):
        for rec in self:
            rec.run_compute = True
            for line in rec.account_move_ids:
                line.date = rec.date


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.constrains('scheduled_date', 'move_ids_without_package', 'move_line_ids_without_package')
    def edit_date(self):
        self.move_ids_without_package.update({'date': self.scheduled_date})
        self.move_line_ids_without_package.update({'date': self.scheduled_date})

    def button_validate(self):
        res = super(stock_picking, self).button_validate()
        self.move_ids_without_package.edit_stock_valuation_layer_date()
        return res


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    # def button_mark_done(self):
    #     date = self.date_planned_start
    #     for rec in self:
    #         rec.move_raw_ids.update({
    #             'date': rec.date_planned_start
    #         })
    #     res=super(mrp_production, self).button_mark_done()
    #     # self.date_planned_start=date
    #     return res
    def _post_inventory(self, cancel_backorder=False):
        print('account.moveaccount.moveaccount.move22222222',self.env['account.move'].search_count([]))

        moves_to_do, moves_not_to_do = set(), set()
        for move in self.move_raw_ids:
            if move.state == 'done':
                moves_not_to_do.add(move.id)
            elif move.state != 'cancel':
                moves_to_do.add(move.id)
                if move.product_qty == 0.0 and move.quantity_done > 0:
                    move.product_uom_qty = move.quantity_done
        print('account.moveaccount.moveaccount.move22222222', self.env['account.move'].search_count([]))
        self.move_raw_ids.update({
            'date': self.date_planned_start
        })
        self.move_finished_ids.update({
            'date': self.date_planned_start
        })
        self.move_raw_ids.get_date_planned_start()
        self.move_finished_ids.get_date_planned_start()
        self.env['stock.move'].browse(moves_to_do)._action_done(cancel_backorder=cancel_backorder)
        moves_to_do = self.move_raw_ids.filtered(lambda x: x.state == 'done') - self.env['stock.move'].browse(moves_not_to_do)
        # Create a dict to avoid calling filtered inside for loops.
        moves_to_do_by_order = defaultdict(lambda: self.env['stock.move'], [
            (key, self.env['stock.move'].concat(*values))
            for key, values in tools_groupby(moves_to_do, key=lambda m: m.raw_material_production_id.id)
        ])
        print('account.moveaccount.moveaccount.move33333333333', self.env['account.move'].search_count([]))
        for order in self:
            finish_moves = order.move_finished_ids.filtered(lambda m: m.product_id == order.product_id and m.state not in ('done', 'cancel'))
            # the finish move can already be completed by the workorder.
            if finish_moves and not finish_moves.quantity_done:
                finish_moves._set_quantity_done(float_round(order.qty_producing - order.qty_produced, precision_rounding=order.product_uom_id.rounding, rounding_method='HALF-UP'))
                finish_moves.move_line_ids.lot_id = order.lot_producing_id
            order._cal_price(moves_to_do_by_order[order.id])
        print('account.moveaccount.moveaccount.move444444444444', self.env['account.move'].search_count([]))
        moves_to_finish = self.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_to_finish = moves_to_finish._action_done(cancel_backorder=cancel_backorder)
        self.action_assign()
        print('account.moveaccount.moveaccount.move55555555555', self.env['account.move'].search_count([]))
        for order in self:
            consume_move_lines = moves_to_do_by_order[order.id].mapped('move_line_ids')
            order.move_finished_ids.move_line_ids.consume_line_ids = [(6, 0, consume_move_lines.ids)]
        print('account.moveaccount.moveaccount.move66666666666666', self.env['account.move'].search_count([]))
        self.move_raw_ids.update({
            'date': self.date_planned_start
        })
        self.move_finished_ids.update({
            'date': self.date_planned_start
        })
        self.move_raw_ids.get_date_planned_start()
        self.move_finished_ids.get_date_planned_start()


        return True
    # def _post_inventory(self, cancel_backorder=False):
    #     res = super(mrp_production, self)._post_inventory(cancel_backorder=cancel_backorder)
    #     self.move_raw_ids.update({
    #         'date': rec.date_planned_start
    #     })
    #     return res

    @api.constrains('date_planned_start', 'date_planned_start')
    def get_date_planned_start(self):

        for rec in self:
            rec.move_raw_ids.update({
                'date': rec.date_planned_start
            })


class mrp_production(models.Model):
    _inherit = 'stock.move'

    # def button_mark_done(self):
    #     date = self.date_planned_start
    #     for rec in self:
    #         rec.move_raw_ids.update({
    #             'date': rec.date_planned_start
    #         })
    #     res=super(mrp_production, self).button_mark_done()
    #     # self.date_planned_start=date
    #     return res

    @api.constrains('date', 'move_line_nosuggest_ids')
    def get_date_planned_start(self):
        for rec in self:
            rec.move_line_nosuggest_ids.update({
                'date': rec.date
            })


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_finish(self):
        end_date = datetime.now()
        for workorder in self:
            if workorder.state in ('done', 'cancel'):
                continue
            workorder.end_all()
            vals = {
                'qty_produced': workorder.qty_produced or workorder.qty_producing or workorder.qty_production,
                'state': 'done',
                'date_finished': end_date,
                'date_planned_finished': end_date,
                'costs_hour': workorder.workcenter_id.costs_hour
            }
            if not workorder.date_start:
                vals['date_start'] = end_date
            # if not workorder.date_planned_start or end_date < workorder.date_planned_start:
            #     vals['date_planned_start'] = end_date
            workorder.write(vals)

            workorder._start_nextworkorder()
        return True


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    create_date = fields.Datetime("Create Date", readonly=True, compute='_compute_create_date')

    def _compute_create_date(self):
        for rec in self:
            rec.create_date = rec.stock_move_id.date


class AccountMoveInheritView(models.Model):
    _inherit = 'account.move'

    date = fields.Date(
        string='Date',
        required=True,
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        tracking=True,
    )
    run_compute = fields.Boolean(compute='_compute_run_compute')

    def _compute_run_compute(self):
        for rec in self:
            stock_move = self.env['stock.move'].search([('account_move_ids', '=', rec.id)])
            rec.run_compute = True
            if stock_move:
                for line in stock_move:
                    rec.date = line.date