# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        help='If set, this Sales Team will be used for sales and assignments related to this partner')


class BlanketOrder(models.Model):
    _name = "blanket.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Blanket Order"

    @api.model
    def _default_company(self):
        return self.env.company

    @api.model
    def _default_currency(self):
        return self.env.company.currency_id

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', "order_line.price_unit")
    def _compute_amount_all(self):
        for order in self.filtered("currency_id"):
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_untaxed),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    name = fields.Char(string='Order Reference', required=True, copy=False, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer"
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("expired", "Expired"),
        ],
        readonly=True, copy=False, index=True, tracking=3, default='draft')
    product_id = fields.Many2one("product.product", related="order_line.product_id", string="Product", )
    date_order = fields.Datetime(string='Order Date', required=True, index=True, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist',
        tracking=1, help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one("res.currency", compute="_compute_balanket_currency_id")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=_default_company,
        readonly=True,
    )
    fiscal_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position")

    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        ondelete="set null", tracking=True,
        change_default=True)
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True,
    )
    original_uom_qty = fields.Float(
        string="Quantity",
        default=1,
        digits="Product Unit of Measure",
    )
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string="Analytic Account",
                                          readonly=True,
                                          copy=False,
                                          check_company=True,
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                          )

    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms')
    validity_date = fields.Date(string='Expiration Date', copy=False)
    order_line = fields.One2many('blanket.order.line', 'order_id', string='Order Lines', copy=True, auto_join=True)
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        readonly=True,
        compute="_compute_amount_all",
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string="Taxes", store=True, readonly=True, compute="_compute_amount_all"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute="_compute_amount_all"
    )
    sale_count = fields.Integer(compute="_compute_sale_count")

    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        compute_sudo=True)
    has_blanket_active_pricelist = fields.Boolean(
        compute='_compute_has_blanket_active_pricelist')
    client_order_ref = fields.Char(string="Customer Reference", store=True, readonly=False)
    client_order_date = fields.Date(string="Customer Reference Date", store=True, readonly=False)

    @api.depends('company_id')
    def _compute_has_blanket_active_pricelist(self):
        for order in self:
            order.has_blanket_active_pricelist = bool(self.env['product.pricelist'].search(
                [('company_id', 'in', (False, order.company_id.id)), ('active', '=', True)],
                limit=1,
            ))

    @api.depends('pricelist_id', 'company_id')
    def _compute_balanket_currency_id(self):
        for order in self:
            order.currency_id = order.pricelist_id.currency_id or order.company_id.currency_id

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(BlanketOrder, self).create(vals_list)
        for template, vals in zip(templates, vals_list):
            if vals.get('name', _('New')) == _('New'):
                template.name = self.env['ir.sequence'].next_by_code('blanket.order') or _('New')
        return templates

    def _get_sale_orders(self):
        return self.mapped("order_line.sale_lines.order_id")

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_expired(self):
        for order in self:
            if order.state not in ('draft', 'expired'):
                raise UserError(
                    _('You can not delete a sent Blanket order or a confirmed Blanket order. You must first cancel it.'))

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            default_team = self.env.context.get('default_team_id', False) or self.partner_id.team_id.id
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=default_team
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)],
                                   user_id=user_id)
        self.update(values)

    @api.depends('company_id', 'fiscal_position_id')
    def _compute_tax_country_id(self):
        for record in self:
            if record.fiscal_position_id.foreign_vat:
                record.tax_country_id = record.fiscal_position_id.country_id
            else:
                record.tax_country_id = record.company_id.account_fiscal_country_id

    def action_view_sale_orders(self):
        sale_orders = self._get_sale_orders()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('id', 'in', sale_orders.ids)]
        action["context"] = [("id", "in", sale_orders.ids)]
        return action

    def _compute_sale_count(self):
        for blanket_order in self:
            blanket_order.sale_count = len(blanket_order._get_sale_orders())

    @api.model
    def _default_company(self):
        return self.env.company

    def button_draft(self):
        self.state = 'draft'

    def button_confirm(self):
        self.state = 'confirm'

    def button_expired(self):
        self.state = 'expired'
