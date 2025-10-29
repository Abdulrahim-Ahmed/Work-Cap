/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    setup(vals) {
        // Call parent setup first
        super.setup(vals);
        
        // Initialize employee fields for serialization
        this.employee_id = vals.employee_id || false;
        this.employee_name = vals.employee_name || false;
    }
});