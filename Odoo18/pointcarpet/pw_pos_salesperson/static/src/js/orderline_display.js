/** @odoo-module **/

console.log("=== POS SALESPERSON DEBUG: orderline_display.js loaded ===");

// Create a simple utility to add salesperson display to order lines
function addSalespersonDisplayToOrderLines() {
    console.log("=== POS SALESPERSON DEBUG: Looking for orderlines to update...");
    
    const orderlines = document.querySelectorAll('.orderline');
    console.log("=== POS SALESPERSON DEBUG: Found", orderlines.length, "orderlines");
    
    orderlines.forEach((orderlineEl, index) => {
        // Check if we already added salesperson display
        if (orderlineEl.querySelector('.salesperson-display')) {
            return;
        }
        
        // Try to find a way to get the line data
        // In Odoo 18, we'll add the display programmatically when the employee is assigned
        console.log("=== POS SALESPERSON DEBUG: Checking orderline", index, "for salesperson data");
    });
}

// Global function that can be called to add salesperson display to all orderlines
window.addSalespersonToOrderLineDisplay = function(orderLine, employeeName) {
    console.log("=== POS SALESPERSON DEBUG: addSalespersonToOrderLineDisplay called for:", employeeName);
    
    // Find all orderline elements and add salesperson info
    setTimeout(() => {
        const orderlines = document.querySelectorAll('.orderline');
        console.log("=== POS SALESPERSON DEBUG: Found", orderlines.length, "orderlines to update");
        
        orderlines.forEach((orderlineEl) => {
            // Remove existing salesperson display
            const existingSalesperson = orderlineEl.querySelector('.salesperson-display');
            if (existingSalesperson) {
                existingSalesperson.remove();
            }
            
            if (employeeName) {
                // Find the info-list within this orderline
                const infoList = orderlineEl.querySelector('.info-list');
                if (infoList) {
                    // Create salesperson list item
                    const salespersonLi = document.createElement('li');
                    salespersonLi.className = 'salesperson-display';
                    salespersonLi.style.cssText = 'color: #28a745; font-size: 0.85em; font-style: italic;';
                    salespersonLi.innerHTML = `<i class="fa fa-user me-1" style="font-size: 0.8em;"></i>${employeeName}`;
                    
                    // Add to the info-list
                    infoList.appendChild(salespersonLi);
                    console.log("=== POS SALESPERSON DEBUG: Added salesperson display to orderline info-list");
                } else {
                    console.log("=== POS SALESPERSON DEBUG: No info-list found in orderline");
                }
            }
        });
    }, 100);
};

// Function to update salesperson display for all current orderlines
function updateAllOrderlinesWithSalesperson(employeeName) {
    const orderlines = document.querySelectorAll('.orderline');
    orderlines.forEach((orderlineEl) => {
        // Remove existing salesperson display
        const existingSalesperson = orderlineEl.querySelector('.salesperson-display');
        if (existingSalesperson) {
            existingSalesperson.remove();
        }
        
        if (employeeName) {
            // Find the info-list within this orderline
            const infoList = orderlineEl.querySelector('.info-list');
            if (infoList) {
                // Create salesperson list item
                const salespersonLi = document.createElement('li');
                salespersonLi.className = 'salesperson-display';
                salespersonLi.style.cssText = 'color: #28a745; font-size: 0.85em; font-style: italic;';
                salespersonLi.innerHTML = `<i class="fa fa-user me-1" style="font-size: 0.8em;"></i>${employeeName}`;
                
                // Add to the info-list
                infoList.appendChild(salespersonLi);
            }
        }
    });
}

// Export the function globally
window.updateAllOrderlinesWithSalesperson = updateAllOrderlinesWithSalesperson;

// Check periodically for orderlines to update
setInterval(addSalespersonDisplayToOrderLines, 2000);

console.log("=== POS SALESPERSON DEBUG: orderline_display.js initialized ===");