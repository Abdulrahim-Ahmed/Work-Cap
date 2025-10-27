/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { SalespersonVisualManager } from "./SalespersonVisualManager";


export class SalespersonButton extends Component {
    static template = "pw_pos_salesperson.SalespersonButton";
    static props = {
        class: { type: String, optional: true },
    };
    static defaultProps = {
        class: "btn btn-light btn-lg lh-lg",
    };

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.dialog = useService("dialog");
        this.notification = useService("notification");
    }

    get buttonText() {
        return _t("Salesperson");
    }

    async onClick() {
        try {
            const order = this.pos.get_order();
            if (!order) {
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
                
                if (recordsMap instanceof Map) {
                    employees = Array.from(recordsMap.values());
                } else if (typeof recordsMap === 'object') {
                    employees = Object.values(recordsMap);
                }
            }
            
            // Method 3: Try pos.models["hr.employee"]
            if (employees.length === 0 && this.pos.models && this.pos.models["hr.employee"]) {
                const posModel = this.pos.models["hr.employee"];
                
                if (posModel.records) {
                    if (posModel.records instanceof Map) {
                        employees = Array.from(posModel.records.values());
                    } else if (typeof posModel.records === 'object') {
                        employees = Object.values(posModel.records);
                    }
                }
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
            
            // Show selection popup
            const selectedEmployee = await makeAwaitable(this.dialog, SelectionPopup, {
                title: _t("Select Salesperson"),
                list: selectionList,
            });
            
            if (selectedEmployee === undefined) {
                return;
            }
            
            if (selectedEmployee) {
                const orderLines = order.get_orderlines();
                let assignedCount = 0;
                
                // Check each line - only assign to lines that don't already have individual assignments
                for (const line of orderLines) {
                    // Only assign if the line doesn't already have an individual employee assignment
                    if (!line.employee_id || !line.employee_name) {
                        // Set the employee data on the order line using simple properties
                        line.employee_id = selectedEmployee.id;
                        line.employee_name = selectedEmployee.name;
                        line.salesperson = selectedEmployee;
                        assignedCount++;
                    } else {
                    }
                }
                
                // Update the order with salesperson for the backend
                order.salesperson_id = selectedEmployee;
                
                // Update the visual display using the unified visual manager
                setTimeout(() => {
                    SalespersonVisualManager.updateAllOrderlinesDisplay(selectedEmployee.name);
                }, 200);
                
                // Show success notification
                this.notification.add(_t("General salesperson %s assigned to %s order lines", selectedEmployee.name, assignedCount), {
                    type: 'success',
                    sticky: false,
                });
            }
            
        } catch (error) {
            this.notification.add(_t("Error selecting salesperson: %s", error.message), {
                type: 'danger',
                sticky: true,
            });
        }
    }
}
