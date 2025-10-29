/** @odoo-module **/

import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SalespersonButton } from "./SalespersonButton";
import { patch } from "@web/core/utils/patch";

console.log("=== POS SALESPERSON DEBUG: control_buttons.js loaded ===");

// Patch ControlButtons to add SalespersonButton
patch(ControlButtons.prototype, {
    setup() {
        console.log("=== POS SALESPERSON DEBUG: Enhanced ControlButtons setup initiated");
        super.setup();
        console.log("=== POS SALESPERSON DEBUG: Enhanced setup completed successfully");
    }
});

// Add SalespersonButton to the components
console.log("=== POS SALESPERSON DEBUG: Adding SalespersonButton to ControlButtons components");

ControlButtons.components = {
    ...ControlButtons.components,
    SalespersonButton,
};

console.log("=== POS SALESPERSON DEBUG: Updated components list:", {
    totalComponents: Object.keys(ControlButtons.components).length,
    components: Object.keys(ControlButtons.components),
    hasSalespersonButton: 'SalespersonButton' in ControlButtons.components
});

console.log("=== POS SALESPERSON DEBUG: ControlButtons patched successfully ===");