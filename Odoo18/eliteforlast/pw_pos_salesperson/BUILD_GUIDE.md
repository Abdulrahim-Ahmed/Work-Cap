# Building a POS Salesperson Per-Line Assignment Module (Odoo 18)

This guide walks you through creating a working module that:
- Loads employees into POS
- Assigns a general salesperson to all lines via a button
- Assigns/removes a salesperson per line via an icon
- Visually reflects the salesperson on each orderline
- Persists `employee_id` to `pos.order.line` after validation

All code snippets are from a minimal, working implementation and can be adapted.

## 1) Module scaffold

`__manifest__.py`
```python
{
    'name': 'POS Salesperson',
    'version': '18.0',
    'depends': ['point_of_sale', 'hr'],
    'assets': {
        'point_of_sale._assets_pos': [
            'your_module/static/src/js/pos_order_patch.js',
            'your_module/static/src/js/pos_order_line_patch.js',
            'your_module/static/src/js/models.js',
            'your_module/static/src/js/SalespersonVisualManager.js',
            'your_module/static/src/js/SalespersonButton.js',
            'your_module/static/src/js/OrderlineSalespersonIcon.js',
            'your_module/static/src/js/OrderlinePatch.js',
            'your_module/static/src/js/control_buttons.js',
            'your_module/static/src/xml/pos.xml',
        ],
    },
}
```

Keep assets minimal and deterministic. The control_buttons registrar is required so the template can find `SalespersonButton`.

## 2) Backend: fields and persistence

- Add `employee_id` to `pos.order.line`
- Ensure `_order_line_fields` accepts `employee_id` from UI payload
- Optionally compute an order-level `salesperson_id`

`models/pos_order.py`
```python
from odoo import api, fields, models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one('hr.employee', string='Salesperson')

    @api.model
    def _order_line_fields(self, line):
        result = super()._order_line_fields(line)
        if isinstance(line, list) and len(line) >= 3:
            data = line[2]
            if isinstance(data, dict) and 'employee_id' in data:
                result['employee_id'] = data['employee_id']
        elif isinstance(line, dict) and 'employee_id' in line:
            result['employee_id'] = line['employee_id']
        return result

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    employee_id = fields.Many2one('hr.employee', string='Salesperson')
```

- Add a compact banner to the order form to signal mixed line-level employees (optional):

`views/pos_order_view.xml`
```xml
<record id="view_pos_pos_form_inherit_salesperson" model="ir.ui.view">
  <field name="name">POS Order Form - Salesperson</field>
  <field name="model">pos.order</field>
  <field name="inherit_id" ref="point_of_sale.view_pos_pos_form"/>
  <field name="arch" type="xml">
    <xpath expr="//field[@name='lines']//list/field[@name='product_id']" position="after">
      <field name="employee_id" string="Salesperson" optional="show" force_save="1"/>
    </xpath>
    <xpath expr="//field[@name='lines']//form//group/field[@name='product_id']" position="after">
      <field name="employee_id" string="Salesperson" force_save="1"/>
    </xpath>
    <xpath expr="//group[@name='order_fields']" position="inside">
      <field name="salesperson_id" invisible="has_mixed_employees"/>
      <field name="has_mixed_employees" invisible="1"/>
    </xpath>
    <xpath expr="//field[@name='salesperson_id']" position="after">
      <div class="alert alert-info d-flex align-items-center gap-2 p-2 my-2" role="alert" invisible="not has_mixed_employees" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        <i class="fa fa-info-circle"/>
        <div class="text-truncate small">
          <strong>Mixed Salespersons:</strong> Different order lines have different assigned salespersons. Check the individual line assignments below.
        </div>
      </div>
    </xpath>
  </field>
</record>
```

## 3) POS line model patch

- Store `employee_id` and `employee_name` on each line (used for display and serialization):

`static/src/js/pos_order_line_patch.js`
```js
/** @odoo-module **/
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
  setup(vals) {
    super.setup(vals);
    this.employee_id = vals.employee_id || false;
    this.employee_name = vals.employee_name || false;
  }
});
```

