/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    serialize() {
        const result = super.serialize(...arguments);
        
        // Ensure employee data is included in serialized order lines
        if (result.lines && Array.isArray(result.lines) && this.lines) {
            // Inject employee fields into the JSON payload sent to backend
            result.lines.forEach((uiLine, index) => {
                try {
                    const modelLine = this.lines[index];
                    if (!uiLine || !Array.isArray(uiLine) || uiLine.length < 3) return;
                    const vals = uiLine[2] || {};
                    const empId = modelLine?.employee_id || null;
                    if (empId !== null && empId !== undefined) {
                        vals.employee_id = empId;
                    }
                    uiLine[2] = vals;
                } catch (e) {
                    // ignore
                }
            });
        }
        return result;
    }
});