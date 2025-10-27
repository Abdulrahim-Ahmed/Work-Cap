/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { OrderlineSalespersonIcon } from "./OrderlineSalespersonIcon";
import { patch } from "@web/core/utils/patch";

// Patch the Orderline component to include our OrderlineSalespersonIcon component
patch(Orderline, {
    components: {
        ...Orderline.components,
        OrderlineSalespersonIcon,
    },
});