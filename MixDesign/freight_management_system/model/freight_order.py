# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ammu Raj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class FreightOrder(models.Model):
    """Model for creating freight orders"""
    _name = 'freight.order'
    _description = 'Freight Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', default='New', readonly=False,
                       help='Name of the order')
    # purchase_order_ids = fields.One2many(
    #     # 'purchase.order',
    #     # 'freight_order_id',
    #     string="Related Purchase Orders"
    # )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Terms",
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    shipper_id = fields.Many2one('res.partner', string='Shipper', required=True,
                                 tracking=True, help="Shipper's Details")
    consignee_id = fields.Many2one('res.partner', 'Consignee',
                                   tracking=True, help="Select the consignee for the order")
    customer_id = fields.Many2one('res.partner', 'Customer',
                                  tracking=True, help="Select Customer Name")
    type = fields.Selection([('import', 'Import'),
                             ('export', 'Export'),
                             ],
                            string='Import/Export', tracking=True, required=True,
                            help="Type of freight operation")
    sale_order_names = fields.Char(string="Sale Order", compute="_compute_sale_order_names", store=False)
    purchase_order_names = fields.Char(string="Purchase Order", compute="_compute_purchase_order_names", store=False)
    import_type = fields.Selection(string="Import Type",
                                   selection=[('import_egypt_free_zone', 'Import Egypt Free Zone'),
                                              ('import_offshore', 'Import OffShore'), ], tracking=True, required=False)
    export_type = fields.Selection(string="Export Type",
                                   selection=[('export_free_zone', 'Export Free Zone'),
                                              ('export_temporary', 'Export Temporary'),
                                              ('export_local_market', 'Export Local Market'),
                                              ('export_global', 'Export Global'), ], tracking=True, required=False)
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water'), ('warehouse_pickup', 'Warehouse Pickup')], tracking=True,
                                      string='Transport',
                                      help='Type of transportation',
                                      required=True)
    land_type = fields.Selection([('ltl', 'LTL'), ('ftl', 'FTL')],
                                 string='Land Shipping', tracking=True,
                                 help="Types of shipment movement involved in"
                                      "Land")
    water_type = fields.Selection([('fcl', 'FCL'), ('lcl', 'LCL')],
                                  string='Water Shipping', tracking=True,
                                  help="Types of shipment movement involved in"
                                       "Water")
    order_date = fields.Date(string='Date', default=fields.Date.today(),
                             tracking=True, help="Date of order")
    loading_port_id = fields.Many2one('freight.port', string="Loading Port",
                                      tracking=True, required=True,
                                      help="Loading port of the freight order")
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port",
                                          tracking=True, required=True,
                                          help="Discharging port of freight"
                                               "order")
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'),
                              ('confirm', 'Confirmed'),
                              ('invoice', 'Invoiced'), ('done', 'Done'),
                              ('cancel', 'Cancel')],
                             default='draft', string="State", tracking=True,
                             help='Different states of freight order')
    clearance = fields.Boolean(string='Clearance', help='Checking the'
                                                        'clearance')
    clearance_count = fields.Integer(compute='_compute_count',
                                     string='Clearance Count',
                                     help='The number of clearance')
    invoice_count = fields.Integer(compute='_compute_count',
                                   string='Invoice Count',
                                   help='The number invoice created')
    total_order_price = fields.Float(string='Total',
                                     compute='_compute_total_order_price',
                                     help='The total order price')
    total_volume = fields.Float(string='Total Volume',
                                compute='_compute_total_order_price',
                                help='The total used volume')
    total_weight = fields.Float(string='Total Gross Weight', digits=(16, 2),
                                compute='_compute_total_order_price',
                                help='The total gross weight used')
    total_net_weight = fields.Float(string='Total Net Weight', digits=(16, 2),
                                    compute='_compute_total_order_price',
                                    help='The total net weight used')
    total_product_qty = fields.Float(string='Total Quantity',
                                     compute='_compute_total_order_price',
                                     help='The total net weight used')
    order_ids = fields.One2many('freight.order.line', 'order_id',
                                string='Freight Order Line',
                                help='The freight order lines of the order')
    route_ids = fields.One2many('freight.order.routes.line', 'freight_id',
                                string='Route', help='The route of order')
    total_route_sale = fields.Float(string='Total Sale',
                                    compute="_compute_total_route_cost",
                                    help='The total cost of sale')
    service_ids = fields.One2many('freight.order.service', 'freight_id',
                                  string="Service", help='Service of the order')
    total_service_sale = fields.Float(string='Service Total Sale',
                                      compute="_compute_total_service_cost",
                                      help='The total service cost of order')
    agent_id = fields.Many2one('res.partner', string='Freight Forwarder', tracking=True,
                               required=True, help="Details of agent")
    expected_date_departure = fields.Date(string='ETD', tracking=True, help='The expected date'
                                                                            'of departure')
    expected_date = fields.Date(string='ETA', tracking=True, help='The expected date'
                                                                  'of the arrival')
    expected_transit_days = fields.Integer(string='ETT Days', compute='_compute_expected_transit_days',
                                           store=True, tracking=True, help='The estimated transit days')
    track_ids = fields.One2many('freight.track', 'freight_id', tracking=True,
                                string='Tracking', help='For tracking the'
                                                        'freight orders')
    document_ids = fields.One2many('freight.order.documents', 'freight_id',
                                   string='Documents', help='For attaching the'
                                                            'freight order documents')
    log_ids = fields.One2many('freight.order.logs', 'freight_id',
                              string='Logs', help='For attaching the'
                                                  'freight order logs')
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True, tracking=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)
    plan_field = fields.Many2one('freight.management', string="Plan", tracking=True, required=False)
    insurance = fields.Integer(string="Insurance", store=True,
                               readonly=False, required=False)
    one_thousand = fields.Float(string="1/1000", compute="_compute_one_thousand", required=False)
    bank_id = fields.Many2one('managing.bank', string="Bank", tracking=True,
                              help="Select the bank for this freight order")
    project_count = fields.Integer(string='Projects', compute='_compute_project_count')
    show_project_button = fields.Boolean(compute='_compute_project_button')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', help='Related Purchase Order')
    purchase_count = fields.Integer(compute='_compute_purchase_count', string="Purchase Orders")
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', help='Related Sales Order')
    sales_count = fields.Integer(compute='_compute_sales_count', string="Sale Orders")
    acid_number = fields.Char(string="ACID Number", tracking=True, required=False)
    bill_of_lading = fields.Char(string="Bill Of Lading", tracking=True, required=False)
    # file_upload = fields.Binary(string="File Upload", required=False)
    stage_id = fields.Many2one('freight.order.stage', string="Stage",
                               default=lambda self: self._default_stage())
    free_days = fields.Integer(string="Free Days", tracking=True, required=False)
    actual_date_departure = fields.Date(string="ATD", tracking=True, required=False,
                                        help='The actual time of departure')
    receiving_date = fields.Date(string="ATA", tracking=True, required=False, help='The actual time of arrival')
    actual_transit_days = fields.Integer(string="ATT Days", compute='_compute_actual_transit_days',
                                         store=True, tracking=True, help='The actual transit days')
    end_date = fields.Date(string="Free Days Remaining", compute="_compute_end_date", required=False)
    end_date_date = fields.Char(string="Free Days End Date", compute="_compute_end_date_date", required=False)
    remaining_days_text = fields.Char(string="Days Remaining", compute="_compute_remaining_days_text", required=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    # import_declaration = fields.Integer(string="Import Declaration", required=False, )
    # export_declaration = fields.Integer(string="Export Declaration", required=False, )
    source_import_declaration = fields.Char(string="Source Import Declaration", required=False, )
    import_declaration2 = fields.Char(string="Import Declaration", required=False, )
    export_declaration2 = fields.Char(string="Export Declaration", required=False, )
    twohundred_tax = fields.Float(string="Gafi", required=False, compute='_compute_twohundred_tax', store=True,
                                  help="This field is calculating 2/100 of total invoice for Gafi")
    gafi_invoice_count = fields.Integer(
        string="Gafi Invoice Count",
        compute="_compute_gafi_invoice_count"
    )
    one_thousand_invoice_count = fields.Integer(
        string="1/1000 Invoice Count",
        compute="_compute_one_thousand_invoice_count"
    )
    incoterm = fields.Many2one('account.incoterms', 'Incoterm',
                               help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    incoterm_location = fields.Char(string='Incoterm Location')
    vessel = fields.Char('Vessel', required=False)
    voyage = fields.Char('Voyage', required=False)
    shipping_line = fields.Char('Shipping Line', required=False)
    create_analytic = fields.Boolean(string='Create Analytic?', required=False)
    create_project = fields.Boolean(string='Create Project?', required=False)
    last_computed_date = fields.Date(string="Last Computed Date", default=fields.Date.today)

    @api.model
    def update_remaining_days_computation(self):
        """Cron job method to trigger recomputation of remaining days"""
        today = fields.Date.today()
        # Find all active freight orders that need updating
        orders = self.search([
            ('receiving_date', '!=', False),
            ('free_days', '>', 0),
            ('last_computed_date', '!=', today)
        ])

        if orders:
            # Update the trigger field to force recomputation
            orders.write({'last_computed_date': today})
            _logger.info(f"Updated {len(orders)} freight orders for daily remaining days computation")

    @api.depends('name')
    def _compute_one_thousand_invoice_count(self):
        for rec in self:
            rec.one_thousand_invoice_count = self.env['account.move'].search_count([
                ('ref', '=', f"{rec.name} - 1/1000 Tax")
            ])

    def action_view_one_thousand_invoices(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('ref', '=', f"{self.name} - 1/1000 Tax")
        ])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', invoices.ids)]
        action['context'] = {'create': False}
        return action

    def _compute_sale_order_names(self):  # Add this method if you have a similar field for sales
        for rec in self:
            orders = self.env['sale.order'].search([
                '|',
                ('freight_order_id', '=', rec.id),
                ('id', '=', rec.sale_order_id.id if rec.sale_order_id else False)
            ])
            rec.sale_order_names = ', '.join(orders.mapped('name')) if orders else ''

    def _compute_purchase_order_names(self):
        for rec in self:
            # Find purchase orders related to this freight order in two ways:
            # 1. Purchase orders that have this freight as their main freight_order_id
            # 2. The purchase order referenced directly in this freight's purchase_order_id field

            orders = self.env['purchase.order'].search([
                '|',
                ('freight_order_id', '=', rec.id),  # Main freight reference
                ('id', '=', rec.purchase_order_id.id if rec.purchase_order_id else False)  # Direct reference
            ])

            rec.purchase_order_names = ', '.join(orders.mapped('name')) if orders else ''

    def action_create_one_thousand_tax_invoice(self):
        """Create invoice only for 1/1000 tax"""
        self.ensure_one()
        if not self.one_thousand:
            raise UserError("1/1000 tax is 0. Cannot create invoice.")

        lines = [(0, 0, {
            'name': '1/1000 Tax',
            'price_unit': self.one_thousand,
            'quantity': 1.0,
        })]

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.shipper_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'ref': f"{self.name} - 1/1000 Tax",
            'invoice_line_ids': lines,
        }

        inv = self.env['account.move'].create(invoice_vals)

        return {
            'name': '1/1000 Tax Invoice',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': inv.id,
            'res_model': 'account.move',
        }

    @api.depends('name')
    def _compute_gafi_invoice_count(self):
        for rec in self:
            rec.gafi_invoice_count = self.env['account.move'].search_count([
                ('ref', '=', f"{rec.name} - 2/100 Tax")
            ])

    def action_view_gafi_invoices(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('ref', '=', f"{self.name} - 2/100 Tax")
        ])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', invoices.ids)]
        action['context'] = {'create': False}
        return action

    @api.depends('total_order_price')
    def _compute_twohundred_tax(self):
        for rec in self:
            rec.twohundred_tax = rec.total_order_price * 0.02

    @api.depends('receiving_date', 'free_days')
    def _compute_end_date(self):
        for record in self:
            if record.receiving_date and record.free_days:
                record.end_date = record.receiving_date + timedelta(days=record.free_days)
            else:
                record.end_date = False

    @api.depends('receiving_date', 'free_days')
    def _compute_end_date_date(self):
        """Compute End Date as receiving_date + free_days and format as MM/DD/YYYY"""
        for record in self:
            if record.receiving_date and record.free_days:
                end_date = record.receiving_date + timedelta(days=record.free_days)
                record.end_date_date = end_date.strftime('%m/%d/%Y')  # Format as MM/DD/YYYY
            else:
                record.end_date_date = ''

    @api.depends('receiving_date', 'free_days')
    def _compute_remaining_days_text(self):
        """Compute remaining days as text - always shows days regardless of threshold"""
        for record in self:
            if record.receiving_date and record.free_days:
                end_date = record.receiving_date + timedelta(days=record.free_days)
                today = fields.Date.today()
                days_diff = (end_date - today).days

                if days_diff > 0:
                    record.remaining_days_text = f"{days_diff} days remaining"
                elif days_diff == 0:
                    record.remaining_days_text = "Today"
                else:
                    record.remaining_days_text = f"{abs(days_diff)} days ago"
            else:
                record.remaining_days_text = ""

    @api.depends('expected_date_departure', 'expected_date')
    def _compute_expected_transit_days(self):
        for record in self:
            if record.expected_date and record.expected_date_departure:
                delta = record.expected_date - record.expected_date_departure
                record.expected_transit_days = delta.days
            else:
                record.expected_transit_days = 0

    @api.depends('actual_date_departure', 'receiving_date')
    def _compute_actual_transit_days(self):
        for record in self:
            if record.receiving_date and record.actual_date_departure:
                delta = record.receiving_date - record.actual_date_departure
                record.actual_transit_days = delta.days
            else:
                record.actual_transit_days = 0

    def _default_stage(self):
        return self.env['freight.order.stage'].search([], order='sequence', limit=1)

    # def _compute_purchase_count(self):
    #     for record in self:
    #         record.purchase_count = self.env['purchase.order'].search_count([('freight_order_id', '=', record.id)])

    def _compute_purchase_count(self):
        for record in self:
            # Count purchase orders related to this freight order in two ways:
            # 1. Purchase orders that have this freight as their main freight_order_id
            # 2. The purchase order referenced directly in this freight's purchase_order_id field

            record.purchase_count = self.env['purchase.order'].search_count([
                '|',
                ('freight_order_id', '=', record.id),  # Main freight reference
                ('id', '=', record.purchase_order_id.id if record.purchase_order_id else False)  # Direct reference
            ])

    # @api.depends('total_order_price')
    # def _compute_insurance(self):
    #     for record in self:
    #         record.insurance = record.total_order_price / 5 if record.total_order_price else 0.0

    @api.depends('insurance')
    def _compute_one_thousand(self):
        for record in self:
            record.one_thousand = record.insurance / 1000 if record.insurance else 0.0

    # def _compute_sales_count(self):
    #     for record in self:
    #         record.sales_count = self.env['sale.order'].search_count([('freight_order_id', '=', record.id)])

    def _compute_sales_count(self):
        for record in self:
            record.sales_count = self.env['sale.order'].search_count([
                '|',
                ('freight_order_id', '=', record.id),
                ('id', '=', record.sale_order_id.id if record.sale_order_id else False)
            ])

    def action_view_purchase_orders(self):
        # Find purchase orders related to this freight order in two ways:
        # 1. Purchase orders that have this freight as their main freight_order_id
        # 2. The purchase order referenced directly in this freight's purchase_order_id field

        purchase_orders = self.env['purchase.order'].search([
            '|',
            ('freight_order_id', '=', self.id),  # Main freight reference
            ('id', '=', self.purchase_order_id.id if self.purchase_order_id else False)  # Direct reference
        ])

        if len(purchase_orders) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': purchase_orders.id,  # Open the single record directly
            }

        return {
            'name': 'Purchase Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', purchase_orders.ids)],
            'context': {'create': False},
        }

    # def action_view_purchase_orders(self):
    #     purchase_orders = self.env['purchase.order'].search([('freight_order_id', '=', self.id)])
    #
    #     if len(purchase_orders) == 1:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'purchase.order',
    #             'view_mode': 'form',
    #             'res_id': purchase_orders.id,  # Open the single record directly
    #         }
    #
    #     return {
    #         'name': 'Purchase Orders',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'list,form',
    #         'res_model': 'purchase.order',
    #         'domain': [('id', 'in', purchase_orders.ids)],
    #         'context': {'create': False},
    #     }

    def action_view_sales_orders(self):
        # Find sales orders related to this freight order in two ways:
        # 1. Sales orders that have this freight as their main freight_order_id
        # 2. The sales order referenced directly in this freight's sale_order_id field

        sales_orders = self.env['sale.order'].search([
            '|',
            ('freight_order_id', '=', self.id),  # Main freight reference
            ('id', '=', self.sale_order_id.id if self.sale_order_id else False)  # Direct reference
        ])

        if len(sales_orders) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'res_id': sales_orders.id,  # Open the single record directly
            }

        return {
            'name': 'Sales Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sales_orders.ids)],
            'context': {'create': False},
        }

    def _compute_project_count(self):
        for rec in self:
            rec.project_count = self.env['project.project'].search_count([('name', '=', rec.name)])

    def _compute_project_button(self):
        for rec in self:
            rec.show_project_button = rec.project_count > 0

    def action_view_project_ids(self):
        self.ensure_one()
        projects = self.env['project.project'].search([('name', '=', self.name)])
        action = self.env.ref('project.open_view_project_all').read()[0]
        if len(projects) > 1:
            action['domain'] = [('id', 'in', projects.ids)]
        elif projects:
            action['views'] = [(self.env.ref('project.edit_project').id, 'form')]
            action['res_id'] = projects.id
        return action

    @api.depends('order_ids.total_price', 'order_ids.volume',
                 'order_ids.weight', 'order_ids.net_weight')
    def _compute_total_order_price(self):
        """Computing the price of the order"""
        for rec in self:
            rec.total_order_price = sum(rec.order_ids.mapped('total_price'))
            rec.total_volume = sum(rec.order_ids.mapped('volume'))
            rec.total_weight = sum(rec.order_ids.mapped('total_gross'))
            rec.total_net_weight = sum(rec.order_ids.mapped('total_net'))
            rec.total_product_qty = sum(rec.order_ids.mapped('product_qty'))

    @api.depends('route_ids.sale')
    def _compute_total_route_cost(self):
        """Computing the total cost of route operation"""
        for rec in self:
            rec.total_route_sale = sum(rec.route_ids.mapped('sale'))

    @api.depends('service_ids.total_sale')
    def _compute_total_service_cost(self):
        """Computing the total cost of services"""
        for rec in self:
            rec.total_service_sale = sum(rec.service_ids.mapped('total_sale'))

    @api.model_create_multi
    def create(self, vals_list):
        """Create Sequence for multiple records"""
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'freight.order.sequence')
        return super(FreightOrder, self).create(vals_list)

    def action_create_custom_clearance(self):
        """Create custom clearance"""
        clearance = self.env['custom.clearance'].create({
            'name': 'CC - ' + self.name,
            'freight_id': self.id,
            'date': self.order_date,
            'consignee_id': self.consignee_id.id,
            'loading_port_id': self.loading_port_id.id,
            'discharging_port_id': self.discharging_port_id.id,
            'agent_id': self.agent_id.id,
        })
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': clearance.id,
            'res_model': 'custom.clearance',
        }
        self.clearance = True
        return result

    def get_custom_clearance(self):
        """Get custom clearance"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Clearance',
            'view_mode': 'list,form',
            'res_model': 'custom.clearance',
            'domain': [('freight_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_track_order(self):
        """Track the order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Received/Delivered',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'freight.order.track',
            'context': {
                'default_freight_id': self.id
            }
        }

    def action_create_bill(self):
        """Create an empty Vendor Bill"""

        bill_data = {
            'move_type': 'in_invoice',  # ✅ Change to Vendor Bill
            'partner_id': self.shipper_id.id,  # The vendor (Shipper)
            'invoice_user_id': self.env.user.id,  # Assigned user
            'invoice_origin': self.name,  # Reference
            'ref': self.name,  # Reference field
            'invoice_line_ids': [],  # ✅ Create an EMPTY Bill (No lines)
        }

        bill = self.env['account.move'].create(bill_data)

        result = {
            'name': 'Vendor Bill',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': bill.id,
            'res_model': 'account.move',
        }

        self.state = 'invoice'  # Update state
        return result

    def action_create_invoice(self):
        """Create invoice"""
        lines = []
        if self.order_ids:
            for order in self.order_ids:
                value = (0, 0, {
                    'name': order.product_id.name,
                    'price_unit': order.price,
                    'quantity': order.volume + order.weight,
                })
                lines.append(value)
        if self.route_ids:
            for route in self.route_ids:
                value = (0, 0, {
                    'name': route.routes_id.name,
                    'price_unit': route.sale,
                })
                lines.append(value)
        if self.service_ids:
            for service in self.service_ids:
                value = (0, 0, {
                    'name': service.service_id.name,
                    'price_unit': service.sale,
                    'quantity': service.qty
                })
                lines.append(value)
        invoice_line = {
            'move_type': 'out_invoice',
            'partner_id': self.shipper_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'ref': self.name,
            'invoice_line_ids': lines,
        }
        inv = self.env['account.move'].create(invoice_line)
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': inv.id,
            'res_model': 'account.move',
        }
        self.state = 'invoice'
        return result

    # def action_create_twohundred_tax_invoice(self):
    #     """Create invoice only for 2/100 tax"""
    #     self.ensure_one()
    #     if not self.twohundred_tax:
    #         raise UserError("Twohundred tax is 0. Cannot create invoice.")
    #
    #     lines = [(0, 0, {
    #         'name': 'GAFI 2/100 Tax',
    #         'price_unit': self.twohundred_tax,
    #         'quantity': 1.0,
    #     })]
    #
    #     invoice_line = {
    #         'move_type': 'in_invoice',
    #         'partner_id': self.shipper_id.id,
    #         'invoice_user_id': self.env.user.id,
    #         'invoice_origin': self.name,
    #         'ref': f"{self.name} - 2/100 Tax",
    #         'invoice_line_ids': lines,
    #     }
    #
    #     inv = self.env['account.move'].create(invoice_line)
    #
    #     result = {
    #         'name': '2/100 Tax Invoice',
    #         'type': 'ir.actions.act_window',
    #         'views': [[False, 'form']],
    #         'target': 'current',
    #         'res_id': inv.id,
    #         'res_model': 'account.move',
    #     }
    #
    #     return result

    def action_create_twohundred_tax_invoice(self):
        """Create customer invoice only for 2/100 tax"""
        self.ensure_one()
        if not self.twohundred_tax:
            raise UserError("2/100 tax is 0. Cannot create bill.")

        # 👇 Find customer "GENERAL AUTHORITY FOR INVESTMENT AND FREE ZONES"
        gafi_partner = self.env['res.partner'].search([
            ('name', '=', 'GENERAL AUTHORITY FOR INVESTMENT AND FREE ZONES')
        ], limit=1)
        if not gafi_partner:
            raise UserError(
                "Customer 'GENERAL AUTHORITY FOR INVESTMENT AND FREE ZONES' not found. Please create it in Contacts.")

        # 👇 Find product "GAFI"
        gafi_product = self.env['product.product'].search([
            ('name', '=', '2/100 GAFI Charge')
        ], limit=1)
        if not gafi_product:
            raise UserError("Product '2/100 GAFI Charge' not found. Please create it in Products.")

        # 👇 Invoice line
        lines = [(0, 0, {
            'product_id': gafi_product.id,
            'name': f"{gafi_product.name} - 2/100",
            'price_unit': self.twohundred_tax,
            'quantity': 1.0,
            'account_id': gafi_product.property_account_expense_id.id
                          or gafi_product.categ_id.property_account_expense_categ_id.id,
            'tax_ids': [(6, 0, gafi_product.taxes_id.ids)],
        })]

        invoice_vals = {
            'move_type': 'in_invoice',
            'partner_id': gafi_partner.id,  # Fixed customer
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'ref': f"{self.name} - 2/100 Tax",
            'invoice_line_ids': lines,
        }

        inv = self.env['account.move'].create(invoice_vals)

        return {
            'name': '2/100 Tax Bill',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': inv.id,
            'res_model': 'account.move',
        }

    def action_cancel(self):
        """Cancel the record"""
        if self.state == 'draft' and self.state == 'submit':
            self.state = 'cancel'
        else:
            raise ValidationError("You can't cancel this order")

    def get_invoice(self):
        """View the invoice"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.name)],
            'context': "{'create': False}"
        }

    @api.depends('name')
    def _compute_count(self):
        """Compute custom clearance and account move's count"""
        for rec in self:
            if rec.env['custom.clearance'].search(
                    [('freight_id', '=', rec.id)]):
                rec.clearance_count = rec.env['custom.clearance'].search_count(
                    [('freight_id', '=', rec.id)])
            else:
                rec.clearance_count = 0
            if rec.env['account.move'].search([('ref', '=', rec.name)]):
                rec.invoice_count = rec.env['account.move'].search_count(
                    [('ref', '=', rec.name)])
            else:
                rec.invoice_count = 0

    def action_submit(self):
        """Submitting order and confirming the linked freight record"""
        for rec in self:
            rec.state = 'submit'

            if rec.create_project:
                tag = self.env['project.tags'].search([('name', '=', rec.plan_field.name)], limit=1)
                if not tag:
                    tag = self.env['project.tags'].create({'name': rec.plan_field.name})

                self.env['project.project'].create({
                    'name': rec.name,
                    'tag_ids': [(6, 0, [tag.id])]
                })

            # self.env['project.project'].create({
            #     'name': rec.name,
            #     # 'tag_ids': [(6, 0, [rec.plan_field.id])]
            # })

            # Check if a freight record is linked
            if rec.plan_field:
                rec.plan_field.order_code = rec.name
                rec.plan_field.action_confirm()

            # Create a new bank line if bank_id is selected
            if rec.bank_id:
                self.env['managing.bank.line'].create({
                    'bank_id': rec.bank_id.id,
                    'freight_number': rec.name,
                    'amount': rec.insurance,
                })

            # ✅ CREATE ANALYTIC ACCOUNT
            if rec.create_analytic:
                analytic_account = self.env['account.analytic.account'].create({
                    'name': rec.name,
                    # 'partner_id': rec.shipper_id.id,
                })
                rec.analytic_account_id = analytic_account.id

    def action_confirm(self):
        """Confirm order and create an analytic account"""
        for rec in self:
            custom_clearance = self.env['custom.clearance'].search([
                ('freight_id', '=', self.id)])
            if custom_clearance:
                for clearance in custom_clearance:
                    if clearance.state == 'confirm':
                        rec.state = 'confirm'

                    elif clearance.state == 'draft':
                        raise ValidationError("The custom clearance '%s' is "
                                              "not confirmed" % clearance.name)
            else:
                raise ValidationError(
                    "Create a custom clearance for %s" % rec.name)
            for line in rec.order_ids:
                line.container_id.state = 'reserve'

    def action_done(self):
        """Mark order as done"""
        for rec in self:
            self.state = 'done'
            for line in rec.order_ids:
                line.container_id.state = 'available'


