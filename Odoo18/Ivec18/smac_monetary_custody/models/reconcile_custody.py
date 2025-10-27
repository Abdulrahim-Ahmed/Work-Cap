from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReconcileCustody(models.Model):
    _name = 'reconcile.cash.custody'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Reconcile Custody'

    name = fields.Char()
    requester_id = fields.Many2one(
        comodel_name='res.partner',
        string='Requester',
        required=True, default=lambda self: self.env.user.partner_id)
    date = fields.Date(
        string='Date',
        required=False, default=fields.Date.today)
    reconcile_custody_lines_ids = fields.One2many(
        comodel_name='reconcile.cash.custody.lines',
        inverse_name='reconcile_custody_id',
        string='Lines',
        required=False)
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'),

                                        ('confirm', 'Confirm'),
                                        ('reconciled', 'Reconciled'),
                                        ],
                             default='draft', tracking=True)
    total_reconciled_amount = fields.Float(
        string='Total Reconciled Amount',
        required=False, compute="get_total_reconciled_amount", store=True)
    journal_entry_count = fields.Integer(
        string='Entries Count',
        required=False, compute="get_journal_entry_count")
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=False)
    credit_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Credit Account',
        required=False)

    def get_journal_entry_count(self):
        for reconcile in self:
            journal_ids = self.env['account.move'].search(
                [('reconcile_custody_id', '=', reconcile.id), ('move_type', '=', 'entry')])
            reconcile.journal_entry_count = len(journal_ids.ids)

    def view_journal_entry_button(self):
        for reconcile in self:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Journals'),
                'res_model': 'account.move',
                'target': 'current',
                'view_mode': 'list,form',
                'domain': [('reconcile_custody_id', '=', reconcile.id), ('move_type', '=', 'entry')],
            }

    @api.onchange("requester_id")
    def get_reconcile_lines(self):
        for reconcile in self:
            if reconcile.requester_id:
                reconcile.reconcile_custody_lines_ids = [(5, 0, 0)]
                requested_custody_ids = self.env['request.cash.custody'].search(
                    [('requester_id', '=', reconcile.requester_id.id), ('state', 'in', ['confirm', 'paid'])])
                if requested_custody_ids:
                    requested_lines = []
                    for request in requested_custody_ids:
                        for line in request.request_custody_lines_ids:
                            reconciled_amount = sum(self.env['reconcile.cash.custody.lines'].search([
                                ('reconcile_custody_id.state', 'in', ['confirm', 'reconciled']),
                                ('reconcile_custody_id.requester_id', '=', request.requester_id.id)
                            ]).mapped('reconciled_amount'))
                            print("!!!!!!!!!!!!!!!!!!!!", reconciled_amount)
                            if line.amount > reconciled_amount:
                                requested_lines.append([0, 0, {
                                    'account_id': line.request_custody_id.request_custody_lines_ids[0].account_id.id,
                                    'amount': line.amount - reconciled_amount,
                                    'project_id': line.request_custody_id.project_id.id,
                                    'request_custody_line_id': line.id,
                                }])
                    reconcile.reconcile_custody_lines_ids = requested_lines

    @api.depends("reconcile_custody_lines_ids", "reconcile_custody_lines_ids.reconciled_amount")
    def get_total_reconciled_amount(self):
        for reconcile in self:
            if reconcile.reconcile_custody_lines_ids:
                reconcile.total_reconciled_amount = sum(
                    reconcile.reconcile_custody_lines_ids.mapped('reconciled_amount'))
            else:
                reconcile.total_reconciled_amount = 0

    # def action_sent_to_confirmation(self):
    #     for reconcile in self:
    #         reconcile.state = 'sent_to_confirmation'
    def action_draft(self):
        for reconcile in self:
            if reconcile.state == 'reconciled':
                journal_entry = self.env['account.move'].search(
                    [('move_type', '=', 'entry'), ('reconcile_custody_id', '=', reconcile.id)])
                if journal_entry:
                    journal_entry.button_draft()
                    journal_entry.name = '/'
                    journal_entry.unlink()
                reconcile.state = 'draft'

    def action_confirm(self):
        for reconcile in self:
            reconcile.state = 'confirm'
            # for line in reconcile.reconcile_custody_lines_ids:
            #     if line.reconciled_amount > line.amount:
            #         raise ValidationError('Reconcile Amount Must Be Less Than Or Equal Amount ')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'reconcile.cash.custody.Sequence') or _('New')
        res = super(ReconcileCustody, self).create(vals)
        return res

    def action_reconciled(self):
        for reconcile in self:
            journal_entry = self.env['account.move']
            if reconcile.total_reconciled_amount > 0:
                line_ids = []
                for line in reconcile.reconcile_custody_lines_ids:
                    if line.reconciled_amount > 0:
                        line_ids += [
                            (0, 0, {
                                'debit': line.reconciled_amount,
                                'credit': 0.0,
                                'account_id': line.account_id.id,
                                'partner_id': line.partner_id.id,

                                'analytic_distribution': {
                                    # line.project_id.analytic_account_id.id: 100,
                                    line.project_id.id: 100,
                                },
                                'currency_id': self.env.company.currency_id.id,
                            })]
                line_ids += [
                    (0, 0, {
                        'debit': 0.0,
                        'credit': reconcile.total_reconciled_amount,
                        'account_id': reconcile.credit_account_id.id,
                        'currency_id': self.env.company.currency_id.id,

                    })]
                journal_entry_created = journal_entry.create({
                    'move_type': 'entry',
                    'invoice_date': reconcile.date,
                    'currency_id': self.env.company.currency_id.id,
                    'journal_id': reconcile.journal_id.id,
                    'reconcile_custody_id': reconcile.id,
                    'line_ids': line_ids,
                })
                if journal_entry_created:
                    journal_entry_created.action_post()
            reconcile.state = 'reconciled'


class ReconcileCashCustodyLInes(models.Model):
    _name = 'reconcile.cash.custody.lines'
    _description = 'Reconcile Cash custody Lines'
    reconcile_custody_id = fields.Many2one(
        comodel_name='reconcile.cash.custody',
        string='Reconcile Custody',
        required=False)
    partner_id = fields.Many2one('res.partner', required=False)

    account_id = fields.Many2one(string='Account', comodel_name="account.account")
    amount = fields.Float(
        string='Amount',
        required=True)
    project_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Project',
        required=True)
    reconciled_amount = fields.Float(
        string='Reconciled Amount',
        required=True)
    request_custody_line_id = fields.Many2one('request.cash.custody.lines', string='Request Cash Custody Line')

    @api.onchange("partner_id")
    def get_payable_account(self):
        for line in self:
            if line.partner_id:
                line.account_id = line.partner_id.property_account_payable_id

    @api.constrains("reconciled_amount", "amount")
    def get_amount_validation(self):
        for line in self:
            if line.reconciled_amount > line.amount:
                raise ValidationError("Reconciled Amount  less than or equal Amount")
