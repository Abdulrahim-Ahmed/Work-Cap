from odoo import models, fields, api, _


class SaleOrderDateWizard(models.TransientModel):
    _name = 'sale.order.date.wizard'
    _description = 'Wizard to Change Sale Order Date'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    new_date_order = fields.Date(string='New Order Date', required=True)



    # def button_confirm(self):
    #     self.ensure_one()
    #     sale_order = self.env['sale.order'].browse(self.env.context.get('default_sale_order_id'))
    #     if sale_order:
    #         sale_order.with_context(wizard_confirmed=True).write({'date_order': self.new_date_order})
    #         sale_order.with_context(wizard_confirmed=True).action_confirm()
    #     return {'type': 'ir.actions.act_window_close'}

    def button_confirm(self):
        self.ensure_one()
        sale_order = self.env['sale.order'].browse(self.env.context.get('default_sale_order_id'))
        if sale_order:
            sale_order.write({'date_order': self.new_date_order})
            # Trigger the order confirmation
            sale_order.with_context(wizard_confirmed=True).action_confirm()
        return {'type': 'ir.actions.act_window_close'}

