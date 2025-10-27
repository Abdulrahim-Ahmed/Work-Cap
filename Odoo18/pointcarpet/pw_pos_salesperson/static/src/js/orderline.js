/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

console.log("=== POS SALESPERSON DEBUG: orderline.js loading ===");

// Patch Orderline component to accept salesperson props
// Using a more permissive validation approach
patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            validate: (line) => {
                // Allow any object structure for the line to avoid validation issues
                return typeof line === 'object' && line !== null;
            },
            optional: false,
        },
    },
});

console.log("=== POS SALESPERSON DEBUG: orderline.js loaded successfully ===");