class FreightOrderLine(models.Model):
    """Freight order lines are defined"""
    _name = 'freight.order.line'
    _description = 'Freight Order Line'

    item_number = fields.Char(string='Item', readonly=True)

    @api.model
    def create(self, vals):
        if 'order_id' in vals:
            order_id = vals['order_id']
            order = self.env['freight.order'].browse(order_id)
            existing_lines = self.search_count([('order_id', '=', order.id)])
            vals['item_number'] = str(existing_lines + 1).zfill(3)  # '001', '002', etc.
        return super(FreightOrderLine, self).create(vals)

    order_id = fields.Many2one('freight.order', string="Freight Order",
                               help="Reference from freight order")
    container_id = fields.Many2one('freight.container', string='Container',
                                   domain="[('state', '=', 'available')]",
                                   help='The freight container')
    product_id = fields.Many2one('product.product', string='Goods',
                                 help='The Freight Products')
    billing_type = fields.Selection([('weight', 'Weight'),
                                     ('volume', 'Volume')], string="Billing On",
                                    help='Select the billing type for'
                                         'calculating the total amount')
    pricing_id = fields.Many2one('freight.price', string='Pricing',
                                 help='The pricing of order')
    price = fields.Float(string='Unit Price', help='Unit price of the selected'
                                                   'goods')
    total_price = fields.Float(string='Total Price', compute="_compute_total_price", help='This will be the'
                                                                                          'total price')
    volume = fields.Float(string='Volume', help='Volume of the goods')
    weight = fields.Float(string='Gross Weight', help='Gross Weight of the goods')
    net_weight = fields.Float(string='Net Weight', help='Net Weight of the goods')
    product_display_name = fields.Char(string="Product Description")
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True,
                               store=True, readonly=False)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure", compute="_compute_product_uom",
        store=True, readonly=False)
    total_gross = fields.Float(string='Total Gross Weight', digits=(16, 2), compute="_compute_totals", store=True)
    total_net = fields.Float(string='Total Net Weight', digits=(16, 2), compute="_compute_totals", store=True)
    secondary_uom_id = fields.Many2one('uom.uom', compute='_quantity_secondary_compute',
                                       string="ALT UOM", readonly=False, store=True)
    secondary_quantity = fields.Float('ALT Qty', compute='_quantity_secondary_compute',
                                      digits='Product Unit of Measure', readonly=False, store=True)

    @api.depends('product_id', 'product_qty', 'product_uom')
    def _quantity_secondary_compute(self):
        for order in self:
            if order.product_id.secondary_uom:
                uom_quantity = order.product_id.uom_id._compute_quantity(order.product_qty,
                                                                         order.product_id.secondary_uom_id,
                                                                         rounding_method='HALF-UP')
                order.update({'secondary_uom_id': order.product_id.secondary_uom_id})
                order.update({'secondary_quantity': uom_quantity})

    # @api.onchange('secondary_quantity')
    # def _onchange_secondary_quantity(self):
    #     """Compute main qty when secondary qty is changed manually"""
    #     for line in self:
    #         if line.product_id and line.secondary_uom_id and line.secondary_quantity:
    #             main_qty = line.secondary_uom_id._compute_quantity(
    #                 line.secondary_quantity,
    #                 line.product_id.uom_id,
    #             )
    #             line.product_qty = float(round(main_qty, 6))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-populate product data when product is selected"""
        if self.product_id:
            self.product_display_name = self.product_id.display_name or self.product_id.name
            self.price = self.product_id.list_price
            self.product_uom = self.product_id.uom_id
            # self.secondary_uom_id = self.product_id.secondary_uom_id
            # self.secondary_quantity = self.product_id.secondary_quantity

            # Set default quantity to 1 if not set
            if not self.product_qty:
                self.product_qty = 1.0

            # If product has weight information, populate it
            if hasattr(self.product_id, 'weight') and self.product_id.weight:
                self.weight = self.product_id.weight

            # If product has net weight information, populate it
            if hasattr(self.product_id, 'net_weight') and self.product_id.net_weight:
                self.net_weight = self.product_id.net_weight

            # If product has volume information, populate it
            if hasattr(self.product_id, 'volume') and self.product_id.volume:
                self.volume = self.product_id.volume

        else:
            # Clear fields when product is removed
            self.product_display_name = False
            self.price = 0.0
            self.product_uom = False
            self.weight = 0.0
            self.volume = 0.0

    @api.depends('weight', 'net_weight', 'product_qty')
    def _compute_totals(self):
        for line in self:
            line.total_gross = line.weight * line.product_qty
            line.total_net = line.net_weight * line.product_qty

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            line.product_uom = line.product_id.uom_id

    @api.constrains('weight')
    def _check_weight(self):
        """Checking the weight of containers"""
        for rec in self:
            if rec.container_id and rec.billing_type:
                if rec.billing_type == 'weight':
                    if rec.container_id.weight < rec.weight:
                        raise ValidationError(
                            'The weight is must be less '
                            'than or equal to %s' % (rec.container_id.weight))

    @api.constrains('volume')
    def _check_volume(self):
        """Checking the volume of containers"""
        for rec in self:
            if rec.container_id and rec.billing_type:
                if rec.billing_type == 'volume':
                    if rec.container_id.volume < rec.volume:
                        raise ValidationError(
                            'The volume is must be less '
                            'than or equal to %s' % (rec.container_id.volume))

    @api.depends('product_qty', 'price')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.product_qty * record.price if record.product_qty and record.price else 0.0

    @api.onchange('pricing_id', 'billing_type')
    def _onchange_price(self):
        """Calculate the weight and volume of container"""
        for rec in self:
            if rec.billing_type == 'weight':
                rec.volume = 0.00
                rec.price = rec.pricing_id.weight
            elif rec.billing_type == 'volume':
                rec.weight = 0.00
                rec.price = rec.pricing_id.volume

    @api.onchange('pricing_id', 'billing_type', 'volume', 'weight')
    def _onchange_total_price(self):
        """Calculate sub total price"""
        for rec in self:
            if rec.billing_type and rec.pricing_id:
                if rec.billing_type == 'weight':
                    rec.total_price = rec.weight * rec.price
                elif rec.billing_type == 'volume':
                    rec.total_price = rec.volume * rec.price


