/** @odoo-module **/
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

export class SetProductListButton extends Component {
    setup() {
        super.setup();
        this.pos = usePos();
        const { popup } = this.env.services;
        this.popup = popup;
    }

    get productsList() {
        let list = [];
        list = this.pos.db.get_product_by_category(
            this.pos.selectedCategoryId
        );
        return list.sort(function(a, b) {
            return a.display_name.localeCompare(b.display_name);
        });
    }

    async onClick() {
        const salespersonList = this.pos.hr_employee.map((salesperson) => {
            return {
                id: salesperson.id,
                item: salesperson,
                label: salesperson.name,
                isSelected: false,
            };
        });

        const { confirmed, payload: selectedSalesperson } = await this.popup.add(SelectionPopup, {
            title: _t("Select the Salesperson"),
            list: salespersonList,
        });

        if (confirmed) {
            const order = this.pos.get_order();
            var name = null;
            var updated = false;
            if (!updated){
             name = document.getElementsByClassName("username")[0].innerHTML;
             updated = true;
            }
            order.salesperson_name = selectedSalesperson.name;
            order.salesperson_id = selectedSalesperson.id;
            if(!Array.isArray(order.cashier['name']))
            {
            order.cashier['name'] = ['Served by ' + order.cashier['name'] , 'Salesperson ' + selectedSalesperson.name];
            }
            else
            {
            order.cashier['name'][1] = 'Salesperson ' + selectedSalesperson.name;
            }
            document.getElementById("salesperson").innerHTML = 'Salesperson: ' + order.salesperson_name;
            document.getElementsByClassName("username")[0].innerHTML = name;
        }
    }
}

SetProductListButton.template = "SalesPersonButton";

ProductScreen.addControlButton({
    component: SetProductListButton,
    condition: function() {
        return true;
    },
});
