import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";

export class ScrapPopup extends Component {
    static template = "pos_custom_popup_button.ScrapPopup";
    static components = { Dialog };
    static props = {
        title: { type: String, optional: true },
        getPayload: Function,
        close: Function,
    };

    setup() {
        this.state = useState({
            products: [], // Array to store multiple products with quantities
            location_id: "",
            scrap_location_id: "",
            reason: "",
            is_loading: false,
            selected_product_id: "", // For adding new products
        });
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.pos = usePos();
        
        this.loadLocations();
        this.loadProducts();
    }

    async loadProducts() {
        try {
            this.products = await this.orm.searchRead(
                "product.product",
                [["type", "in", ["product", "consu"]]],
                ["id", "name", "default_code"]
            );
        } catch (error) {
            console.error("Failed to load products:", error);
            this.products = [];
        }
    }

    async loadLocations() {
        try {
            // Load internal locations for source
            const locations = await this.orm.searchRead(
                "stock.location",
                [["usage", "in", ["internal", "inventory"]]],
                ["id", "complete_name", "usage"]
            );
            this.locations = locations;
            console.log("Loaded locations:", locations);
            
            // Set default location if available
            if (locations.length > 0) {
                this.state.location_id = locations[0].id;
            }

            // Get scrap location - try different approaches
            let scrapLocations = await this.orm.searchRead(
                "stock.location",
                [["scrap_location", "=", true]],
                ["id", "complete_name"]
            );
            
            // If no dedicated scrap location, try to find by usage
            if (scrapLocations.length === 0) {
                scrapLocations = await this.orm.searchRead(
                    "stock.location",
                    [["usage", "=", "inventory"]],
                    ["id", "complete_name"]
                );
            }
            
            // If still no scrap location, create a fallback with first location
            if (scrapLocations.length === 0) {
                scrapLocations = locations.slice(0, 1); // Use first location as fallback
            }
            
            this.scrapLocations = scrapLocations;
            console.log("Loaded scrap locations:", scrapLocations);
            
            if (scrapLocations.length > 0) {
                this.state.scrap_location_id = scrapLocations[0].id;
            }
        } catch (error) {
            console.error("Failed to load locations:", error);
            this.locations = [];
            this.scrapLocations = [];
        }
    }

    addProduct() {
        if (!this.state.selected_product_id) {
            this.notification.add(_t("Please select a product"), { type: "warning" });
            return;
        }

        // Check if product already exists
        const existingProduct = this.state.products.find(p => p.product_id == this.state.selected_product_id);
        if (existingProduct) {
            this.notification.add(_t("Product already added"), { type: "warning" });
            return;
        }

        const selectedProduct = this.products.find(p => p.id == this.state.selected_product_id);
        if (selectedProduct) {
            this.state.products.push({
                product_id: selectedProduct.id,
                product_name: selectedProduct.name,
                product_code: selectedProduct.default_code,
                scrap_qty: 1.0,
            });
            this.state.selected_product_id = ""; // Reset selection
        }
    }

    removeProduct(index) {
        this.state.products.splice(index, 1);
    }

    updateProductQuantity(index, quantity) {
        const numQty = parseFloat(quantity);
        if (!isNaN(numQty) && numQty > 0) {
            this.state.products[index].scrap_qty = numQty;
        } else if (quantity === '' || quantity === null || quantity === undefined) {
            // Allow empty value for user convenience while typing
            this.state.products[index].scrap_qty = '';
        } else {
            // Revert to previous valid value if invalid input
            this.notification.add(_t("Please enter a valid positive quantity"), { type: "warning" });
        }
    }

    validateProductQuantities() {
        const invalidProducts = [];
        this.state.products.forEach((product, index) => {
            if (!product.scrap_qty || product.scrap_qty <= 0) {
                invalidProducts.push(product.product_name);
            }
        });
        return invalidProducts;
    }

    addAllAvailableProducts() {
        if (this.availableProducts.length === 0) {
            this.notification.add(_t("No more products available to add"), { type: "info" });
            return;
        }

        this.availableProducts.forEach(product => {
            this.state.products.push({
                product_id: product.id,
                product_name: product.name,
                product_code: product.default_code,
                scrap_qty: 1.0,
            });
        });

        this.notification.add(_t(`Added ${this.availableProducts.length} products`), { type: "success" });
    }

    clearAllProducts() {
        this.state.products.splice(0, this.state.products.length);
        this.notification.add(_t("All products removed"), { type: "info" });
    }

