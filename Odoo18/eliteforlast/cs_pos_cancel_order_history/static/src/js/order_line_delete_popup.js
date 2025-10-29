/** @odoo-module */
console.log("order_line_delete_popup.js loaded");

import { patch } from "@web/core/utils/patch";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Numpad } from "@point_of_sale/app/generic_components/numpad/numpad";
import { useService } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

console.log("Imports for order_line_delete_popup.js successful");

/* ----------------------------------------------------------------------
   1.  PATCH NUMPAD COMPONENT - Comprehensive Event Interception
---------------------------------------------------------------------- */
patch(Numpad.prototype, {
    setup() {
        super.setup();
        console.log("✅ Numpad setup called");
    },

    // Patch all potential methods that could handle numpad input
    async sendInput(buttonValue) {
        console.log("🔍 Numpad sendInput called with:", buttonValue);

        // Show popup but don't block normal behavior
        await this.handlePopupLogic(buttonValue, "sendInput");

        // Always continue with normal numpad behavior
        return super.sendInput(buttonValue);
    },

    // Additional method that might be called for button clicks
    async onClick(buttonValue) {
        console.log("🔍 Numpad onClick called with:", buttonValue);

        // Show popup but don't block normal behavior
        await this.handlePopupLogic(buttonValue, "onClick");

        // Always continue with normal numpad behavior
        return super.onClick ? super.onClick(buttonValue) : null;
    },

    // Another potential method for handling input
    async onInput(buttonValue) {
        console.log("🔍 Numpad onInput called with:", buttonValue);

        // Show popup but don't block normal behavior
        await this.handlePopupLogic(buttonValue, "onInput");

        // Always continue with normal numpad behavior
        return super.onInput ? super.onInput(buttonValue) : null;
    },

    // Handle button press events
    async onButtonPress(buttonValue) {
        console.log("🔍 Numpad onButtonPress called with:", buttonValue);

        // Show popup but don't block normal behavior
        await this.handlePopupLogic(buttonValue, "onButtonPress");

        // Always continue with normal numpad behavior
        return super.onButtonPress ? super.onButtonPress(buttonValue) : null;
    },

    // Central popup handling logic
    async handlePopupLogic(buttonValue, methodName) {
        console.log(`🔍 handlePopupLogic called from ${methodName} with:`, buttonValue);

        if (!this.shouldTriggerPopup(buttonValue)) {
            console.log("🔍 Popup not triggered for button:", buttonValue);
            return false;
        }

        const pos = this.env.services.pos;
        const currentOrder = pos?.get_order();
        const selectedOrderline = currentOrder?.get_selected_orderline();

        if (!selectedOrderline) {
            console.log("🔍 No selected order line, skipping popup");
            return false;
        }

        console.log("🔍 Showing popup for manual entry detection");

        try {
            const dialog = this.env.services.dialog;
            const cancelReasons = await this.getCancelReasonsFromNumpad(pos);

            const reasonList = cancelReasons.map((reason, index) => ({
                id: reason.id || index + 1,
                label: reason.name,
                item: reason.name,
                isSelected: false
            }));

            // Fixed: Remove invalid props for SelectionPopup in Odoo 18
            const result = await makeAwaitable(dialog, SelectionPopup, {
                title: "Manual Entry Detected - Select Reason",
                list: reasonList
            });

            console.log("🔍 Popup result received:", result);

            let selectedReason = "No reason selected";

            // SelectionPopup returns the selected reason directly as a string
            if (result && typeof result === 'string') {
                selectedReason = result;
                console.log("✅ Reason successfully captured:", selectedReason);
            } else if (result === null || result === undefined) {
                console.log("❌ User cancelled or no selection made");
            } else {
                console.log("❌ Unexpected result format:", result);
            }

            // Log order line data and save to database regardless of reason selection
            await this.logOrderLineData(selectedOrderline, selectedReason, pos, buttonValue, methodName);

            return false; // Never block the action - always allow normal behavior
        } catch (err) {
            console.error("Error in popup handling:", err);
            return false; // Allow action to continue on error
        }
    },

    async logOrderLineData(orderline, reason, pos, buttonValue, methodName) {
        const product = orderline.get_product();
        const currentOrder = pos.get_order();
        const cashier = pos.get_cashier();
        const partner = currentOrder.get_partner();
        const session = pos.session;

        // Only include fields that exist in the pos.order.cancel model
        let orderLineData = {
            product_id: product.id,
            qty: orderline.get_quantity() || 1,
            price_unit: orderline.get_unit_price() || 0,
            note: reason || 'No reason provided',
            user_id: cashier && cashier.user_id ? (Array.isArray(cashier.user_id) ? cashier.user_id[0] : cashier.user_id) : (pos.user ? pos.user.id : false),
            employee_id: cashier ? cashier.id : false,
            partner_id: partner ? partner.id : false,
            session_id: session ? session.id : false,
            company_id: pos.company ? pos.company.id : false
        };
        orderLineData = stripObjects(orderLineData);

        // Validate required fields
        if (!orderLineData.product_id) {
            console.error('❌ Product ID is required but missing');
            return;
        }

        console.log("✅ Order Line Data Logged:", orderLineData);
        console.log(`✅ Selected Reason: ${reason}`);

        try {
            // Access ORM through the environment services
            const orm = this.env.services?.orm || pos.orm;

            if (!orm) {
                console.error("❌ ORM service not available");
                return;
            }

            console.log("🔍 Attempting to save order line data:", orderLineData);
            console.log("🔍 ORM service available:", !!orm);

            // Save to database using ORM - Fixed method call
            const result = await orm.call(
                'pos.order.cancel',
                'create_new_order',
                [[orderLineData]]  // Backend expects array of orderLines
            );
            console.log("✅ Order line data saved to database:", result);
        } catch (error) {
            console.error("❌ ProductScreen error saving order line data to database:", error);
            console.error("❌ Error details:", {
                message: error.message,
                stack: error.stack,
                data: orderLineData
            });
        }
    },

    shouldTriggerPopup(buttonValue) {
        const shouldTrigger = "0123456789.,".includes(buttonValue) ||
                             buttonValue === 'Backspace' ||
                             buttonValue === 'Delete' ||
                             buttonValue === '+/-';
        console.log(`🔍 shouldTriggerPopup for "${buttonValue}":`, shouldTrigger);
        return shouldTrigger;
    },

    async getCancelReasonsFromNumpad(pos) {
        let cancelReasons = [];

        // Try to get cancel reasons from the loaded data using the correct Odoo 18 pattern
        if (pos.models && pos.models['pos.cancel.reason']) {
            cancelReasons = pos.models['pos.cancel.reason'].getAll();
        }

        // Alternative: try accessing via pos.data
        if (!cancelReasons.length && pos.data && pos.data['pos.cancel.reason']) {
            cancelReasons = pos.data['pos.cancel.reason'];
        }

        // Fallback to default reasons if none found
        if (!cancelReasons.length) {
            cancelReasons = [
                { id: 1, name: "Customer Changed Mind" },
                { id: 2, name: "Out of Stock" },
                { id: 3, name: "Wrong Item Added" },
                { id: 4, name: "Pricing Error" },
                { id: 5, name: "System Error" },
                { id: 6, name: "Other" },
            ];
        }

        return cancelReasons;
    },
});

