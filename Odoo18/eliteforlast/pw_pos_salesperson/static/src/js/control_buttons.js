/** @odoo-module **/

import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SalespersonButton } from "./SalespersonButton";
import { patch } from "@web/core/utils/patch";

// Ensure ControlButtons has access to SalespersonButton component
patch(ControlButtons.prototype, {
    setup() {
        super.setup();
    }
});

ControlButtons.components = {
    ...ControlButtons.components,
    SalespersonButton,
};