    async confirm() {
        if (!this.state.products || this.state.products.length === 0) {
            this.notification.add(_t("Please add at least one product"), { type: "danger" });
            return;
        }

        // Validate each product
        const invalidProducts = this.validateProductQuantities();
        if (invalidProducts.length > 0) {
            const productList = invalidProducts.join(', ');
            this.notification.add(_t(`Please enter valid quantities for: ${productList}`), { type: "danger" });
            return;
        }

        if (!this.state.location_id) {
            this.notification.add(_t("Please select a source location"), { type: "danger" });
            return;
        }

        if (!this.state.scrap_location_id) {
            this.notification.add(_t("Please select a scrap location"), { type: "danger" });
            return;
        }

        this.state.is_loading = true;

        try {
            // Get analytic account from POS session/config
            const analyticAccountId = this.pos.config.analytic_account_id || 
                                    (this.pos.pos_session && this.pos.pos_session.pos_analytic_account_id);

            const createdScraps = [];
            const errors = [];

            // Create scrap records for each product
            for (const product of this.state.products) {
                try {
                    const scrapData = {
                        product_id: parseInt(product.product_id),
                        scrap_qty: parseFloat(product.scrap_qty),
                        location_id: parseInt(this.state.location_id),
                        scrap_location_id: parseInt(this.state.scrap_location_id),
                        name: this.state.reason || _t(`POS Scrap - ${product.product_name}`),
                        date_done: new Date().toISOString().split('T')[0], // Current date
                    };

                    // Add analytic account if available
                    if (analyticAccountId) {
                        scrapData.analytic_account_id = parseInt(analyticAccountId);
                    }

                    console.log("Creating scrap with data:", scrapData);

                    const scrapId = await this.orm.create("stock.scrap", [scrapData]);
                    console.log("Scrap created with ID:", scrapId);
                    
                    createdScraps.push({
                        scrap_id: scrapId,
                        product_id: product.product_id,
                        product_name: product.product_name,
                        scrap_qty: product.scrap_qty,
                    });
                } catch (error) {
                    console.error(`Failed to create scrap for ${product.product_name}:`, error);
                    errors.push(`${product.product_name}: ${error.message || error}`);
                }
            }

            // Show results
            if (createdScraps.length > 0) {
                const successMsg = createdScraps.length === 1 
                    ? _t("Scrap record created successfully. Please validate it from the Inventory app.")
                    : _t(`${createdScraps.length} scrap records created successfully. Please validate them from the Inventory app.`);
                this.notification.add(successMsg, { type: "success" });
            }

            if (errors.length > 0) {
                const errorMsg = _t("Some scraps failed to create: ") + errors.join(", ");
                this.notification.add(errorMsg, { type: "warning" });
            }

            if (createdScraps.length > 0) {
                this.props.getPayload({
                    scraps: createdScraps,
                    total_products: createdScraps.length,
                });
                
                // Automatically close the wizard after successful scrap creation
                this.props.close();
            }
            
        } catch (error) {
            console.error("Failed to create scraps:", error);
            let errorMsg = _t("Failed to create scraps");
            
            if (error.data && error.data.message) {
                errorMsg += ": " + error.data.message;
            } else if (error.message) {
                errorMsg += ": " + error.message;
            } else if (typeof error === 'string') {
                errorMsg += ": " + error;
            }
            
            this.notification.add(errorMsg, { type: "danger" });
        } finally {
            this.state.is_loading = false;
        }
    }

    close() {
        this.props.close();
    }

    get availableProducts() {
        if (!this.products) return [];
        // Filter out already added products
        const addedProductIds = this.state.products.map(p => p.product_id);
        return this.products.filter(p => !addedProductIds.includes(p.id));
    }

    getAnalyticAccount() {
        // Try to get from config first, then from session
        const analyticAccountId = this.pos.config.analytic_account_id || 
                                (this.pos.pos_session && this.pos.pos_session.pos_analytic_account_id);
        
        if (analyticAccountId) {
            // Try to find the analytic account in loaded data
            if (this.pos.models && this.pos.models['account.analytic.account']) {
                return this.pos.models['account.analytic.account'].find(acc => acc.id === analyticAccountId);
            }
            // If not in loaded data, return basic info
            return { id: analyticAccountId, name: `Analytic Account (ID: ${analyticAccountId})` };
        }
        return null;
    }
}