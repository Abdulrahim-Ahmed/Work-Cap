# POS Salesperson — Visual Update Fix Notes

This document summarizes the concrete changes that fixed the orange salesperson label not updating on orderlines and ensured correct backend persistence.

## Root causes
- The orderline DOM was being updated by index, which is brittle when the DOM and in-memory orderlines diverge.
- The click handler updated data but did not reliably point to the correct DOM node after the async popup.
- General assignment (button) and individual assignment (icon) used different DOM strategies and could leave stale visual elements.
- After cleanup, the `SalespersonButton` component was not registered in `ControlButtons`, causing a component definition error in POS.

## What we changed

### 1) Reliable DOM targeting from the clicked icon
- Captured the orderline container at click-time and reused it after the async popup returns.
- New helper uses upward traversal from a known child element to find the nearest container that holds an `.info-list`.

Files:
- `static/src/js/OrderlineSalespersonIcon.js`

```js
// Capture container element at click time for reliable DOM update
const containerElAtClick = (event.currentTarget?.closest && event.currentTarget.closest('.orderline'))
    || (this.el?.closest && this.el.closest('.orderline'))
    || this.el
    || event.currentTarget;

// After selecting/removing an employee
SalespersonVisualManager.updateFromChildElement(containerElAtClick, selectedEmployee.name /* or null */);
```

- `static/src/js/SalespersonVisualManager.js`

```js
static updateFromChildElement(childEl, employeeName) {
  let el = childEl; let container = null;
  for (let i = 0; i < 10 && el; i++) {
    if (el.classList?.contains('orderline')) { container = el; break; }
    if (el.querySelector && el.querySelector('.info-list')) { container = el; break; }
    el = el.parentElement;
  }
  if (container) this.updateIndividualOrderlineDOM(container, employeeName);
}
```

Effect: Immediately updates the orange badge on the exact line that was clicked, regardless of list re-renders.

### 2) Stable selectors for fallback
- Added data attributes to the orderline root so we can target specific lines by `cid/id/product_id` as a fallback.

File:
- `static/src/xml/pos.xml`

```xml
<xpath expr="//li[hasclass('orderline')]" position="attributes">
  <attribute name="t-att-data-line-id">line.id</attribute>
  <attribute name="t-att-data-line-cid">line.cid</attribute>
  <attribute name="t-att-data-product-id">line.product_id</attribute>
</xpath>
```

Effect: Visual updates can still locate the correct line even if traversal fails.

### 3) Don’t overwrite individual labels with general assignment
- When applying a general salesperson via the button, only update lines that do not have an individual assignment.
- When updating a single line, update/remove the dynamic `.salesperson-display` OR the template-driven `.salesperson-item` text, whichever exists.

File:
- `static/src/js/SalespersonVisualManager.js` (updateOrderlineDisplay + updateIndividualOrderlineDOM)

Effect: The per-line label is accurate and never overwritten by general assignment.

### 4) Backend payload contains only `employee_id`
- Injected only `employee_id` into `result.lines[i][2]` during order serialization.

File:
- `static/src/js/pos_order_patch.js`

```js
const result = super.serialize(...arguments);
if (result.lines && Array.isArray(result.lines) && this.lines) {
  result.lines.forEach((uiLine, idx) => {
    const line = this.lines[idx];
    if (!Array.isArray(uiLine) || uiLine.length < 3) return;
    const vals = uiLine[2] || {};
    if (line?.employee_id !== undefined && line?.employee_id !== null) {
      vals.employee_id = line.employee_id;
    }
    uiLine[2] = vals;
  });
}
```

Effect: Avoids server errors on `employee_name` and guarantees `employee_id` persists to `pos.order.line`.

### 5) Backend reads and stores `employee_id`
- `_order_line_fields` inspects each UI line’s third element and sets `employee_id`.

File:
- `models/pos_order.py`

```python
if isinstance(line, list) and len(line) >= 3:
    data = line[2]
    if isinstance(data, dict) and 'employee_id' in data:
        result['employee_id'] = data['employee_id']
```

Effect: The employee is visible after validation in Point of Sale > Orders.

### 6) Register `SalespersonButton` in ControlButtons (post-cleanup)
- After pruning files, POS failed to find `SalespersonButton` referenced in the template.
- Restored a minimal registrar that adds `SalespersonButton` to `ControlButtons.components`.

File:
- `static/src/js/control_buttons.js`

```js
/** @odoo-module **/
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SalespersonButton } from "./SalespersonButton";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, { setup() { super.setup(); } });
ControlButtons.components = { ...ControlButtons.components, SalespersonButton };
```

Effect: Eliminates the Owl component-definition error and shows the Salesperson button.

## Result
- Orange label updates instantly on individual changes.
- General assignment respects individual overrides.
- Backend stores `employee_id` correctly with no errors.
- POS template loads with `SalespersonButton` registered.
