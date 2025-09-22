# JavaScript Fixes for Odoo 18 Compatibility

## Issues Fixed

### 1. ORM API Changes
**File**: `static/src/js/booking_form.js`
- **Issue**: Used old `orm.call()` syntax for write operations
- **Fix**: Changed to `orm.write()` and `orm.searchRead()` methods
- **Changes**:
  - `this.orm.call("event.booking", "write", [[id], data])` → `this.orm.write("event.booking", [id], data)`
  - `this.orm.call("event.hall", "search_read", [domain], fields, options)` → `this.orm.searchRead("event.hall", domain, fields, options)`

### 2. Field Widget Registration
**File**: `static/src/js/meal_selection_widget.js`
- **Issue**: Incorrect field widget registration syntax
- **Fix**: Updated to use proper Odoo 18 field registration format
- **Changes**:
  - Added `standardFieldProps` import
  - Added proper `static props` definition
  - Changed registry format: `registry.category("fields").add("meal_selection", MealSelectionWidget)` → `registry.category("fields").add("meal_selection", { component: MealSelectionWidget })`

### 3. Missing XML Template
**File**: `static/src/xml/meal_selection_widget.xml` (Created)
- **Issue**: Widget referenced template that didn't exist
- **Fix**: Created proper OWL template with Bootstrap styling
- **Features**:
  - Meal filter buttons
  - Package selection interface
  - Selected meals display
  - Total cost calculation

### 4. Asset Bundle Update
**File**: `__manifest__.py`
- **Issue**: Missing XML template in assets
- **Fix**: Added XML template to web.assets_backend bundle

## Compatibility Notes

### ORM API Changes in Odoo 18
- `orm.call(model, "write", [ids], data)` → `orm.write(model, ids, data)`
- `orm.call(model, "search_read", [domain], fields, options)` → `orm.searchRead(model, domain, fields, options)`

### Field Widget Registration
- Must include `standardFieldProps` for proper field behavior
- Registry format changed to object with `component` property

### Template Requirements
- All OWL components must have corresponding XML templates
- Templates must be included in asset bundles
- Use `owl="1"` attribute for OWL templates

## Testing
- ✅ JavaScript syntax validated
- ✅ ORM API calls updated to Odoo 18 format
- ✅ Field widget registration corrected
- ✅ XML template created and included
- ✅ Asset bundle updated

## Installation
After these fixes, the module should load without JavaScript errors in Odoo 18.
