# Odoo 18 Project Configuration

## Critical Framework Changes

### XML View Tags
- **IMPORTANT**: In Odoo 18, the `<tree>` tag has been **replaced** with `<list>` tag
- Always use `<list>` instead of `<tree>` for list views in XML view definitions

### Example:
```xml
<!-- Odoo 18 Correct Syntax -->
<record id="view_partner_list" model="ir.ui.view">
    <field name="name">Partner List</field>
    <field name="model">res.partner</field>
    <field name="arch" type="xml">
        <list string="Partners">
            <field name="name"/>
            <field name="email"/>
            <field name="phone"/>
        </list>
    </field>
</record>
```

- Odoo started **deprecating the old attrs syntax**: 

In **Odoo ≤15**, you’d typically write something like:

```xml
<field name="my_field" attrs="{'invisible': [('state', '=', 'done')]}"/>
```

In **Odoo 16 and above**, they encourage the **new declarative syntax** using invisible, readonly, required directly with domain tuples, like: 

```xml
<field name="my_field" invisible="state == 'done'"/>
```

or: 

```xml
<field name="my_field" invisible="state in ['done', 'cancel']"/>
```

- This is a breaking change from previous Odoo versions



## Project Structure

- Main Odoo directory: `/Volumes/Samsung T5/Odoo/Development & Study/odoo-18.0/`
- Enterprise: `/Volumes/Samsung T5/Odoo/Development & Study/odoo-18.0/enterprise/`

## Development Notes
- Always check for Odoo 18 compatibility when creating or modifying views
- Use the correct XML syntax for all view definitions