`static/src/js/models.js`
```js
/** @odoo-module **/
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
  setup() {
    super.setup(...arguments);
    this.employee_id = this.employee_id || null;
    this.employee_name = this.employee_name || null;
    this.salesperson = this.salesperson || null;
  },

  // Keep getDisplayData unchanged to avoid prop validation issues

  export_as_JSON() {
    const result = super.export_as_JSON();
    result.employee_id = this.employee_id;
    result.employee_name = this.employee_name;
    return result;
  },

  init_from_JSON(json) {
    super.init_from_JSON(json);
    this.employee_id = json.employee_id || null;
    this.employee_name = json.employee_name || null;
    if (this.employee_id && this.pos) {
      const employees = this.pos.employees || [];
      this.salesperson = employees.find((e) => e.id === this.employee_id);
    }
  }
});
```

## 4) Inject `employee_id` on serialize

- Ensure the payload to backend includes `employee_id` in each line’s values (3rd element):

`static/src/js/pos_order_patch.js`
```js
/** @odoo-module **/
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
  serialize() {
    const result = super.serialize(...arguments);
    if (result.lines && Array.isArray(result.lines) && this.lines) {
      result.lines.forEach((uiLine, index) => {
        try {
          const modelLine = this.lines[index];
          if (!Array.isArray(uiLine) || uiLine.length < 3) return;
          const vals = uiLine[2] || {};
          const empId = modelLine?.employee_id ?? null;
          if (empId !== null && empId !== undefined) {
            vals.employee_id = empId;
          }
          uiLine[2] = vals;
        } catch (e) {}
      });
    }
    return result;
  }
});
```

## 5) POS UI — templates and components

- Add a per-line icon to set/remove the salesperson
- Add a line-level visual label
- Add stable attributes on each `orderline` for targeting by selectors

`static/src/xml/pos.xml`
```xml
<templates id="template" xml:space="preserve">
  <t t-name="pw_pos_salesperson.SalespersonButton">
    <button t-attf-class="{{props.class}} salesperson-btn" t-on-click="onClick" title="Select salesperson for order lines">
      <div class="d-flex align-items-center">
        <i class="fa fa-user-tie me-2"/>
        <span t-esc="buttonText"/>
      </div>
    </button>
  </t>

  <t t-name="pw_pos_salesperson.OrderlineSalespersonIcon">
    <button class="btn btn-sm p-1 border-0 bg-transparent orderline-salesperson-icon" t-on-click="onClick" t-att-title="iconTitle">
      <i t-attf-class="{{iconClass}}" style="font-size: 0.8em;"/>
    </button>
  </t>

  <t t-name="point_of_sale.Orderline" t-inherit="point_of_sale.Orderline" t-inherit-mode="extension">
    <xpath expr="//li[hasclass('orderline')]" position="attributes">
      <attribute name="t-att-data-line-id">line.id</attribute>
      <attribute name="t-att-data-line-cid">line.cid</attribute>
      <attribute name="t-att-data-product-id">line.product_id</attribute>
    </xpath>
    <xpath expr="//li[hasclass('price-per-unit')]" position="after">
      <li class="d-flex justify-content-end">
        <OrderlineSalespersonIcon line="line"/>
      </li>
    </xpath>
    <xpath expr="//ul[hasclass('info-list')]" position="inside">
      <li t-if="line.employee_name" class="salesperson-item">
        <i class="fa fa-user me-1" style="color: #28a745; font-size: 0.8em;"/>
        <span t-esc="line.employee_name" style="color: #28a745; font-size: 0.85em; font-style: italic;"/>
      </li>
    </xpath>
  </t>
</templates>
```

- Patch Orderline component to insert our icon component:

`static/src/js/OrderlinePatch.js`
```js
/** @odoo-module **/
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { OrderlineSalespersonIcon } from "./OrderlineSalespersonIcon";
import { patch } from "@web/core/utils/patch";

patch(Orderline, {
  components: {
    ...Orderline.components,
    OrderlineSalespersonIcon,
  },
});
```

- Register the button component in ControlButtons so the template can use it:

`static/src/js/control_buttons.js`
```js
/** @odoo-module **/
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SalespersonButton } from "./SalespersonButton";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, { setup() { super.setup(); } });
ControlButtons.components = { ...ControlButtons.components, SalespersonButton };
```

## 6) General salesperson button (assign to all lines without an individual assignment)

