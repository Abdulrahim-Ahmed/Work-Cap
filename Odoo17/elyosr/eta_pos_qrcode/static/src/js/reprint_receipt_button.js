/** @odoo-module */

import { ReprintReceiptButton } from "@point_of_sale/app/screens/ticket_screen/reprint_receipt_button/reprint_receipt_button";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { qrCodeSrc } from "@point_of_sale/utils";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

patch(ReprintReceiptButton.prototype, {
    async click() {
            const pos_qr_code = await this.pos.orm.call("pos.order", "get_eta_qr_code", [this.props.order.name]);
            this.pos.get_order().eg_pos_qr_code = pos_qr_code;
            super.click(...arguments);
        }
    }
);
