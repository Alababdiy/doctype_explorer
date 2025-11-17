# DocType Explorer API Quick Reference

## Authentication

All API endpoints (except `get_doctype_api`) use Frappe's standard authentication. The `get_doctype_api` endpoint requires an `AUTH-KEY`.

### Setting AUTH-KEY

```bash
# Method 1: Environment Variable
export DOCTYPE_EXPLORER_AUTH_KEY="your_key"

# Method 2: Site Config
bench --site your-site.local set-config doctype_explorer_auth_key "your_key"
```

---

## API Endpoints

### 1. Get DocType API (GET) - Authenticated

**Endpoint**: `/api/method/doctype_explorer.explorer.get_doctype_api`

**Method**: `GET`

**Authentication**: `AUTH-KEY` (required)

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `AUTH-KEY` | string | Yes | Authentication key (GET param or header) |
| `doctype_name` | string | Yes | Name of the DocType |
| `level` | integer | No | Recursion depth (0 = infinite, default: 0) |

**Example**:
```bash
curl -X GET "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_api?AUTH-KEY=key&doctype_name=Sales%20Order&level=2"
```

**Response**: Formatted JSON with DocType structure

---

### 2. Generate DocType Documentation

**Endpoint**: `/api/method/doctype_explorer.explorer.generate_doctype_documentation`

**Method**: `POST`

**Authentication**: Frappe session

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `doctype_name` | string | Yes | Name of the DocType |
| `return_json` | boolean | No | Return JSON instead of saving file (default: false) |
| `level` | integer | No | Recursion depth (0 = infinite, default: 0) |

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.generate_doctype_documentation" \
  -H "Content-Type: application/json" \
  -d '{"doctype_name": "Sales Order", "return_json": true, "level": 2}'
```

**Response**:
```json
{
  "success": true,
  "data": {...},
  "message": "Documentation generated for Sales Order"
}
```

---

### 3. Bulk Generate Documentation

**Endpoint**: `/api/method/doctype_explorer.explorer.bulk_generate_documentation`

**Method**: `POST`

**Authentication**: Frappe session

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `doctypes` | array | No* | List of DocType names |
| `module` | string | No* | Generate for all DocTypes in module |

*Either `doctypes` or `module` is required

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.bulk_generate_documentation" \
  -H "Content-Type: application/json" \
  -d '{"doctypes": ["Sales Order", "Purchase Order"]}'
```

**Response**:
```json
{
  "success": true,
  "results": [
    {"doctype": "Sales Order", "success": true, "file_path": "..."},
    {"doctype": "Purchase Order", "success": true, "file_path": "..."}
  ],
  "total": 2,
  "successful": 2
}
```

---

### 4. Compare DocTypes

**Endpoint**: `/api/method/doctype_explorer.explorer.compare_doctypes`

**Method**: `POST`

**Authentication**: Frappe session

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `doctype1` | string | Yes | First DocType name |
| `doctype2` | string | Yes | Second DocType name |

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.compare_doctypes" \
  -H "Content-Type: application/json" \
  -d '{"doctype1": "Sales Order", "doctype2": "Purchase Order"}'
```

**Response**:
```json
{
  "success": true,
  "comparison": {
    "doctype1": "Sales Order",
    "doctype2": "Purchase Order",
    "fields_only_in_dt1": ["field1", "field2"],
    "fields_only_in_dt2": ["field3", "field4"],
    "common_fields": ["name", "creation"],
    "field_type_differences": [...],
    "summary": {
      "total_fields_dt1": 45,
      "total_fields_dt2": 42,
      "common_fields_count": 35
    }
  }
}
```

---

### 5. Get DocType Dependencies

**Endpoint**: `/api/method/doctype_explorer.explorer.get_doctype_dependencies`

**Method**: `POST`

**Authentication**: Frappe session

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `doctype_name` | string | Yes | Name of the DocType |
| `depth` | integer | No | How many levels deep (default: 1) |

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_dependencies" \
  -H "Content-Type: application/json" \
  -d '{"doctype_name": "Sales Order", "depth": 2}'
```

**Response**:
```json
{
  "success": true,
  "dependencies": {
    "doctype": "Sales Order",
    "direct_links": [
      {"field": "customer", "linked_to": "Customer"},
      {"field": "company", "linked_to": "Company"}
    ],
    "child_tables": [
      {"field": "items", "child_doctype": "Sales Order Item"}
    ],
    "total_dependencies": 3,
    "nested_dependencies": {...}
  }
}
```

---

### 6. Export to HTML

**Endpoint**: `/api/method/doctype_explorer.explorer.export_to_html`

**Method**: `POST`

**Authentication**: Frappe session

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `doctype_name` | string | Yes | Name of the DocType |

**Example**:
```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.export_to_html" \
  -H "Content-Type: application/json" \
  -d '{"doctype_name": "Sales Order"}'
```

**Response**: Path to HTML file
```
/path/to/site/public/files/doctype_docs/Sales_Order.html
```

---

## Response Format

### Success Response Structure

```json
{
  "success": true,
  "data": {
    "doctype_name": "DocType Name",
    "module": "Module Name",
    "fields": [...],
    "linked_doctypes": {...},
    "child_tables": {...},
    "permissions": [...],
    "meta_info": {...}
  },
  "message": "Success message",
  "doctype_name": "DocType Name",
  "level": 2
}
```

### Error Response Structure

```json
{
  "success": false,
  "message": "Error message",
  "error": "Error type"
}
```

---

## Common Use Cases

### Get Formatted JSON for a DocType

```bash
curl -X GET "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_api?AUTH-KEY=key&doctype_name=Item&level=1" | jq '.'
```

### Save Documentation to File

```bash
curl -X GET "http://your-site.com/api/method/doctype_explorer.explorer.get_doctype_api?AUTH-KEY=key&doctype_name=Customer&level=0" > customer_docs.json
```

### Generate Documentation for All DocTypes in a Module

```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.bulk_generate_documentation" \
  -H "Content-Type: application/json" \
  -d '{"module": "Selling"}'
```

### Compare Two Similar DocTypes

```bash
curl -X POST "http://your-site.com/api/method/doctype_explorer.explorer.compare_doctypes" \
  -H "Content-Type: application/json" \
  -d '{"doctype1": "Sales Invoice", "doctype2": "Purchase Invoice"}' | jq '.comparison.summary'
```

---

## Notes

- **Level Parameter**: 
  - `0` = Infinite depth (explore all linked DocTypes recursively)
  - `1+` = Limited depth (stop after N levels)
  
- **URL Encoding**: Remember to URL-encode DocType names with spaces:
  - `Sales Order` → `Sales%20Order`
  
- **Formatted JSON**: The `get_doctype_api` endpoint returns formatted JSON with 2-space indentation for readability.

- **File Locations**: Generated files are saved to:
  - JSON: `sites/{site}/public/files/doctype_docs/{doctype_name}.json`
  - HTML: `sites/{site}/public/files/doctype_docs/{doctype_name}.html`