class FreightOrderRoutesLine(models.Model):
    """Defining the routes for the shipping, also we can add the operations for
    the routes."""
    _name = 'freight.order.routes.line'
    _description = 'Freight Order Routes Lines'

    freight_id = fields.Many2one('freight.order', string='Freight Order',
                                 help='Relation from freight order')
    routes_id = fields.Many2one('freight.routes', required=True,
                                string='Routes', help='Select route of freight')
    source_loc_id = fields.Many2one('freight.port', string='Source Location',
                                    help='Select the source port')
    destination_loc_id = fields.Many2one('freight.port',
                                         string='Destination Location',
                                         help='Select the destination port')
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water'), ('warehouse_pickup', 'Warehouse Pickup')],
                                      string="Transport",
                                      required=True,
                                      help='Select the transporting medium')
    sale = fields.Float(string='Sale', help="Set the price for Land")
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)

    @api.onchange('routes_id', 'transport_type')
    def _onchange_routes_id(self):
        """Calculate the price of route operation"""
        for rec in self:
            if rec.routes_id and rec.transport_type:
                if rec.transport_type == 'land':
                    rec.sale = rec.routes_id.land_sale
                elif rec.transport_type == 'air':
                    rec.sale = rec.routes_id.air_sale
                elif rec.transport_type == 'water':
                    rec.sale = rec.routes_id.water_sale


