/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

console.log("=== POS SALESPERSON DEBUG: models.js loading ===");

// Patch PosOrderline to include salesperson data in display
patch(PosOrderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.employee_id = this.employee_id || null;
        this.employee_name = this.employee_name || null;
        this.salesperson = this.salesperson || null;
        console.log("=== POS SALESPERSON DEBUG: PosOrderline setup with employee data");
    },

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            salesperson: this.salesperson?.name || '',
            salesperson_name: this.salesperson?.name || '',
            has_salesperson: Boolean(this.salesperson),
        };
    },

    export_as_JSON() {
        const result = super.export_as_JSON();
        result.employee_id = this.employee_id;
        result.employee_name = this.employee_name;
        console.log("=== POS SALESPERSON DEBUG: PosOrderline exported with employee:", result.employee_id);
        return result;
    },

    init_from_JSON(json) {
        super.init_from_JSON(json);
        this.employee_id = json.employee_id || null;
        this.employee_name = json.employee_name || null;
        if (this.employee_id && this.pos) {
            // Try to find the employee object from POS data
            const employees = this.pos.employees || [];
            this.salesperson = employees.find(emp => emp.id === this.employee_id);
        }
        console.log("=== POS SALESPERSON DEBUG: PosOrderline initialized from JSON with employee:", this.employee_id);
    }
});

console.log("=== POS SALESPERSON DEBUG: models.js loaded successfully");