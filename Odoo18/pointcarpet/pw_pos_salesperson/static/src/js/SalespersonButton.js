/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

console.log('=== POS SALESPERSON DEBUG: SalespersonButton.js loaded ===');

export class SalespersonButton extends Component {
    static template = "pw_pos_salesperson.SalespersonButton";
    static props = {
        class: { type: String, optional: true },
    };
    static defaultProps = {
        class: "btn btn-light btn-lg lh-lg",
    };

    setup() {
        console.log('=== POS SALESPERSON DEBUG: SalespersonButton setup initiated');
        
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        
        console.log('=== POS SALESPERSON DEBUG: SalespersonButton setup completed');
    }

    get buttonText() {
        return _t("Salesperson");
    }

    async onClick() {
        console.log("=== POS SALESPERSON DEBUG: SalespersonButton click called ===");
        console.log("this.pos:", this.pos);
        console.log("this.pos.data:", this.pos.data);
        console.log("this.pos.data keys:", this.pos.data ? Object.keys(this.pos.data) : "NO_DATA");
        
        try {
            const order = this.pos.get_order();
            if (!order) {
                console.error('=== POS SALESPERSON DEBUG: No active order found');
                this.notification.add(_t("No active order to assign salesperson"), {
                    type: 'danger',
                    sticky: false,
                });
                return;
            }

            // Get employees from different possible sources in Odoo 18
            let employees = [];
            
            // Method 1: Try pos.data["hr.employee"]
            if (this.pos.data && this.pos.data["hr.employee"]) {
                const hrEmployeeData = this.pos.data["hr.employee"];
                console.log("=== POS SALESPERSON DEBUG: hr.employee data structure:", hrEmployeeData);
                
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
            
            // Method 2: Try pos.data.records["hr.employee"]
            if (employees.length === 0 && this.pos.data && this.pos.data.records && this.pos.data.records["hr.employee"]) {
                const recordsMap = this.pos.data.records["hr.employee"];
                console.log("=== POS SALESPERSON DEBUG: records hr.employee type:", typeof recordsMap);
                
                if (recordsMap instanceof Map) {
                    employees = Array.from(recordsMap.values());
                } else if (typeof recordsMap === 'object') {
                    employees = Object.values(recordsMap);
                }
            }
            
            // Method 3: Try pos.models["hr.employee"]
            if (employees.length === 0 && this.pos.models && this.pos.models["hr.employee"]) {
                const posModel = this.pos.models["hr.employee"];
                console.log("=== POS SALESPERSON DEBUG: pos.models hr.employee:", posModel);
                
                if (posModel.records) {
                    if (posModel.records instanceof Map) {
                        employees = Array.from(posModel.records.values());
                    } else if (typeof posModel.records === 'object') {
                        employees = Object.values(posModel.records);
                    }
                }
            }
            
            console.log("=== POS SALESPERSON DEBUG: Final employees found:", employees.length);
            if (employees.length > 0) {
                console.log("=== POS SALESPERSON DEBUG: First employee:", employees[0]);
                console.log("=== POS SALESPERSON DEBUG: Employee keys:", Object.keys(employees[0] || {}));
            }
            
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
            
            console.log("=== POS SALESPERSON DEBUG: Selection list:", selectionList.slice(0, 3));
            
            // Show selection popup
            const selectedEmployee = await makeAwaitable(this.dialog, SelectionPopup, {
                title: _t("Select Salesperson"),
                list: selectionList,
            });
            
            console.log("=== POS SALESPERSON DEBUG: Dialog returned:", selectedEmployee);
            
            if (selectedEmployee === undefined) {
                console.log("=== POS SALESPERSON DEBUG: Selection cancelled");
                return;
            }
            
            if (selectedEmployee) {
                const orderLines = order.get_orderlines();
                console.log("=== POS SALESPERSON DEBUG: Setting salesperson", selectedEmployee.name, "for", orderLines.length, "lines");
                
                // Simple assignment - just set the basic properties
                for (const line of orderLines) {
                    console.log("=== POS SALESPERSON DEBUG: Setting employee for line:", line);
                    
                    // Set the employee data on the order line using simple properties
                    line.employee_id = selectedEmployee.id;
                    line.employee_name = selectedEmployee.name;
                    line.salesperson = selectedEmployee;
                    
                    console.log("=== POS SALESPERSON DEBUG: Line now has employee_id:", line.employee_id, "employee_name:", line.employee_name);
                }
                
                // Update the order with salesperson for the backend
                order.salesperson_id = selectedEmployee;
                
                // Update the visual display of salesperson on all orderlines
                if (typeof window.updateAllOrderlinesWithSalesperson === 'function') {
                    setTimeout(() => {
                        window.updateAllOrderlinesWithSalesperson(selectedEmployee.name);
                    }, 200);
                } else {
                    console.log("=== POS SALESPERSON DEBUG: updateAllOrderlinesWithSalesperson function not found");
                }
                
                // Show success notification
                this.notification.add(_t("Salesperson %s assigned to %s order lines", selectedEmployee.name, orderLines.length), {
                    type: 'success',
                    sticky: false,
                });
                
                console.log("=== POS SALESPERSON DEBUG: Salesperson assignment completed");
            }
            
        } catch (error) {
            console.error('=== POS SALESPERSON DEBUG: Error in onClick:', error);
            this.notification.add(_t("Error selecting salesperson: %s", error.message), {
                type: 'danger',
                sticky: true,
            });
        }
    }
}

console.log('=== POS SALESPERSON DEBUG: SalespersonButton class defined successfully');
