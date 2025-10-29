/** @odoo-module */
console.log("🚀 POS Minimal Orders Override - v2.0");
import {patch} from "@web/core/utils/patch";
import {ControlButtons} from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import {useService} from "@web/core/utils/hooks";
import {SelectCreateDialog} from "@web/views/view_dialogs/select_create_dialog";


console.log("🚀 Multiple Imports Successful for pos_override");

patch(ControlButtons.prototype, {
    async onClickQuotation() {
        console.log("Custom onClickQuotation called!");

        try {
            // Get our custom view ID
            const views = await this.env.services.orm.searchRead(
                'ir.ui.view',
                [
                    ['model', '=', 'sale.order'],
                    ['type', '=', 'list'],
                    ['name', '=', 'sale.order.tree.minimal']
                ],
                ['id', 'name']
            );

            console.log("🔍 Found views:", views);

            if (views && views.length > 0) {
                const viewId = views[0].id;
                console.log("🎯 Found our minimal view ID:", viewId);

                // Method 1: Try with target="new" (popup)
                try {
                    await this.env.services.action.doAction({
                        name: "Sales Orders (Minimal)",
                        type: "ir.actions.act_window",
                        res_model: "sale.order",
                        view_mode: "list,form",
                        views: [
                            [viewId, "list"],
                            [false, "form"]
                        ],
                        target: "new", // This should open in popup/modal
                        context: {},
                        domain: []
                    });
                    console.log("✅ Popup method 1 worked!");
                    return;
                } catch (error) {
                    console.error("❌ Popup method 1 failed:", error);
                }

                // Method 2: Use dialog service directly
                try {
                    this.env.services.dialog.add(SelectCreateDialog, {
                        title: "Sales Orders (Minimal)",
                        resModel: "sale.order",
                        context: {},
                        domain: [],
                        multiSelect: false,
                        noCreate: true,
                        onSelected: (records) => {
                            console.log("Selected records:", records);
                        },
                        onClose: () => {
                            console.log("Dialog closed");
                        }
                    });
                    console.log("✅ Dialog service method worked!");
                    return;
                } catch (error) {
                    console.error("❌ Dialog service method failed:", error);
                }

                // Method 3: Try the action with different target
                try {
                    await this.env.services.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: "sale.order",
                        view_mode: "list",
                        view_id: viewId,
                        target: "dialog", // Alternative popup target
                        context: {}
                    });
                    console.log("✅ Dialog target method worked!");
                    return;
                } catch (error) {
                    console.error("❌ Dialog target method failed:", error);
                }
            }
        } catch (error) {
            console.error("❌ Failed to find view:", error);
        }

        // Final fallback: Use the original Odoo behavior but with your XML action
        try {
            console.log("🔄 Using XML action fallback...");
            await this.env.services.action.doAction({
                name: "cs_hide_pos_fields.action_sale_order_tree_minimal",
                target: "new" // Try popup with XML action
            });
        } catch (error) {
            console.error("❌ All methods failed:", error);
        }
    },
});