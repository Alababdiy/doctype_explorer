# DocType Explorer

A comprehensive Frappe app for exploring, documenting, and analyzing Frappe DocTypes. Generate detailed JSON/HTML documentation, compare DocTypes, inspect dependencies, and access DocType information via RESTful API.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Desk Page Interface](#desk-page-interface)
  - [API Endpoints](#api-endpoints)
  - [Bench Commands](#bench-commands)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Examples](#examples)
- [License](#license)

## Features

- **📄 Generate Documentation**: Create comprehensive JSON and HTML documentation for any DocType
- **🔍 Explore DocTypes**: View complete DocType structure including fields, links, child tables, and permissions
- **🔗 Dependency Analysis**: Inspect DocType dependencies and relationships
- **⚖️ Compare DocTypes**: Compare two DocTypes to find differences
- **📦 Bulk Operations**: Generate documentation for multiple DocTypes or entire modules
- **🌐 RESTful API**: Access DocType information via authenticated API endpoints
- **📊 Formatted Output**: Get beautifully formatted JSON responses
- **🎯 Recursive Depth Control**: Control how deep to explore linked DocTypes

## Installation

### Prerequisites

- Frappe Framework installed
- Bench CLI configured

### Install the App

```bash
# Get the app
bench get-app https://github.com/Alababdiy/doctype-explorer.git

# Install on your site
bench --site your-site.local install-app doctype_explorer

# Build assets and restart
bench build
bench restart
```

### Verify Installation

After installation, you should see the "DocType Explorer" page in your Frappe desk.

## Usage

### Desk Page Interface

1. Navigate to **DocType Explorer** from the Frappe desk
2. Enter a **DocType Name** (e.g., "Sales Order", "Customer")
3. Set the **Level** (0 for infinite depth, or a positive number for limited depth)
4. Click **Generate JSON** to create documentation
5. Use **Copy JSON** to copy the output to clipboard
6. Use **Export HTML** to generate a formatted HTML documentation file

#### Features:
- **DocType Name**: Select any DocType from your system
- **Level**: Control recursion depth (0 = infinite, 1+ = limited depth)
- **Generate JSON**: Creates formatted JSON documentation
- **Copy JSON**: Copies JSON to clipboard
- **Export HTML**: Generates a styled HTML file saved to `/files/doctype_docs/`

### API Endpoints

#### 1. Get DocType Documentation (GET)

**Endpoint**: `/api/method/doctype_explorer.explorer.get_doctype_api`

**Authentication**: Required via `AUTH-KEY` parameter or header

**Parameters**:
- `AUTH-KEY` (required): Authentication key
- `doctype_name` (required): Name of the DocType to document
- `level` (optional): Maximum recursion depth (0 for infinite, default: 0)

**Example Request**:
```bash
curl -X GET "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_api?AUTH-KEY=your_key&doctype_name=Sales%20Order&level=2"
```

**Example with Header Authentication**:
```bash
curl -X GET "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_api?doctype_name=Customer&level=1" \
  -H "AUTH-KEY: your_key"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "doctype_name": "Sales Order",
    "module": "Selling",
    "fields": [...],
    "linked_doctypes": {...},
    "child_tables": {...},
    "permissions": [...],
    ...
  },
  "message": "Documentation generated for Sales Order",
  "doctype_name": "Sales Order",
  "level": 2
}
```

#### 2. Generate DocType Documentation

**Endpoint**: `/api/method/doctype_explorer.explorer.generate_doctype_documentation`

**Parameters**:
- `doctype_name` (required): Name of the DocType
- `return_json` (optional): If `true`, returns JSON instead of saving to file
- `level` (optional): Maximum recursion depth (0 for infinite)

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.generate_doctype_documentation" \
  -H "Content-Type: application/json" \
  -d '{
    "doctype_name": "Sales Order",
    "return_json": true,
    "level": 2
  }'
```

#### 3. Bulk Generate Documentation

**Endpoint**: `/api/method/doctype_explorer.explorer.bulk_generate_documentation`

**Parameters**:
- `doctypes` (optional): List of DocType names
- `module` (optional): Generate for all DocTypes in a module

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.bulk_generate_documentation" \
  -H "Content-Type: application/json" \
  -d '{
    "doctypes": ["Sales Order", "Purchase Order", "Item"]
  }'
```

#### 4. Compare DocTypes

**Endpoint**: `/api/method/doctype_explorer.explorer.compare_doctypes`

**Parameters**:
- `doctype1` (required): First DocType name
- `doctype2` (required): Second DocType name

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.compare_doctypes" \
  -H "Content-Type: application/json" \
  -d '{
    "doctype1": "Sales Order",
    "doctype2": "Purchase Order"
  }'
```

#### 5. Get DocType Dependencies

**Endpoint**: `/api/method/doctype_explorer.explorer.get_doctype_dependencies`

**Parameters**:
- `doctype_name` (required): DocType name
- `depth` (optional): How many levels deep to search (default: 1)

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_dependencies" \
  -H "Content-Type: application/json" \
  -d '{
    "doctype_name": "Sales Order",
    "depth": 2
  }'
```

#### 6. Export to HTML

**Endpoint**: `/api/method/doctype_explorer.explorer.export_to_html`

**Parameters**:
- `doctype_name` (required): DocType name

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.export_to_html" \
  -H "Content-Type: application/json" \
  -d '{
    "doctype_name": "Sales Order"
  }'
```

### Bench Commands

#### Generate Documentation via Console

```bash
bench --site your-site.local console
```

Then in the console:
```python
from doctype_explorer.explorer import document_doctype
document_doctype("Sales Order")
```

#### Execute from Bench Command

```bash
bench --site your-site.local execute doctype_explorer.explorer.execute_from_bench --args "['Sales Order']"
```

## API Reference

### Response Structure

The JSON documentation includes:

```json
{
  "doctype_name": "Sales Order",
  "module": "Selling",
  "is_submittable": true,
  "is_child_table": false,
  "track_changes": true,
  "allow_rename": false,
  "allow_import": true,
  "is_tree": false,
  "editable_grid": false,
  "quick_entry": false,
  "title_field": "name",
  "image_field": null,
  "description": "Sales Order description",
  "generated_at": "2024-01-15T10:30:00",
  "fields": [
    {
      "fieldname": "customer",
      "label": "Customer",
      "fieldtype": "Link",
      "options": "Customer",
      "required": true,
      "read_only": false,
      "in_list_view": true,
      "description": "Customer name",
      "default": "",
      "length": 140,
      ...
    }
  ],
  "linked_doctypes": {
    "customer": {
      "doctype_name": "Customer",
      "field_reference": "customer",
      "label": "Customer",
      "fields": [...]
    }
  },
  "child_tables": {
    "items": {
      "doctype_name": "Sales Order Item",
      "field_reference": "items",
      "label": "Items",
      "fields": [...],
      "nested_links": {...}
    }
  },
  "permissions": [
    {
      "role": "Sales User",
      "read": true,
      "write": true,
      "create": true,
      "delete": false,
      "submit": true,
      "cancel": true,
      "amend": false
    }
  ],
  "naming_rule": "Naming Series",
  "sort_field": "creation",
  "sort_order": "desc",
  "meta_info": {
    "total_fields": 45,
    "link_fields_count": 8,
    "child_table_count": 2,
    "required_fields_count": 5
  }
}
```

### Field Information

Each field includes:
- `fieldname`: Internal field name
- `label`: Display label
- `fieldtype`: Field type (Data, Link, Table, etc.)
- `options`: Options (for Link fields, this is the linked DocType)
- `required`: Whether field is required
- `read_only`: Whether field is read-only
- `in_list_view`: Whether field appears in list view
- `in_standard_filter`: Whether field appears in standard filters
- `in_global_search`: Whether field is searchable globally
- `bold`: Whether field is bold
- `hidden`: Whether field is hidden
- `print_hide`: Whether field is hidden in print
- `unique`: Whether field must be unique
- `description`: Field description
- `default`: Default value
- `length`: Field length
- `precision`: Decimal precision
- `depends_on`: Field dependencies

## Configuration

### Setting AUTH-KEY for API

The `get_doctype_api` endpoint requires an AUTH-KEY. Configure it using one of these methods (priority order):

#### 1. Environment Variable (Highest Priority)

```bash
export DOCTYPE_EXPLORER_AUTH_KEY="your_secret_key_here"
```

#### 2. Site Config

```bash
bench --site your-site.local set-config doctype_explorer_auth_key "your_secret_key_here"
```

This adds the key to `sites/your-site.local/site_config.json`:
```json
{
  "doctype_explorer_auth_key": "your_secret_key_here"
}
```

#### 3. System Settings (Lowest Priority)

Add a custom field `custom_doctype_explorer_auth_key` in System Settings DocType.

### Security Best Practices

1. **Use Strong Keys**: Generate a strong, random authentication key
2. **Environment Variables**: Prefer environment variables for production
3. **HTTPS Only**: Always use HTTPS in production
4. **Key Rotation**: Regularly rotate your AUTH-KEY

## Examples

### Example 1: Get Customer DocType Documentation

```bash
curl -X GET "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_api?AUTH-KEY=your_key&doctype_name=Customer&level=1" | jq '.'
```

### Example 2: Generate Documentation for Multiple DocTypes

```python
import frappe

result = frappe.call(
    'doctype_explorer.explorer.bulk_generate_documentation',
    doctypes=['Sales Order', 'Purchase Order', 'Item']
)

print(f"Generated {result['successful']} out of {result['total']} DocTypes")
```

### Example 3: Compare Two DocTypes

```python
import frappe

comparison = frappe.call(
    'doctype_explorer.explorer.compare_doctypes',
    doctype1='Sales Order',
    doctype2='Purchase Order'
)

print(f"Common fields: {len(comparison['comparison']['common_fields'])}")
print(f"Only in Sales Order: {comparison['comparison']['fields_only_in_dt1']}")
print(f"Only in Purchase Order: {comparison['comparison']['fields_only_in_dt2']}")
```

### Example 4: Get Dependencies with Python

```python
import frappe

dependencies = frappe.call(
    'doctype_explorer.explorer.get_doctype_dependencies',
    doctype_name='Sales Order',
    depth=2
)

print(f"Direct links: {len(dependencies['dependencies']['direct_links'])}")
print(f"Child tables: {len(dependencies['dependencies']['child_tables'])}")
```

### Example 5: Using in JavaScript (Frontend)

```javascript
frappe.call({
    method: 'doctype_explorer.explorer.generate_doctype_documentation',
    args: {
        doctype_name: 'Sales Order',
        return_json: true,
        level: 2
    },
    callback: function(r) {
        if (r.message && r.message.success) {
            console.log('DocType Structure:', r.message.data);
        }
    }
});
```

### Example 6: Save JSON to File

```bash
curl -X GET "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_api?AUTH-KEY=your_key&doctype_name=Item&level=0" \
  -o item_doctype.json
```

## Troubleshooting

### API Returns "AUTH-KEY validation not configured"

**Solution**: Set the AUTH-KEY using one of the configuration methods above.

### Module Not Found Error

**Solution**: Ensure the app is properly installed:
```bash
bench --site your-site.local install-app doctype_explorer
bench restart
```

### Circular Reference Warnings

When exploring DocTypes with circular references, the documentation will include:
```json
{
  "_circular_reference": true,
  "doctype": "DocType Name",
  "depth_exceeded": false
}
```

This is normal and prevents infinite loops.

### Large DocType Performance

For very large DocTypes with many linked DocTypes:
- Use `level=1` or `level=2` to limit depth
- Consider using bulk operations during off-peak hours

## License

MIT



---

**Note**: This app is designed for Frappe Framework and requires proper Frappe installation and configuration.