class FreightOrderServiceLine(models.Model):
    """Services in freight orders"""
    _name = 'freight.order.service'
    _description = 'Freight Order Service'

    freight_id = fields.Many2one('freight.order', string='Freight Order',
                                 help='Relation from freight order')
    service_id = fields.Many2one('freight.service', required=True,
                                 string='Service', help='Select the service')
    partner_id = fields.Many2one('res.partner', string="Vendor",
                                 help='Select the partner for the service')
    qty = fields.Float(string='Quantity', help='How many Quantity required')
    cost = fields.Float(string='Cost', help='The cost price of the service')
    sale = fields.Float(string='Sale', help='Sale price of the service')
    total_sale = fields.Float('Total Sale', help='The total sale price')
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)

    @api.onchange('service_id', 'partner_id')
    def _onchange_partner_id(self):
        """Calculate the price of services"""
        for rec in self:
            if rec.service_id:
                if rec.partner_id:
                    if rec.service_id.line_ids:
                        for service in rec.service_id.line_ids:
                            if rec.partner_id == service.partner_id:
                                rec.sale = service.sale
                            else:
                                rec.sale = rec.service_id.sale_price
                    else:
                        rec.sale = rec.service_id.sale_price
                else:
                    rec.sale = rec.service_id.sale_price

    @api.onchange('qty', 'sale')
    def _onchange_qty(self):
        """Calculate the subtotal of route operation"""
        for rec in self:
            rec.total_sale = rec.qty * rec.sale


class Tracking(models.Model):
    """Tracking the freight order"""
    _name = 'freight.track'
    _description = 'Freight Track'

    source_loc_id = fields.Many2one('freight.port', string='Source Location',
                                    help='Select the source location of port')
    destination_loc_id = fields.Many2one('freight.port',
                                         string='Destination Location',
                                         help='Destination location of the port')
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], string='Transport',
                                      help='Transporting medium of the order')
    freight_id = fields.Many2one('freight.order', string='Freight Order',
                                 help='Reference from freight order')
    date = fields.Date(string='Date', help='Select the date')
    type = fields.Selection([('received', 'Received'),
                             ('delivered', 'Delivered')],
                            string='Received/Delivered',
                            help='Status of the order')
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Current company",
                                 default=lambda
                                     self: self.env.company.id)
