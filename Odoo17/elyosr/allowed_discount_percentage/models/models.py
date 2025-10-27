# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class HrJobDiscountPercentage(models.Model):
    _inherit = 'hr.job'

    allowed_discount_percentage = fields.Float(
        string='Allowed Discount Percentage',
        help="The maximum allowed discount percentage for this job position."
    )


class HrEmployeeDiscountPercentage(models.Model):
    _inherit = 'hr.employee'

    allowed_discount_percentage = fields.Float(string="Allowed Discount Percentage")

    @api.onchange('job_id')
    def _onchange_job_id(self):
        # When the job position changes, update the employee's allowed discount percentage
        if self.job_id:
            self.allowed_discount_percentage = self.job_id.allowed_discount_percentage
        else:
            self.allowed_discount_percentage = 0.0  # Reset if no job position is assigned

    @api.model
    def create(self, vals):
        # Ensure allowed_discount_percentage is set during employee creation
        if 'job_id' in vals:
            job = self.env['hr.job'].browse(vals['job_id'])
            vals['allowed_discount_percentage'] = job.allowed_discount_percentage
        return super(HrEmployeeDiscountPercentage, self).create(vals)

    def write(self, vals):
        # Ensure allowed_discount_percentage is updated during employee update
        if 'job_id' in vals:
            job = self.env['hr.job'].browse(vals['job_id'])
            vals['allowed_discount_percentage'] = job.allowed_discount_percentage
        return super(HrEmployeeDiscountPercentage, self).write(vals)


class SaleOrderLineDiscountPercentage(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('discount')
    def _check_allowed_discount(self):
        for line in self:
            # Get the employee associated with the sale order's user
            employee = line.order_id.user_id.employee_id
            if employee:
                # Get the allowed discount percentage from the employee's job position
                allowed_percentage = employee.allowed_discount_percentage

                # Check if the discount is more than or equal to the allowed discount percentage
                if allowed_percentage and line.discount > allowed_percentage:
                    raise exceptions.ValidationError(
                        "The discount of %.1f%% exceeds the allowed discount percentage for your position." % (
                            line.discount)
                    )