`static/src/js/SalespersonButton.js`
```js
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { SalespersonVisualManager } from "./SalespersonVisualManager";

export class SalespersonButton extends Component {
  static template = "pw_pos_salesperson.SalespersonButton";
  static props = { class: { type: String, optional: true } };
  static defaultProps = { class: "btn btn-light btn-lg lh-lg" };

  setup() {
    this.pos = usePos();
    this.ui = useState(useService("ui"));
    this.dialog = useService("dialog");
    this.notification = useService("notification");
  }

  get buttonText() { return _t("Salesperson"); }

  async onClick() {
    try {
      const order = this.pos.get_order();
      if (!order) {
        this.notification.add(_t("No active order to assign salesperson"), { type: 'danger' });
        return;
      }
      let employees = [];
      const hrEmployee = this.pos.data?.["hr.employee"]; // Odoo 18 data container
      if (hrEmployee?.data) employees = hrEmployee.data;
      else if (Array.isArray(hrEmployee)) employees = hrEmployee;
      else if (hrEmployee?.records instanceof Map) employees = Array.from(hrEmployee.records.values());
      else if (hrEmployee?.records && typeof hrEmployee.records === 'object') employees = Object.values(hrEmployee.records);
      else if (this.pos.data?.records?.["hr.employee"]) {
        const recs = this.pos.data.records["hr.employee"];
        employees = recs instanceof Map ? Array.from(recs.values()) : Object.values(recs);
      } else if (this.pos.models?.["hr.employee"]?.records) {
        const recs = this.pos.models["hr.employee"].records;
        employees = recs instanceof Map ? Array.from(recs.values()) : Object.values(recs);
      }
      if (!employees.length) {
        this.dialog.add(AlertDialog, { title: _t("No Employees Found"), body: _t("No active employees found.") });
        return;
      }
      const selectionList = employees.map((e) => ({ id: e.id, label: e.name, item: e }));
      const selectedEmployee = await makeAwaitable(this.dialog, SelectionPopup, { title: _t("Select Salesperson"), list: selectionList });
      if (selectedEmployee === undefined) return;

      if (selectedEmployee) {
        let assignedCount = 0;
        for (const line of order.get_orderlines()) {
          if (!line.employee_id || !line.employee_name) {
            line.employee_id = selectedEmployee.id;
            line.employee_name = selectedEmployee.name;
            line.salesperson = selectedEmployee;
            assignedCount++;
          }
        }
        order.salesperson_id = selectedEmployee; // convenience
        setTimeout(() => SalespersonVisualManager.updateAllOrderlinesDisplay(selectedEmployee.name), 200);
        this.notification.add(_t("General salesperson %s assigned to %s order lines", selectedEmployee.name, assignedCount), { type: 'success' });
      }
    } catch (error) {
      this.notification.add(_t("Error selecting salesperson: %s", error.message), { type: 'danger', sticky: true });
    }
  }
}
```

## 7) Per-line icon (assign/remove per line)

