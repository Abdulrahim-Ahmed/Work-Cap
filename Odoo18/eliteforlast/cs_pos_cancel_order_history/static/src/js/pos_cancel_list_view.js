/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class PosOrderCancelListController extends ListController {
    setup() {
        super.setup();
        this.companyService = useService("company");
    }

    async onWillStart() {
        await super.onWillStart();
        this.updateDomainWithCompany();
    }

    async onWillUpdateProps(nextProps) {
        await super.onWillUpdateProps(nextProps);
        this.updateDomainWithCompany();
    }

    updateDomainWithCompany() {
        // Get allowed company IDs from session context
        const allowedCompanyIds = session.user_context.allowed_company_ids || 
                                 this.env.context.allowed_company_ids ||
                                 [this.companyService.currentCompany];
        
        // Update the domain to filter by allowed companies
        if (allowedCompanyIds && allowedCompanyIds.length > 0) {
            const companyDomain = [["company_id", "in", allowedCompanyIds]];
            
            // Get existing domain or empty array
            const existingDomain = this.props.domain || [];
            
            // Remove any existing company_id domain
            const filteredDomain = existingDomain.filter(
                item => !(Array.isArray(item) && item[0] === "company_id")
            );
            
            // Combine domains - company filter first
            this.props.domain = [...companyDomain, ...filteredDomain];
        }
    }

    async willStart() {
        await super.willStart();
        // Listen for company changes
        this.companyService.addEventListener("company-changed", () => {
            this.updateDomainWithCompany();
            this.reload();
        });
    }
}

export const PosOrderCancelListView = {
    ...listView,
    Controller: PosOrderCancelListController,
};

// Register the custom view for pos.order.cancel model
registry.category("views").add("pos_order_cancel_list", PosOrderCancelListView);
