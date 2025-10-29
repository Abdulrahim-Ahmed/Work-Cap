/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

console.log("=== POS SALESPERSON DEBUG: product_screen.js loading ===");

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
        console.log("=== POS SALESPERSON DEBUG: ProductScreen patched setup completed");
    },

    async changeUser(orderline) {
        console.log("=== POS SALESPERSON DEBUG: changeUser called for orderline:", orderline);
        
        // Get employees from different possible sources
        let employees = [];
        
        if (this.pos.data && this.pos.data["hr.employee"]) {
            const hrEmployeeData = this.pos.data["hr.employee"];
            if (hrEmployeeData.data) {
                employees = hrEmployeeData.data;
            } else if (Array.isArray(hrEmployeeData)) {
                employees = hrEmployeeData;
            } else if (hrEmployeeData.records) {
                if (hrEmployeeData.records instanceof Map) {
                    employees = Array.from(hrEmployeeData.records.values());
                } else if (typeof hrEmployeeData.records === 'object') {
                    employees = Object.values(hrEmployeeData.records);
                }
            }
        }
        
        if (employees.length === 0 && this.pos.data && this.pos.data.records && this.pos.data.records["hr.employee"]) {
            const recordsMap = this.pos.data.records["hr.employee"];
            if (recordsMap instanceof Map) {
                employees = Array.from(recordsMap.values());
            } else if (typeof recordsMap === 'object') {
                employees = Object.values(recordsMap);
            }
        }
        
        console.log("=== POS SALESPERSON DEBUG: Found", employees.length, "employees for selection");
        
        if (!employees || employees.length === 0) {
            this.dialog.add(AlertDialog, {
                title: _t("No Employees Found"),
                body: _t("No active employees found. Please make sure employees are created and active in the HR module."),
            });
            return;
        }

        const selectionList = employees.map(employee => ({
            id: employee.id,
            label: employee.name,
            item: employee,
        }));
        
        const { confirmed, payload: selectedEmployee } = await this.dialog.add(
            SelectionPopup,
            {
                title: _t("Select Salesperson for Line"),
                list: selectionList,
            }
        );
        
        if (confirmed && selectedEmployee) {
            console.log("=== POS SALESPERSON DEBUG: Setting employee", selectedEmployee.name, "for line");
            orderline.set_line_employee(selectedEmployee);
        }
    },

    removeUser(orderline) {
        console.log("=== POS SALESPERSON DEBUG: removeUser called for orderline:", orderline);
        orderline.set_line_employee(null);
    }
});

console.log("=== POS SALESPERSON DEBUG: product_screen.js loaded successfully");