`static/src/js/OrderlineSalespersonIcon.js`
```js
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { SalespersonVisualManager } from "./SalespersonVisualManager";

export class OrderlineSalespersonIcon extends Component {
  static template = "pw_pos_salesperson.OrderlineSalespersonIcon";
  static props = { line: { type: Object } };

  setup() {
    this.pos = usePos();
    this.ui = useState(useService("ui"));
    this.dialog = useService("dialog");
    this.notification = useService("notification");
  }

  get currentEmployeeName() {
    if (this.props.line.employee_name) return this.props.line.employee_name;
    if (this.props.line.employee_id && this.pos.data?.["hr.employee"]) {
      const store = this._getEmployeesList();
      const emp = store.find((e) => e.id === this.props.line.employee_id);
      return emp ? emp.name : null;
    }
    return null;
  }
  get iconClass() { return this.currentEmployeeName ? "fa fa-user text-success" : "fa fa-user-plus text-muted"; }
  get iconTitle() { return this.currentEmployeeName ? _t("Assigned to: %s (click to change)", this.currentEmployeeName) : _t("Assign salesperson to this line"); }

  _getEmployeesList() {
    let employees = [];
    const hrEmployee = this.pos.data?.["hr.employee"];
    if (hrEmployee?.data) employees = hrEmployee.data;
    else if (Array.isArray(hrEmployee)) employees = hrEmployee;
    else if (hrEmployee?.records instanceof Map) employees = Array.from(hrEmployee.records.values());
    else if (hrEmployee?.records && typeof hrEmployee.records === 'object') employees = Object.values(hrEmployee.records);
    else if (this.pos.data?.records?.["hr.employee"]) {
      const recs = this.pos.data.records["hr.employee"];
      employees = recs instanceof Map ? Array.from(recs.values()) : Object.values(recs);
    } else if (this.pos.models?.["hr.employee"]?.records) {
      const recs = this.pos.models["hr.employee"].records;
      employees = recs instanceof Map ? Array.from(recs.values()) : Object.values(recs);
    }
    return employees || [];
  }

  async onClick(event) {
    event.stopPropagation();
    const containerElAtClick = (event.currentTarget?.closest && event.currentTarget.closest('.orderline'))
      || (this.el?.closest && this.el.closest('.orderline'))
      || this.el
      || event.currentTarget;

    try {
      const order = this.pos.get_order();
      if (!order) {
        this.notification.add(_t("No active order found"), { type: 'danger' });
        return;
      }
      const employees = this._getEmployeesList();
      if (!employees?.length) {
        this.dialog.add(AlertDialog, { title: _t("No Employees Found"), body: _t("No active employees found.") });
        return;
      }
      const selectionList = [{ id: null, label: _t("Remove Salesperson"), item: null }];
      selectionList.push(...employees.map((e) => ({ id: e.id, label: e.name, item: e })));
      const selectedEmployee = await makeAwaitable(this.dialog, SelectionPopup, { title: _t("Select Salesperson for Line"), list: selectionList });
      if (selectedEmployee === undefined) return;

      const targetLine = order.get_orderlines().find((l) =>
        (l.product && l.product.id === this.props.line.product_id) ||
        (l.id === this.props.line.id) ||
        (l.cid === this.props.line.cid) ||
        (l.get_product && l.get_product().id === this.props.line.product_id)
      );
      if (!targetLine) {
        this.notification.add(_t("Could not find target order line"), { type: 'danger' });
        return;
      }

      if (selectedEmployee && selectedEmployee.id !== undefined && selectedEmployee.id !== null) {
        targetLine.employee_id = selectedEmployee.id;
        targetLine.employee_name = selectedEmployee.name;
        targetLine.salesperson = selectedEmployee;
        SalespersonVisualManager.updateFromChildElement(containerElAtClick, selectedEmployee.name);
        this.notification.add(_t("Salesperson %s assigned to line", selectedEmployee.name), { type: 'success' });
      } else {
        targetLine.employee_id = null;
        targetLine.employee_name = null;
        targetLine.salesperson = null;
        SalespersonVisualManager.updateFromChildElement(containerElAtClick, null);
        this.notification.add(_t("Salesperson removed from line"), { type: 'info' });
      }

      try {
        this.props.line.employee_id = targetLine.employee_id;
        this.props.line.employee_name = targetLine.employee_name;
        this.render();
        if (typeof order.trigger === 'function') order.trigger('change', order); else order.trigger?.('change');
      } catch (e) {}
    } catch (error) {
      this.notification.add(_t("Error selecting salesperson: %s", error.message), { type: 'danger', sticky: true });
    }
  }
}
```

## 8) Visual manager (DOM updates)

