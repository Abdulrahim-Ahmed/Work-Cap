/** @odoo-module **/

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { qrCodeSrc } from "@point_of_sale/utils";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async push_single_order(order) {
        const order_id = this.db.add_order(order.export_as_JSON());
        let result = await super.push_single_order(order);
        const eg_pos_qr_code = await this.orm.call("pos.order", "get_eta_qr_code", [order_id]);
        this.get_order().eg_pos_qr_code = eg_pos_qr_code;
        return result
    },
});


patch(Order.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.pos_qr_code = this.pos.get_order().eg_pos_qr_code;
        return result;

    }
});