// Utility to strip objects from payloads
function stripObjects(obj) {
    for (const key in obj) {
        if (typeof obj[key] === 'object' && obj[key] !== null) {
            if ('id' in obj[key]) {
                obj[key] = obj[key].id;
            } else {
                obj[key] = false;
            }
        }
    }
    return obj;
}

/* ----------------------------------------------------------------------
   2.  PATCH PRODUCT SCREEN - Additional Coverage
---------------------------------------------------------------------- */
patch(ProductScreen.prototype, {
    setup() {
        console.log("✅ ProductScreen setup called");
        super.setup();
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        console.log("✅ Dialog and ORM services loaded in ProductScreen");
        
        // Add keyboard event listener
        this.addKeyboardListener();
    },

    addKeyboardListener() {
        console.log("✅ Adding keyboard event listener");
        document.addEventListener('keydown', this.onKeyDown.bind(this));
    },

    async onKeyDown(event) {
        console.log("🔍 Key pressed:", event.key);
        
        // Check if backspace key is pressed
        if (event.key === 'Backspace') {
            console.log("🔍 Backspace key detected");
            
            // Check if an order line is selected
            const currentOrder = this.pos.get_order();
            const selectedOrderline = currentOrder?.get_selected_orderline();
            
            if (selectedOrderline) {
                console.log("✅ Both conditions met: Backspace + Selected order line");
                console.log("📋 Selected order line:", selectedOrderline.get_product().display_name);
                
                // Show cancel reason popup
                await this.showCancelReasonPopup(selectedOrderline);
            } else {
                console.log("❌ No order line selected");
            }
        }
    },

    async showCancelReasonPopup(orderline) {
        console.log("🔍 Showing cancel reason popup for backspace event");
        
        try {
            const cancelReasons = await this.getCancelReasons();

            const reasonList = cancelReasons.map((reason, index) => ({
                id: reason.id || index + 1,
                label: reason.name,
                item: reason.name,
                isSelected: false
            }));

            const result = await makeAwaitable(this.dialog, SelectionPopup, {
                title: "Backspace Key - Select Cancel Reason",
                list: reasonList
            });

            console.log("🔍 Backspace popup result:", result);

            let selectedReason = "No reason selected";

            if (result && typeof result === 'string') {
                selectedReason = result;
                console.log("✅ Backspace reason selected:", selectedReason);
            } else {
                console.log("❌ Backspace popup cancelled");
            }

            // Log the data
            await this.logOrderLineDataFromProductScreen(orderline, selectedReason, "Backspace", "keyboard");

        } catch (err) {
            console.error("Error showing backspace cancel popup:", err);
        }
    },

    // Patch potential numpad-related methods in ProductScreen
    async _onNumpadClick(buttonValue) {
        console.log("🔍 ProductScreen _onNumpadClick called with:", buttonValue);

        // Show popup but don't block normal behavior
        await this.handleProductScreenPopup(buttonValue, "_onNumpadClick");

        // Always continue with normal numpad behavior
        return super._onNumpadClick ? super._onNumpadClick(buttonValue) : null;
    },

    async onNumpadClick(buttonValue) {
        console.log("🔍 ProductScreen onNumpadClick called with:", buttonValue);

        // Show popup but don't block normal behavior
        await this.handleProductScreenPopup(buttonValue, "onNumpadClick");

        // Always continue with normal numpad behavior
        return super.onNumpadClick ? super.onNumpadClick(buttonValue) : null;
    },

    async handleProductScreenPopup(buttonValue, methodName) {
        console.log(`🔍 ProductScreen handleProductScreenPopup called from ${methodName} with:`, buttonValue);

        const currentOrder = this.pos.get_order();
        const selectedOrderline = currentOrder?.get_selected_orderline();

        if (!selectedOrderline || !this.shouldShowPopup(buttonValue)) {
            return false;
        }

        try {
            const cancelReasons = await this.getCancelReasons();

            const reasonList = cancelReasons.map((reason, index) => ({
                id: reason.id || index + 1,
                label: reason.name,
                item: reason.name,
                isSelected: false
            }));

            // Fixed: Remove invalid props for SelectionPopup in Odoo 18
            const result = await makeAwaitable(this.dialog, SelectionPopup, {
                title: "Manual Entry Detected - Select Reason",
                list: reasonList
            });

            console.log("🔍 ProductScreen popup result received:", result);

            let selectedReason = "No reason selected";

            // SelectionPopup returns the selected reason directly as a string
            if (result && typeof result === 'string') {
                selectedReason = result;
                console.log("✅ ProductScreen reason successfully captured:", selectedReason);
            } else if (result === null || result === undefined) {
                console.log("❌ ProductScreen user cancelled or no selection made");
            } else {
                console.log("❌ ProductScreen unexpected result format:", result);
            }

            // Log order line data and save to database regardless of reason selection
            await this.logOrderLineDataFromProductScreen(selectedOrderline, selectedReason, buttonValue, methodName);

            return false; // Never block the action - always allow normal behavior
        } catch (err) {
            console.error("Error showing manual-entry popup from ProductScreen:", err);
            return false;
        }
    },

    async logOrderLineDataFromProductScreen(orderline, reason, buttonValue, methodName) {
        const product = orderline.get_product();
        const currentOrder = this.pos.get_order();
        const cashier = this.pos.get_cashier();
        const partner = currentOrder.get_partner();
        const session = this.pos.session;
        //////////////////////////////////////////////////////////////
        let orderLineData = {
            product_id: product.id,
            qty: orderline.get_quantity() || 1,
            price_unit: orderline.get_unit_price() || 0,
            note: reason || 'No reason provided',
            user_id: cashier && cashier.user_id ? (Array.isArray(cashier.user_id) ? cashier.user_id[0] : cashier.user_id) : (this.pos.user ? this.pos.user.id : false),
            employee_id: cashier ? cashier.id : false,
            partner_id: partner ? partner.id : false,
            session_id: session ? session.id : false,
            pos_name: this.pos.config ? this.pos.config.name : false,
            company_id: this.pos.company ? this.pos.company.id : false
        };
        orderLineData = stripObjects(orderLineData);

        // Validate required fields
        if (!orderLineData.product_id) {
            console.error('❌ ProductScreen Product ID is required but missing');
            return;
        }

        console.log("✅ Order Line Data Logged from ProductScreen:", orderLineData);
        console.log(`✅ Selected Reason from ProductScreen: ${reason}`);

        try {
            console.log("🔍 ProductScreen attempting to save order line data:", orderLineData);
            console.log("🔍 ProductScreen ORM service available:", !!this.orm);

            // Use the ORM service that was properly initialized in setup()
            const result = await this.orm.call(
                'pos.order.cancel',
                'create_new_order',
                [[orderLineData]]  // Backend expects array of orderLines
            );
            console.log("✅ ProductScreen order line data saved to database:", result);
        } catch (error) {
            console.error("❌ ProductScreen error saving order line data to database:", error);
            console.error("❌ ProductScreen error details:", {
                message: error.message,
                stack: error.stack,
                data: orderLineData
            });
        }
    },

    shouldShowPopup(buttonValue) {
        return "0123456789.,".includes(buttonValue) ||
               buttonValue === 'Backspace' ||
               buttonValue === 'Delete' ||
               buttonValue === '+/-';
    },

    async getCancelReasons() {
        let cancelReasons = [];

        // Try to get cancel reasons from the loaded data using the correct Odoo 18 pattern
        if (this.pos.models && this.pos.models['pos.cancel.reason']) {
            cancelReasons = this.pos.models['pos.cancel.reason'].getAll();
        }

        // Alternative: try accessing via this.pos.data
        if (!cancelReasons.length && this.pos.data && this.pos.data['pos.cancel.reason']) {
            cancelReasons = this.pos.data['pos.cancel.reason'];
        }

        // Fallback to default reasons if none found
        if (!cancelReasons.length) {
            cancelReasons = [
                { id: 1, name: "Customer Changed Mind" },
                { id: 2, name: "Out of Stock" },
                { id: 3, name: "Wrong Item Added" },
                { id: 4, name: "Pricing Error" },
                { id: 5, name: "System Error" },
                { id: 6, name: "Other" },
            ];
        }

        return cancelReasons;
    },
});

console.log("✅ All patches applied successfully with comprehensive debugging");