from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RequestCashCustody(models.Model):
    _name = 'request.cash.custody'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Request Cash custody'

    name = fields.Char()
    requester_id = fields.Many2one(
        comodel_name='res.partner',
        string='Requester',
        required=True, default=lambda self: self.env.user.partner_id)
    project_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Project',
        required=True)
    date = fields.Date(
        string='Date',
        required=False, default=fields.Date.today)
    request_custody_lines_ids = fields.One2many(
        comodel_name='request.cash.custody.lines',
        inverse_name='request_custody_id',
        string='Lines',
        required=False)
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'),

                                        ('confirm', 'Confirm'),
                                        ('paid', 'Paid'),
                                        ],
                             default='draft', tracking=True)
    # ('sent_to_confirmation', 'Sent To Confirmation'),
    # ('submit', 'Submit'),
    total_amount = fields.Float(
        string='Total Amount',
        required=False, compute="get_total_amount", store=True)
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=False)
    debit_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Debit Account',
        required=False)
    credit_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Credit Account',
        required=False)
    journal_entry_count = fields.Integer(
        string='Entries Count',
        required=False, compute="get_journal_entry_count")

    def get_journal_entry_count(self):
        for request in self:
            journal_ids = self.env['account.move'].search(
                [('request_custody_id', '=', request.id), ('move_type', '=', 'entry')])
            request.journal_entry_count = len(journal_ids.ids)

    def view_journal_entry_button(self):
        for request in self:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Journals'),
                'res_model': 'account.move',
                'target': 'current',
                'view_mode': 'list,form',
                'domain': [('request_custody_id', '=', request.id), ('move_type', '=', 'entry')],
            }

    @api.depends("request_custody_lines_ids", "request_custody_lines_ids.amount")
    def get_total_amount(self):
        for request in self:
            if request.request_custody_lines_ids:
                request.total_amount = sum(request.request_custody_lines_ids.mapped('amount'))
            else:
                request.total_amount = 0

    # def action_sent_to_confirmation(self):
    #     for request in self:
    #         request.state = 'sent_to_confirmation'

    def action_confirm(self):
        for request in self:
            request.state = 'confirm'

    # def action_submit(self):
    #     for request in self:
    #         request.state = 'submit'

    def action_paid(self):
        for request in self:
            journal_entry = self.env['account.move']
            if request.total_amount > 0:
                line_ids = [
                    (0, 0, {
                        'debit': request.total_amount,
                        'credit': 0.0,
                        'account_id': request.debit_account_id.id,
                        'currency_id': self.env.company.currency_id.id,
                    })]
                line_ids += [
                    (0, 0, {
                        'debit': 0.0,
                        'credit': request.total_amount,
                        'account_id': request.credit_account_id.id,
                        'currency_id': self.env.company.currency_id.id,
                    })]
                journal_entry_created=journal_entry.create({
                    'move_type': 'entry',
                    'invoice_date': request.date,
                    'currency_id': self.env.company.currency_id.id,
                    'journal_id': request.journal_id.id,
                    'request_custody_id': request.id,
                    'line_ids': line_ids,
                })
                if journal_entry_created:
                    journal_entry_created.action_post()
                request.state = 'paid'
                if not request.request_custody_lines_ids.account_id:
                    raise ValidationError('The Field Account Must Be Set')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'request.cash.custody.Sequence') or _('New')
        res = super(RequestCashCustody, self).create(vals)

        return res


class RequestCashCustodyLInes(models.Model):
    _name = 'request.cash.custody.lines'
    _description = 'Request Cash custody Lines'
    request_custody_id = fields.Many2one(
        comodel_name='request.cash.custody',
        string='Request Custody',
        required=False)
    description = fields.Char()
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account', domain="[('account_type', 'in', ['expense','expense_depreciation','expense_direct_cost'])]"
       )
    amount = fields.Float(
        string='Amount',
        required=True)

    @api.constrains("amount")
    def get_positive_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError("Amount Must Be Positive")
