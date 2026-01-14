# Custom Operations Report

This module adds an Operations Report wizard that can generate PDF and Excel
reports for sales operations. The Excel output is built directly from the
wizard (no `report_xlsx` dependency).

## Features

- Wizard with date range and section filters.
- PDF output (existing QWeb report).
- Excel output with multiple sections, enabled/disabled via checkboxes.
- Section data pulled from sales orders, deliveries, and returns.

## How to Use

1) Go to `Operations Reports > Operations Report`.
2) Set `From Date` and `To Date`.
3) Choose which sections to include.
4) Choose the output type (PDF/Excel) and click the corresponding button.

If no section is selected, the wizard raises a validation error.

## Section Filters (Booleans)

These booleans control which sections appear in the Excel output:

- `show_sales_section` -> `تقرير المبيعات`
- `show_delivery_to_carrier_section` -> `ما تم تسليمه لشركة الشحن`
- `show_returns_section` -> `القطع التي تم استرجاعها`
- `show_delivery_to_customer_section` -> `ما تم تسليمه للعملاء`
- `show_daily_quotes_section` -> `الطلبات الجديده (يومي)`

## Section Details and Field Sources

### 1) تقرير المبيعات (Sales Report)
Source: `sale.order` and `sale.order.line`

Columns:
- تاريخ الطلب: `sale.order.date_order` (fallback `create_date`)
- رقم الاوردر: `sale.order.name`
- عدد القطع: sum of `sale.order.line.product_uom_qty` for non-service lines
- قيمة الاوردر: `sale.order.amount_total`
- تكلفة القطع في الاوردر: sum of line cost
  - `sale.order.line.purchase_price` when available, fallback `product.standard_price`
- ربح المنتج: total - cost
- هامش الربح %: profit / total

Notes:
- Service products and section/note lines are excluded.

### 2) ما تم تسليمه لشركة الشحن (Delivered to Carrier)
Source: first picking for the order (`sale.order.picking_ids`)

Columns:
- تاريخ التسليم: first picking `scheduled_date` (fallback `date_done`)
- رقم الاوردر: `sale.order.name`
- عدد القطع: quantity from picking moves, fallback line qty
- اسم المنتج: `sale.order.line.product_id.display_name`
- قيمة القطع: `sale.order.line.price_subtotal`
- حالة التسليم: `تم التسليم` if any done picking to customer exists
- تكلفة المنتج في الاوردر: line cost (purchase price or standard price)
- ربح المنتج: value - cost
- هامش الربح %: profit / value

### 3) القطع التي تم استرجاعها (Returned Items)
Source: return pickings (customer -> internal)

Columns:
- تاريخ الاستلام: `stock.picking.scheduled_date`
- تاريخ الارجاع: `stock.picking.date_done` (fallback `scheduled_date`)
- رقم الاوردر: `sale.order.name`
- اسم المنتج: `sale.order.line.product_id.display_name`
- عدد القطع: quantity from return moves
- قيمة القطع: line unit price * returned qty

### 4) ما تم تسليمه للعملاء (Delivered to Customers)
Source: pickings with destination usage = customer and state = done

Columns:
- تاريخ التسليم: `stock.picking.scheduled_date` (fallback `date_done`)
- رقم الاوردر: `sale.order.name`
- عدد القطع: quantity from picking moves
- اسم المنتج: `sale.order.line.product_id.display_name`
- قيمة القطع: line unit price * delivered qty
- قيمة الشحن: sum of delivery lines `sale.order.line.is_delivery`
- حالة التسليم: `تم التسليم` (always done here)

### 5) الطلبات الجديده (يومي) (Quotations Only)
Source: quotations (`sale.order` with state draft/sent)

Columns:
- تاريخ الاوردر: `sale.order.date_order`
- اسم العميل: `sale.order.partner_id.name`
- اسم المنتج: `sale.order.line.product_id.display_name`
- عدد القطع: `sale.order.line.product_uom_qty`
- عدد القطع المطلوبه: custom field `sale.order.line.demand_qty`
  - Provided by module: `/opt/odoo18/pistage-main/available_qty_check`
- العدد في محزن الاونلاين: `product.qty_available` with context location
  - Location = `sale.order.warehouse_id.lot_stock_id`
- القطع المتاحه: `product.qty_available` with context warehouse
  - Warehouse = `sale.order.warehouse_id`

Notes:
- Service products and section/note lines are excluded.

## Technical Notes

- Excel output is generated in `wizard/operations_report_wizard.py`.
- Section filters apply only to Excel output. If you need the same in PDF,
  wire the booleans into the QWeb template.
- Quantities for deliveries/returns are read from `stock.move`.

