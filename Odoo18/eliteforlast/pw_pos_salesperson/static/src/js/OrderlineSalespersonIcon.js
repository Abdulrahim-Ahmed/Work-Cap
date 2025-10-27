/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { SalespersonVisualManager } from "./SalespersonVisualManager";

// POS Salesperson - OrderlineSalespersonIcon component

export class OrderlineSalespersonIcon extends Component {
    static template = "pw_pos_salesperson.OrderlineSalespersonIcon";
    static props = {
        line: { type: Object },
    };

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.dialog = useService("dialog");
        this.notification = useService("notification");
    }

    get currentEmployeeName() {
        if (this.props.line.employee_name) {
            return this.props.line.employee_name;
        }
        if (this.props.line.employee_id && this.pos.data && this.pos.data["hr.employee"]) {
            const employees = this._getEmployeesList();
            const employee = employees.find(emp => emp.id === this.props.line.employee_id);
            return employee ? employee.name : null;
        }
        return null;
    }

    get iconClass() {
        return this.currentEmployeeName ? "fa fa-user text-success" : "fa fa-user-plus text-muted";
    }

    get iconTitle() {
        return this.currentEmployeeName 
            ? _t("Assigned to: %s (click to change)", this.currentEmployeeName)
            : _t("Assign salesperson to this line");
    }


    _getEmployeesList() {
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
        
        return employees || [];
    }

    async onClick(event) {
        // Prevent event propagation to avoid selecting the orderline
        event.stopPropagation();
        // Capture container element at click time for reliable DOM update after async popup
        const containerElAtClick = (event.currentTarget?.closest && event.currentTarget.closest('.orderline'))
            || (this.el?.closest && this.el.closest('.orderline'))
            || this.el
            || event.currentTarget;
        
        try {
            const order = this.pos.get_order();
            if (!order) {
                console.error('=== POS SALESPERSON DEBUG: No active order found');
                this.notification.add(_t("No active order found"), {
                    type: 'danger',
                    sticky: false,
                });
                return;
            }

            const employees = this._getEmployeesList();
            
            if (!employees || employees.length === 0) {
                this.dialog.add(AlertDialog, {
                    title: _t("No Employees Found"),
                    body: _t("No active employees found. Please make sure employees are created and active in the HR module."),
                });
                return;
            }

            // Add option to remove salesperson
            const selectionList = [
                {
                    id: null,
                    label: _t("Remove Salesperson"),
                    item: null,
                }
            ];

            // Add employees to selection list
            selectionList.push(...employees.map(employee => ({
                id: employee.id,
                label: employee.name,
                item: employee,
            })));
            
            // Show selection popup
            const selectedEmployee = await makeAwaitable(this.dialog, SelectionPopup, {
                title: _t("Select Salesperson for Line"),
                list: selectionList,
            });
            
            if (selectedEmployee === undefined) {
                return;
            }
            
            // Find the actual orderline object in the order
            const orderLines = order.get_orderlines();
            const targetLine = orderLines.find(line => {
                // Try to match by various criteria
                return (line.product && line.product.id === this.props.line.product_id) ||
                       (line.id === this.props.line.id) ||
                       (line.cid === this.props.line.cid) ||
                       (line.get_product() && line.get_product().id === this.props.line.product_id);
            });

            if (!targetLine) {
                this.notification.add(_t("Could not find target order line"), {
                    type: 'danger',
                    sticky: false,
                });
                return;
            }

            if (selectedEmployee && selectedEmployee.id !== undefined && selectedEmployee.id !== null) {
                // Assign employee to this specific line
                targetLine.employee_id = selectedEmployee.id;
                targetLine.employee_name = selectedEmployee.name;
                targetLine.salesperson = selectedEmployee;
                
                // Update the DOM of the clicked orderline directly for immediate feedback
                SalespersonVisualManager.updateFromChildElement(containerElAtClick, selectedEmployee.name);
                
                this.notification.add(_t("Salesperson %s assigned to line", selectedEmployee.name), {
                    type: 'success',
                    sticky: false,
                });
            } else {
                // Remove employee from this line
                targetLine.employee_id = null;
                targetLine.employee_name = null;
                targetLine.salesperson = null;
                // Remove the visual display for this specific line
                SalespersonVisualManager.updateFromChildElement(containerElAtClick, null);
                
                this.notification.add(_t("Salesperson removed from line"), {
                    type: 'info',
                    sticky: false,
                });
            }

            // Trigger a re-render by updating the order and line
            try {
                // Update the line data that the template uses
                this.props.line.employee_id = targetLine.employee_id;
                this.props.line.employee_name = targetLine.employee_name;
                
                // Force component re-render
                this.render();
                
                // Also try to trigger order change if available
                if (typeof order.trigger === 'function') {
                    order.trigger('change', order);
                } else {
                    // Force update on the POS
                    order.trigger?.('change');
                }
            } catch (error) {}
            
        } catch (error) {
            this.notification.add(_t("Error selecting salesperson: %s", error.message), {
                type: 'danger',
                sticky: true,
            });
        }
    }
}