# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    salesperson_employee_id = fields.Many2one('hr.employee', string="Sales Person",
                                              store=True, readonly=False)
    # compute = '_compute_salesperson_employee'

    # @api.depends('user_id')
    # def _compute_salesperson_employee(self):
    #     for order in self:
    #         employee = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
    #         order.salesperson_employee_id = employee


# class SaleReportSalesTeam(models.Model):
#     _inherit = 'sale.report'
#
#     salesperson_employee_id = fields.Many2one('hr.employee', string="Sales Person",
#                                               compute='_compute_salesperson_employee', store=True, readonly=False)
#
#     def _select_sale(self):
#         select_str = super(SaleReportSalesTeam, self)._select_sale()
#         return select_str + ", s.salesperson_employee_id as salesperson_employee_id"
#
#     def _group_by_sale(self):
#         group_by_str = super(SaleReportSalesTeam, self)._group_by_sale()
#         return group_by_str + ", s.salesperson_employee_id"
#
#     def _query(self):
#         with_ = self._with_sale()
#         return f"""
#             {"WITH" + with_ + "(" if with_ else ""}
#             SELECT {self._select_sale()}
#             FROM {self._from_sale()}
#             WHERE {self._where_sale()}
#             GROUP BY {self._group_by_sale()}
#             {")" if with_ else ""}
#         """


# class PosOrderLine(models.Model):
#     _inherit = "pos.order.line"
#
#     salesperson_employee_id = fields.Many2one('hr.employee', string="Sales Person", store=True, readonly=False)
#
#
# class PosOrderReportInherit(models.Model):
#     _inherit = "report.pos.order"
#
#     # sales_person_id = fields.Many2one('hr.employee', string='Pos SalesPerson', store=True)
#     salesperson_employee_id = fields.Many2one('hr.employee', string="Sales Person", store=True, readonly=False)
#
#     def _select(self):
#         return super(PosOrderReportInherit, self)._select() + ", l.salesperson_employee_id as salesperson_employee_id"
#
#     def _from(self):
#         return super(PosOrderReportInherit,
#                      self)._from() + " LEFT JOIN pos_order_line v ON (v.id=l.salesperson_employee_id)"
#
#     def _group_by(self):
#         return super(PosOrderReportInherit, self)._group_by() + ", l.salesperson_employee_id"
