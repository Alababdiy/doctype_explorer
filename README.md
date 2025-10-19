## DocType Explorer for Frappe

Utilities to explore Frappe DocTypes, generate JSON/HTML documentation, compare two DocTypes, and inspect dependencies.

### Install in Bench

```bash
bench get-app https://github.com/Alababdiy/doctype-explorer.git.
bench --site your.local install-app doctype_explorer
bench build && bench restart
```

### Desk Page

- Open the "DocType Explorer" page from the Desk.
- Actions: Generate JSON, Copy JSON, Export HTML for any DocType.

### Whitelisted APIs

- `doctype_explorer.explorer.generate_doctype_documentation(doctype_name, return_json=False)`
- `doctype_explorer.explorer.bulk_generate_documentation(doctypes=None, module=None)`
- `doctype_explorer.explorer.compare_doctypes(doctype1, doctype2)`
- `doctype_explorer.explorer.get_doctype_dependencies(doctype_name, depth=1)`

#### License

MIT