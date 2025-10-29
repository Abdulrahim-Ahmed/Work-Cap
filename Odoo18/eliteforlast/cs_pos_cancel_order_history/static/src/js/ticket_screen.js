/** @odoo-module */
console.log("ticket_screen.js loaded")
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { CancelReasonPopup } from "@cs_pos_cancel_order_history/js/cancel_reason_popup";
import { patch } from "@web/core/utils/patch";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

console.log("Multiple Imports Successful");

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

patch(PosStore.prototype, {

    async onDeleteOrder(order) {
        console.log("✅ You clicked cancel order");
        console.log("🔍 Order to be cancelled:", order);

        // Get cancel reasons from the loaded data using the correct Odoo 18 pattern
        let cancelReasons = [];

        // In Odoo 18, loaded models are accessible via this.models
        if (this.models && this.models['pos.cancel.reason']) {
            cancelReasons = this.models['pos.cancel.reason'].getAll();
            console.log("Found cancel reasons via models:", cancelReasons);
        }

        // Alternative: try accessing via this.data
        if (!cancelReasons.length && this.data && this.data['pos.cancel.reason']) {
            cancelReasons = this.data['pos.cancel.reason'];
            console.log("Found cancel reasons via data:", cancelReasons);
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
            console.log("Using fallback cancel reasons:", cancelReasons);
        }

        console.log("Final cancel reasons:", cancelReasons);

        // Transform the reasons into the format expected by SelectionPopup
        const reasonList = cancelReasons.map((reason, index) => ({
            id: reason.id || index + 1,
            label: reason.name,
            item: reason.name,
            isSelected: false
        }));

        console.log("Transformed reason list:", reasonList);

        try {
            // Fixed: Remove invalid props for SelectionPopup in Odoo 18
            const selectedReason = await makeAwaitable(this.dialog, SelectionPopup, {
                title: "Select Cancel Reason for Complete Order",
                list: reasonList
            });

            console.log("Selected reason:", selectedReason);

            let reason = "No reason selected";
            if (selectedReason && typeof selectedReason === 'string') {
                reason = selectedReason;
                console.log("✅ Order cancellation reason successfully captured:", reason);
            } else if (selectedReason === null || selectedReason === undefined) {
                console.log("❌ User cancelled reason selection");
                // User cancelled the reason selection, don't proceed with order cancellation
                return;
            }

            // Log all order lines from the cancelled order to database
            await this.logCancelledOrderData(order, reason);

            // Proceed with the actual order cancellation
            return super.onDeleteOrder(order);

        } catch (error) {
            console.error("❌ Error in order cancellation process:", error);
            // Still proceed with cancellation even if logging fails
            return super.onDeleteOrder(order);
        }
    },

    async logCancelledOrderData(order, reason) {
        console.log("🔍 Starting to log cancelled order data");
        console.log("🔍 Order:", order);
        console.log("🔍 Reason:", reason);

        if (!order) {
            console.error("❌ No order provided for logging");
            return;
        }

        const orderLines = order.get_orderlines();
        console.log("🔍 Order lines count:", orderLines.length);

        if (!orderLines || orderLines.length === 0) {
            console.log("ℹ️ No order lines to log for cancelled order");
            return;
        }

        // Get current session and user info
        const cashier = this.get_cashier();
        const partner = order.get_partner();
        const session = this.session;

        console.log("🔍 Session info:", {
            cashier: cashier ? cashier.name : 'No cashier',
            partner: partner ? partner.name : 'No partner',
            session_id: session ? session.id : 'No session'
        });

        // Convert all order lines to the format expected by pos.order.cancel model
        const orderLinesData = [];

        for (const orderLine of orderLines) {
            const product = orderLine.get_product();

            if (!product || !product.id) {
                console.warn("⚠️ Skipping order line with missing product:", orderLine);
                continue;
            }

            let orderLineData = {
                product_id: product.id,
                qty: orderLine.get_quantity() || 0,
                price_unit: orderLine.get_unit_price() || 0,
                note: `Complete Order Cancelled - ${reason}`,
                user_id: cashier && cashier.user_id ? (Array.isArray(cashier.user_id) ? cashier.user_id[0] : cashier.user_id) : (this.user ? this.user.id : false),
                employee_id: cashier ? cashier.id : false,
                partner_id: partner ? partner.id : false,
                session_id: session ? session.id : false,
                pos_name: this.config ? this.config.name : false,
                company_id: this.company ? this.company.id : false
            };
            orderLineData = stripObjects(orderLineData);

            orderLinesData.push(orderLineData);
            console.log("✅ Order Line Data prepared:", orderLineData);
        }

        console.log("🔍 Total order lines data to save:", orderLinesData.length);

        if (orderLinesData.length === 0) {
            console.log("ℹ️ No valid order lines data to save");
            return;
        }

        try {
            // Get ORM service from environment services
            const orm = this.env.services?.orm;

            if (!orm) {
                console.error("❌ ORM service not available for saving cancelled order data");
                return;
            }

            console.log("🔍 Attempting to save cancelled order data to database");
            console.log("🔍 ORM service available:", !!orm);
            console.log("🔍 Data to save:", orderLinesData);

            // Save to database using the same method as order line deletion
            const result = await orm.call(
                'pos.order.cancel',
                'create_new_order',
                [orderLinesData]  // Backend expects array of orderLines
            );

            console.log("✅ Cancelled order data saved to database successfully:", result);

        } catch (error) {
            console.error("❌ Error saving cancelled order data to database:", error);
            console.error("❌ Error details:", {
                message: error.message,
                stack: error.stack,
                orderLinesData: orderLinesData
            });
        }
    },
});