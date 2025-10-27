# -*- coding: utf-8 -*-
from odoo import models, fields


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    salesperson_id = fields.Many2one('hr.employee', string='Sales Employee', readonly=True)
    # salesperson_name = fields.Char(string='Salesperson Name', readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True)

    def _select(self):
        # Prioritize employee information, fallback to user's linked employee if no employee is assigned on order line
        return super(PosOrderReport, self)._select() + """
            ,CASE 
                WHEN l.employee_id IS NOT NULL THEN l.employee_id
                ELSE (SELECT he2.id FROM hr_employee he2 WHERE he2.user_id = s.user_id LIMIT 1)
             END AS salesperson_id
        """

    def _from(self):
        # Add LEFT JOINs for hr.employee and res.partner to get employee and user details
        return super(PosOrderReport, self)._from() + """
            LEFT JOIN hr_employee he ON l.employee_id = he.id
            LEFT JOIN res_users su ON s.user_id = su.id
            LEFT JOIN res_partner rp ON su.partner_id = rp.id
        """

    def _group_by(self):
        # Group by the relevant fields
        return super(PosOrderReport, self)._group_by() + """
            ,l.employee_id
            ,he.name
            ,s.user_id
            ,rp.name
        """
