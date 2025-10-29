from odoo import models, fields, api, _
from datetime import timedelta


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_generate_report(self):
        # Trigger the Excel report generation
        return self.env.ref('report_location_qty.product_location_report_xlsx').report_action(self)
