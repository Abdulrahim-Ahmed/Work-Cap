/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    // Get employees using the data directly from loaded data
    getEmployees() {
        console.log("=== POS SALESPERSON DEBUG: getEmployees called ===");
        console.log("this.data:", this.data);
        console.log("this.data keys:", this.data ? Object.keys(this.data) : "NO_DATA");
        console.log("this.data['hr.employee']:", this.data ? this.data["hr.employee"] : "NO_DATA");
        
        try {
            const result = this.data["hr.employee"]?.data || [];
            console.log("getEmployees result:", result);
            console.log("=== POS SALESPERSON DEBUG: getEmployees complete ===");
            return result;
        } catch (e) {
            console.error("Error in getEmployees:", e);
            return [];
        }
    },

    // Access employees data for compatibility
    get employees() {
        console.log("=== POS SALESPERSON DEBUG: employees getter called ===");
        try {
            const result = this.getEmployees();
            console.log("employees getter result:", result);
            return result;
        } catch (e) {
            console.error("Error in employees getter:", e);
            return [];
        }
    },
});
