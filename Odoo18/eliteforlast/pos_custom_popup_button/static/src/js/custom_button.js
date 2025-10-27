import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { useService } from "@web/core/utils/hooks";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ScrapPopup } from "./scrap_popup";

patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
    },

    async onClickPopupSingleField() {
        const result = await makeAwaitable(this.dialog, ScrapPopup, {
            title: "Scrap Product",
        });
        
        if (result) {
            // Handle the scrap result if needed
            console.log("Scrap created:", result);
        }
    }
});