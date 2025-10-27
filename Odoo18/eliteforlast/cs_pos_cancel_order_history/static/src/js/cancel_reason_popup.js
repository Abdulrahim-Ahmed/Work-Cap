/** @odoo-module */

import { Component, xml } from "@odoo/owl";

export class CancelReasonPopup extends Component {
    static template = "cs_pos_cancel_order_history.cancel_reason_popup";

    static props = {
        title: { type: String },
        reasons: { type: Array, optional: true },
        getPayload: { type: Function },
        close: { type: Function },
    };

    setup() {
        console.log("CancelReasonPopup setup - props:", this.props);
    }

    getSelectedReason() {
        const selectedRadio = this.el.querySelector('input[name="reason"]:checked');
        return selectedRadio ? selectedRadio.value : null;
    }

    onConfirm() {
        const selectedReason = this.getSelectedReason();
        console.log("Selected reason:", selectedReason);
        
        if (selectedReason) {
            // Call the getPayload function and pass the result to close
            const payload = { reason: selectedReason };
            this.props.close(payload);
        } else {
            // Show warning or handle no selection case
            console.warn("No reason selected");
            // Could add visual feedback here
        }
    }

    onCancel() {
        console.log("Cancel clicked");
        this.props.close(null);
    }
}
