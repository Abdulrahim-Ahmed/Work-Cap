from odoo import models, fields, api
from odoo.exceptions import AccessError
from odoo import models, _
from odoo.exceptions import AccessError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.picking_type_code == 'outgoing':
            if not self.env.user.has_group('cs_access_right.group_delivery_validator'):
                raise AccessError(_("You are not allowed to validate Deliveries. Contact your manager."))

        elif self.picking_type_code == 'incoming':
            if not self.env.user.has_group('cs_access_right.group_receipt_validator'):
                raise AccessError(_("You are not allowed to validate Receipts. Contact your manager."))
        return super(StockPicking, self).button_validate()


    def unlink(self):
        if not self.env.user.has_group('cs_access_right.group_stock_picking_delete'):
            raise AccessError("You are not allowed to delete Stock Operations.")
        return super().unlink()



class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_draft(self):
        if self.move_type in ['out_invoice', 'in_invoice']:
            if not self.env.user.has_group('cs_access_right.group_reset_draft'):
                raise AccessError("You are not allowed to reset Invoices/Bills to draft.")
        return super().button_draft()

    def action_register_payment(self):
        if not self.env.user.has_group('cs_access_right.group_register_payment'):
            raise AccessError("You are not allowed to make a register payment")
        return super().action_register_payment()

    def unlink(self):
        if self.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']:
            if not self.env.user.has_group('cs_access_right.group_account_move_delete'):
                raise AccessError("You are not allowed to delete Invoices/Bills/Credit Notes.")
        return super().unlink()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def action_draft(self):
    #     if not self.env.user.has_group('cs_access_right.group_reset_draft'):
    #         raise AccessError("You are not allowed to reset Sale Orders to draft.")
    #     return super().action_draft()

    def action_lock(self):
        if not self.env.user.has_group('cs_access_right.group_sale_action_lock'):
            raise AccessError("You are not allowed to Lock Sale Orders.")
        return super().action_lock()

    def action_unlock(self):
        if not self.env.user.has_group('cs_access_right.group_sale_action_unlock'):
            raise AccessError("You are not allowed to UnLock Sale Orders.")
        return super().action_unlock()

    def unlink(self):
        if not self.env.user.has_group('cs_access_right.group_sale_order_delete'):
            raise AccessError("You are not allowed to delete Sale Orders.")
        return super().unlink()


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_draft(self):
        if not self.env.user.has_group('cs_access_right.group_reset_draft'):
            raise AccessError("You are not allowed to reset Purchase Orders to draft.")
        return super().button_draft()

    def button_lock(self):
        if not self.env.user.has_group('cs_access_right.group_purchase_action_lock'):
            raise AccessError("You are not allowed to Lock Purchase Orders.")
        return super().button_lock()

    def button_unlock(self):
        if not self.env.user.has_group('cs_access_right.group_purchase_action_unlock'):
            raise AccessError("You are not allowed to UnLock Purchase Orders.")
        return super().button_unlock()

    def unlink(self):
        if not self.env.user.has_group('cs_access_right.group_purchase_order_delete'):
            raise AccessError("You are not allowed to delete Purchase Orders.")
        return super().unlink()
