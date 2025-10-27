/** @odoo-module **/

console.log('=== POS SALESPERSON DEBUG: SalespersonVisualManager.js loaded ===');

/**
 * Centralized visual manager for salesperson display in orderlines
 * Handles both general and individual salesperson assignments
 */
export class SalespersonVisualManager {
    
    static updateOrderlineDisplay(orderLine, employeeName, isIndividual = false) {
        console.log("=== VISUAL MANAGER DEBUG: Updating orderline display for:", employeeName, "Individual:", isIndividual);
        console.log("=== VISUAL MANAGER DEBUG: OrderLine:", orderLine);
        
        try {
            // Find all orderline elements
            const orderlines = document.querySelectorAll('.orderline');
            console.log("=== VISUAL MANAGER DEBUG: Found", orderlines.length, "orderlines to check");
            
            // For individual assignments, try to find by stable data attributes first
            if (isIndividual && orderLine) {
                try {
                    const candidateSelectors = [];
                    const lineCid = orderLine.cid || orderLine._cid || null;
                    const lineId = orderLine.id || null;
                    const productId = orderLine.product?.id || orderLine.product_id || null;
                    if (lineCid) candidateSelectors.push(`.orderline[data-line-cid="${lineCid}"]`);
                    if (lineId) candidateSelectors.push(`.orderline[data-line-id="${lineId}"]`);
                    if (productId) candidateSelectors.push(`.orderline[data-product-id="${productId}"]`);
                    for (const sel of candidateSelectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            console.log("=== VISUAL MANAGER DEBUG: Found orderline via selector:", sel);
                            this.updateIndividualOrderlineDOM(el, employeeName);
                            return;
                        }
                    }
                } catch (e) {
                    console.log("=== VISUAL MANAGER DEBUG: Selector-based lookup failed:", e);
                }
                // Try different ways to get the POS order in Odoo 18
                let posOrder = null;
                let allOrderlines = [];
                
                // Method 1: orderLine.order (traditional)
                if (orderLine.order) {
                    posOrder = orderLine.order;
                    allOrderlines = posOrder.get_orderlines();
                }
                // Method 2: orderLine.models['pos.order'] (possible in Odoo 18)
                else if (orderLine.models && orderLine.models['pos.order']) {
                    const orderModel = orderLine.models['pos.order'];
                    if (orderModel.records && orderModel.records.size > 0) {
                        // Find the current order - assume it's the last one or find by matching lines
                        posOrder = Array.from(orderModel.records.values()).find(order => 
                            order.lines && order.lines.some(line => line === orderLine)
                        );
                        if (posOrder) {
                            allOrderlines = posOrder.get_orderlines();
                        }
                    }
                }
                // Method 3: Global search for orders containing this line
                else {
                    // Try to find the order by searching through DOM - less reliable but fallback
                    console.log("=== VISUAL MANAGER DEBUG: Trying global DOM search for orderline");
                    const currentOrderlines = Array.from(document.querySelectorAll('.orderline'));
                    const targetIndex = currentOrderlines.findIndex(el => {
                        // Try to match by product or unique characteristics
                        const productNameEl = el.querySelector('.product-name');
                        const priceEl = el.querySelector('.price');
                        if (productNameEl && priceEl && orderLine.product_id && orderLine.price) {
                            return productNameEl.textContent.includes(orderLine.product_id.display_name) &&
                                   priceEl.textContent.includes(orderLine.price.toString());
                        }
                        return false;
                    });
                    
                    if (targetIndex >= 0) {
                        console.log("=== VISUAL MANAGER DEBUG: Found orderline by DOM search at index:", targetIndex);
                        const targetOrderlineEl = currentOrderlines[targetIndex];
                        this.updateIndividualOrderlineDOM(targetOrderlineEl, employeeName);
                        return;
                    }
                }
                
                if (posOrder && allOrderlines.length > 0) {
                    const lineIndex = allOrderlines.findIndex(line => line === orderLine);
                    
                    console.log("=== VISUAL MANAGER DEBUG: Found orderLine at index:", lineIndex, "out of", allOrderlines.length);
                    
                    if (lineIndex >= 0 && lineIndex < orderlines.length) {
                        const targetOrderlineEl = orderlines[lineIndex];
                        
                        console.log("=== VISUAL MANAGER DEBUG: Updating orderline at DOM index:", lineIndex);
                        
                        this.updateIndividualOrderlineDOM(targetOrderlineEl, employeeName);
                        return; // Exit early for individual assignments
                    } else {
                        console.log("=== VISUAL MANAGER DEBUG: Invalid line index:", lineIndex);
                    }
                } else {
                    console.log("=== VISUAL MANAGER DEBUG: No POS order found for orderLine, trying fallback");
                }
                
                console.log("=== VISUAL MANAGER DEBUG: Individual assignment completed");
                return;
            }
            
            // For general assignments, update all orderlines that don't have individual assignments
            let matchFound = false;
            orderlines.forEach((orderlineEl, index) => {
                console.log("=== VISUAL MANAGER DEBUG: Checking orderline", index, "for general assignment");
                
                // Detect existing badges
                const existingDynamic = orderlineEl.querySelector('.salesperson-display');
                const templateBadgeSpan = orderlineEl.querySelector('.salesperson-item span');

                // If dynamic badge is marked as individual, skip updating this line with general
                if (!isIndividual && existingDynamic?.dataset.isIndividual === 'true') {
                    console.log("=== VISUAL MANAGER DEBUG: Skipping orderline", index, "- has individual assignment");
                    return;
                }

                // Remove previous dynamic general badge to avoid duplicates
                if (existingDynamic) {
                    existingDynamic.remove();
                    console.log("=== VISUAL MANAGER DEBUG: Removed existing dynamic display from orderline", index);
                }
                
                // Add new salesperson display if employee name provided
                if (employeeName) {
                    const infoList = orderlineEl.querySelector('.info-list');
                    if (infoList) {
                        // Prefer updating the template-based badge if present
                        if (templateBadgeSpan) {
                            templateBadgeSpan.textContent = employeeName;
                            console.log("=== VISUAL MANAGER DEBUG: Updated template-based salesperson item in orderline", index);
                        } else {
                            // Otherwise add our dynamic badge
                            const salespersonLi = document.createElement('li');
                            salespersonLi.className = 'salesperson-display';
                            salespersonLi.style.cssText = 'color: #ff8800; font-size: 0.85em; font-weight: bold; background: rgba(255, 136, 0, 0.1); padding: 2px 6px; border-radius: 3px; margin-top: 2px; display: inline-block;';
                            salespersonLi.innerHTML = `<i class=\"fa fa-user me-1\" style=\"font-size: 0.8em;\"></i>${employeeName}`;
                            salespersonLi.dataset.isIndividual = isIndividual ? 'true' : 'false';
                            infoList.appendChild(salespersonLi);
                            console.log("=== VISUAL MANAGER DEBUG: Added salesperson dynamic display to orderline", index);
                        }
                    } else {
                        console.log("=== VISUAL MANAGER DEBUG: No info-list found in orderline", index);
                    }
                }
            });
            
            if (isIndividual && !matchFound) {
                console.log("=== VISUAL MANAGER DEBUG: No matching orderline found for individual assignment");
            }
            
        } catch (error) {
            console.error("=== VISUAL MANAGER DEBUG: Error updating display:", error);
        }
    }
    
    static updateAllOrderlinesDisplay(employeeName) {
        console.log("=== VISUAL MANAGER DEBUG: Updating ALL orderlines with general salesperson:", employeeName);
        
        // Use the unified system for general assignment
        this.updateOrderlineDisplay(null, employeeName, false);
    }
    
    static updateIndividualOrderlineDisplay(orderLine, employeeName) {
        console.log("=== VISUAL MANAGER DEBUG: Updating INDIVIDUAL orderline with salesperson:", employeeName);
        
        // Use the unified system for individual assignment
        this.updateOrderlineDisplay(orderLine, employeeName, true);
    }

    /**
     * Update a specific orderline display by starting from a child element (e.g., the clicked icon).
     * This is resilient to template structure differences because it climbs up the DOM tree
     * until it finds a container that contains an `.info-list`.
     */
    static updateFromChildElement(childEl, employeeName) {
        try {
            if (!childEl) {
                console.log("=== VISUAL MANAGER DEBUG: No child element provided for updateFromChildElement");
                return;
            }
            let el = childEl;
            let container = null;
            for (let i = 0; i < 10 && el; i += 1) {
                if (el.classList?.contains('orderline')) {
                    container = el;
                    break;
                }
                // If this element has an info-list in its subtree, consider it the container
                if (el.querySelector && el.querySelector('.info-list')) {
                    container = el;
                    break;
                }
                el = el.parentElement;
            }
            if (container) {
                console.log("=== VISUAL MANAGER DEBUG: Found container via child traversal");
                this.updateIndividualOrderlineDOM(container, employeeName);
            } else {
                console.log("=== VISUAL MANAGER DEBUG: Could not find container via child traversal; skipping DOM update");
            }
        } catch (error) {
            console.error("=== VISUAL MANAGER DEBUG: Error in updateFromChildElement:", error);
        }
    }
    
    static updateIndividualOrderlineDOM(orderlineEl, employeeName) {
        console.log("=== VISUAL MANAGER DEBUG: Updating individual orderline DOM with employee:", employeeName);
        
        // Remove/refresh any existing salesperson indicators
        // 1) Our dynamic badge
        const existingDynamicBadge = orderlineEl.querySelector('.salesperson-display');
        if (existingDynamicBadge) {
            existingDynamicBadge.remove();
            console.log("=== VISUAL MANAGER DEBUG: Removed existing dynamic display from target orderline");
        }
        // 2) Template-based badge rendered by OWL (uses line.employee_name)
        const templateBadge = orderlineEl.querySelector('.salesperson-item');
        const templateBadgeText = templateBadge?.querySelector('span');
        
        if (employeeName) {
            // Add new salesperson display
            const infoList = orderlineEl.querySelector('.info-list');
            if (infoList) {
                // If template badge exists, update it directly for immediate visual feedback
                if (templateBadgeText) {
                    templateBadgeText.textContent = employeeName;
                    console.log("=== VISUAL MANAGER DEBUG: Updated template-based salesperson item text");
                } else {
                    // Otherwise, add our dynamic badge
                    const salespersonLi = document.createElement('li');
                    salespersonLi.className = 'salesperson-display';
                    salespersonLi.style.cssText = 'color: #ff8800; font-size: 0.85em; font-weight: bold; background: rgba(255, 136, 0, 0.1); padding: 2px 6px; border-radius: 3px; margin-top: 2px; display: inline-block;';
                    salespersonLi.innerHTML = `<i class="fa fa-user me-1" style="font-size: 0.8em;"></i>${employeeName}`;
                    salespersonLi.dataset.isIndividual = 'true';
                    infoList.appendChild(salespersonLi);
                    console.log("=== VISUAL MANAGER DEBUG: Added individual salesperson dynamic display to target orderline");
                }
            } else {
                console.log("=== VISUAL MANAGER DEBUG: No info-list found in target orderline");
            }
        } else {
            // Clearing assignment: also clear template-based text if present
            if (templateBadge) {
                templateBadge.remove();
                console.log("=== VISUAL MANAGER DEBUG: Removed template-based salesperson item from target orderline");
            }
            console.log("=== VISUAL MANAGER DEBUG: Removed salesperson from target orderline");
        }
    }
    
    static clearAllSalespersonDisplays() {
        console.log("=== VISUAL MANAGER DEBUG: Clearing all salesperson displays");
        
        try {
            const existingDisplays = document.querySelectorAll('.salesperson-display');
            existingDisplays.forEach(display => display.remove());
        } catch (error) {
            console.error("=== VISUAL MANAGER DEBUG: Error clearing displays:", error);
        }
    }
}

// Export globally for compatibility with existing code
window.SalespersonVisualManager = SalespersonVisualManager;
window.updateAllOrderlinesWithSalesperson = (employeeName) => {
    SalespersonVisualManager.updateAllOrderlinesDisplay(employeeName);
};
window.updateOrderlinesWithGeneralSalesperson = (employeeName) => {
    SalespersonVisualManager.updateAllOrderlinesDisplay(employeeName);
};

console.log('=== POS SALESPERSON DEBUG: SalespersonVisualManager initialized ===');