`static/src/js/SalespersonVisualManager.js`
```js
/** @odoo-module **/
export class SalespersonVisualManager {
  static updateOrderlineDisplay(orderLine, employeeName, isIndividual = false) {
    try {
      const orderlines = document.querySelectorAll('.orderline');
      if (isIndividual && orderLine) {
        try {
          const sels = [];
          const cid = orderLine.cid || orderLine._cid || null;
          const id = orderLine.id || null;
          const pid = orderLine.product?.id || orderLine.product_id || null;
          if (cid) sels.push(`.orderline[data-line-cid="${cid}"]`);
          if (id) sels.push(`.orderline[data-line-id="${id}"]`);
          if (pid) sels.push(`.orderline[data-product-id="${pid}"]`);
          for (const s of sels) {
            const el = document.querySelector(s);
            if (el) { this.updateIndividualOrderlineDOM(el, employeeName); return; }
          }
        } catch (_) {}
        const current = Array.from(document.querySelectorAll('.orderline'));
        const i = current.findIndex((el) => {
          const nameEl = el.querySelector('.product-name');
          const priceEl = el.querySelector('.price');
          if (nameEl && priceEl && orderLine.product_id && orderLine.price) {
            return nameEl.textContent.includes(orderLine.product_id.display_name) && priceEl.textContent.includes(orderLine.price.toString());
          }
          return false;
        });
        if (i >= 0) { this.updateIndividualOrderlineDOM(current[i], employeeName); return; }
        return;
      }
      orderlines.forEach((el) => {
        const existing = el.querySelector('.salesperson-display');
        const templateSpan = el.querySelector('.salesperson-item span');
        if (!isIndividual && existing?.dataset.isIndividual === 'true') return;
        if (existing) existing.remove();
        if (employeeName) {
          const info = el.querySelector('.info-list');
          if (info) {
            if (templateSpan) templateSpan.textContent = employeeName; else {
              const li = document.createElement('li');
              li.className = 'salesperson-display';
              li.style.cssText = 'color:#ff8800;font-size:0.85em;font-weight:bold;background:rgba(255,136,0,.1);padding:2px 6px;border-radius:3px;margin-top:2px;display:inline-block;';
              li.innerHTML = `<i class="fa fa-user me-1" style="font-size:.8em;"></i>${employeeName}`;
              li.dataset.isIndividual = isIndividual ? 'true' : 'false';
              info.appendChild(li);
            }
          }
        }
      });
    } catch (_) {}
  }

  static updateAllOrderlinesDisplay(name) { this.updateOrderlineDisplay(null, name, false); }
  static updateIndividualOrderlineDisplay(line, name) { this.updateOrderlineDisplay(line, name, true); }

  static updateFromChildElement(childEl, employeeName) {
    try {
      if (!childEl) return;
      let el = childEl; let container = null;
      for (let i = 0; i < 10 && el; i++) {
        if (el.classList?.contains('orderline')) { container = el; break; }
        if (el.querySelector && el.querySelector('.info-list')) { container = el; break; }
        el = el.parentElement;
      }
      if (container) this.updateIndividualOrderlineDOM(container, employeeName);
    } catch (_) {}
  }

  static updateIndividualOrderlineDOM(orderlineEl, employeeName) {
    const existing = orderlineEl.querySelector('.salesperson-display');
    if (existing) existing.remove();
    const templateBadge = orderlineEl.querySelector('.salesperson-item');
    const templateSpan = templateBadge?.querySelector('span');
    if (employeeName) {
      const info = orderlineEl.querySelector('.info-list');
      if (info) {
        if (templateSpan) templateSpan.textContent = employeeName; else {
          const li = document.createElement('li');
          li.className = 'salesperson-display';
          li.style.cssText = 'color:#ff8800;font-size:0.85em;font-weight:bold;background:rgba(255,136,0,.1);padding:2px 6px;border-radius:3px;margin-top:2px;display:inline-block;';
          li.innerHTML = `<i class=\"fa fa-user me-1\" style=\"font-size:.8em;\"></i>${employeeName}`;
          li.dataset.isIndividual = 'true';
          info.appendChild(li);
        }
      }
    } else {
      if (templateBadge) templateBadge.remove();
    }
  }

  static clearAllSalespersonDisplays() {
    try { document.querySelectorAll('.salesperson-display').forEach((d) => d.remove()); } catch (_) {}
  }
}

window.SalespersonVisualManager = SalespersonVisualManager;
window.updateAllOrderlinesWithSalesperson = (n) => SalespersonVisualManager.updateAllOrderlinesDisplay(n);
window.updateOrderlinesWithGeneralSalesperson = (n) => SalespersonVisualManager.updateAllOrderlinesDisplay(n);
```

## 9) Tips
- Always test with `?debug=assets` and hard refresh.
- Avoid altering `Orderline` prop shape to prevent Owl validation errors.
- Keep assets minimal and avoid duplicate DOM updaters.
- Only send `employee_id` to backend; do not send `employee_name`.
- If you reference a custom component in a template (like `SalespersonButton` inside `ControlButtons`), ensure you register it in JS (via `control_buttons.js`).

You now have a working foundation for per-line salesperson assignment in Odoo 18 POS. Add tests, linting, and configuration options as needed.