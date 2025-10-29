/** @odoo-module */
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
     setup(_defaultObj, options) {
           super.setup(...arguments);
           this.salesperson_id = this.salesperson_id || null;
       },
     init_from_JSON(json) {
      this.set_customer_suggestion(json.salesperson_id);
      super.init_from_JSON(...arguments);
   },
   export_as_JSON() {
       const json = super.export_as_JSON(...arguments);
       if (json) {
           json.salesperson_id = this.salesperson_id;
       }
       return json;
   },
    set_customer_suggestion(salesperson_id) {
       this.salesperson_id = salesperson_id;
   },
});
