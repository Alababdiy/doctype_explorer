import os
import json
from datetime import datetime

import frappe
from frappe.model.meta import get_meta
from werkzeug.wrappers import Response


def generate_doctype_json(
    doctype_name,
    output_path=None,
    processed_doctypes=None,
    include_nested_links=True,
    max_depth=3,
    current_depth=0,
):
    """
    Generate comprehensive JSON documentation for a DocType including all linked
    DocTypes and child tables.

    Args:
        doctype_name (str): Name of the DocType to document
        output_path (str | bool | None): Path to save JSON. If False, do not save.
        processed_doctypes (set | None): Track already processed doctypes
        include_nested_links (bool): Whether to include nested link documentation
        max_depth (int): Maximum recursion depth for nested links
        current_depth (int): Current recursion depth

    Returns:
        dict: Complete DocType structure as dictionary
    """
    if processed_doctypes is None:
        processed_doctypes = set()

    # Prevent infinite recursion for circular references
    if doctype_name in processed_doctypes or current_depth >= max_depth:
        return {
            "_circular_reference": True,
            "doctype": doctype_name,
            "depth_exceeded": current_depth >= max_depth,
        }

    processed_doctypes.add(doctype_name)

    # Get DocType metadata
    try:
        meta = get_meta(doctype_name)
    except Exception as e:  # noqa: BLE001 - bubble as Frappe error message
        frappe.throw(f"Error getting metadata for DocType '{doctype_name}': {str(e)}")

    # Build main structure
    doctype_structure = {
        "doctype_name": doctype_name,
        "module": meta.module,
        "is_submittable": meta.is_submittable,
        "is_child_table": meta.istable,
        "track_changes": meta.track_changes,
        "allow_rename": meta.allow_rename,
        "allow_import": meta.allow_import,
        "is_tree": meta.is_tree,
        "editable_grid": meta.editable_grid,
        "quick_entry": meta.quick_entry,
        "title_field": meta.title_field,
        "image_field": meta.image_field,
        "description": meta.description or "",
        "generated_at": datetime.now().isoformat(),
        "fields": [],
        "linked_doctypes": {},
        "child_tables": {},
        "permissions": [],
        "naming_rule": meta.autoname or "Prompt",
        "sort_field": getattr(meta, "sort_field", None),
        "sort_order": getattr(meta, "sort_order", None),
        "meta_info": {
            "total_fields": len(meta.fields),
            "link_fields_count": 0,
            "child_table_count": 0,
            "required_fields_count": 0,
        },
    }

    # Collect all fields
    link_fields = []
    child_table_fields = []

    for field in meta.fields:
        field_data = {
            "fieldname": field.fieldname,
            "label": field.label,
            "fieldtype": field.fieldtype,
            "options": field.options,
            "required": bool(field.reqd),
            "read_only": bool(field.read_only),
            "in_list_view": bool(field.in_list_view),
            "in_standard_filter": bool(field.in_standard_filter),
            "in_global_search": bool(field.in_global_search),
            "bold": bool(field.bold),
            "hidden": bool(field.hidden),
            "print_hide": bool(field.print_hide),
            "unique": bool(field.unique),
            "description": field.description or "",
            "default": field.default or "",
            "length": field.length or 0,
            "precision": field.precision or "",
            "depends_on": field.depends_on or "",
        }

        # Update meta info counts
        if field.reqd:
            doctype_structure["meta_info"]["required_fields_count"] += 1

        doctype_structure["fields"].append(field_data)

        # Track Link and Table fields for detailed documentation
        if field.fieldtype == "Link" and field.options:
            doctype_structure["meta_info"]["link_fields_count"] += 1
            link_fields.append(
                {
                    "field_name": field.fieldname,
                    "label": field.label,
                    "linked_doctype": field.options,
                }
            )
        elif field.fieldtype == "Table" and field.options:
            doctype_structure["meta_info"]["child_table_count"] += 1
            child_table_fields.append(
                {
                    "field_name": field.fieldname,
                    "label": field.label,
                    "child_doctype": field.options,
                }
            )

    # Document Link fields
    for link in link_fields:
        try:
            linked_meta = get_meta(link["linked_doctype"])
            linked_structure = {
                "doctype_name": link["linked_doctype"],
                "field_reference": link["field_name"],
                "label": link["label"],
                "fields": [],
            }

            for lf in linked_meta.fields:
                linked_structure["fields"].append(
                    {
                        "fieldname": lf.fieldname,
                        "label": lf.label,
                        "fieldtype": lf.fieldtype,
                        "options": lf.options,
                        "required": bool(lf.reqd),
                    }
                )

            doctype_structure["linked_doctypes"][link["field_name"]] = linked_structure
        except Exception as e:  # noqa: BLE001
            doctype_structure["linked_doctypes"][link["field_name"]] = {
                "error": str(e),
                "doctype_name": link["linked_doctype"],
            }

    # Document Child Table fields
    for child in child_table_fields:
        try:
            child_meta = get_meta(child["child_doctype"])
            child_structure = {
                "doctype_name": child["child_doctype"],
                "field_reference": child["field_name"],
                "label": child["label"],
                "fields": [],
                "nested_links": {},
            }

            nested_links = []
            for cf in child_meta.fields:
                field_info = {
                    "fieldname": cf.fieldname,
                    "label": cf.label,
                    "fieldtype": cf.fieldtype,
                    "options": cf.options,
                    "required": bool(cf.reqd),
                    "description": cf.description or "",
                }
                child_structure["fields"].append(field_info)

                # Track nested links
                if cf.fieldtype == "Link" and cf.options:
                    nested_links.append(
                        {
                            "fieldname": cf.fieldname,
                            "label": cf.label,
                            "linked_doctype": cf.options,
                        }
                    )

            # Document nested links in child tables
            for nl in nested_links:
                try:
                    nested_meta = get_meta(nl["linked_doctype"])
                    nested_structure = {
                        "doctype_name": nl["linked_doctype"],
                        "field_reference": nl["fieldname"],
                        "label": nl["label"],
                        "fields": [],
                    }

                    for nf in nested_meta.fields:
                        nested_structure["fields"].append(
                            {
                                "fieldname": nf.fieldname,
                                "label": nf.label,
                                "fieldtype": nf.fieldtype,
                                "options": nf.options,
                            }
                        )

                    child_structure["nested_links"][nl["fieldname"]] = nested_structure
                except Exception as e:  # noqa: BLE001
                    child_structure["nested_links"][nl["fieldname"]] = {"error": str(e)}

            doctype_structure["child_tables"][child["field_name"]] = child_structure
        except Exception as e:  # noqa: BLE001
            doctype_structure["child_tables"][child["field_name"]] = {
                "error": str(e),
                "doctype_name": child["child_doctype"],
            }

    # Add permissions info
    if getattr(meta, "permissions", None):
        for perm in meta.permissions:
            doctype_structure["permissions"].append(
                {
                    "role": perm.role,
                    "read": bool(perm.read),
                    "write": bool(perm.write),
                    "create": bool(perm.create),
                    "delete": bool(perm.delete),
                    "submit": bool(perm.submit),
                    "cancel": bool(perm.cancel),
                    "amend": bool(perm.amend),
                }
            )

    # Save to file if output path specified or use default (None)
    if output_path or output_path is None:
        if not output_path:
            site_path = frappe.get_site_path()
            output_dir = os.path.join(site_path, "public", "files", "doctype_docs")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{doctype_name.replace(' ', '_')}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doctype_structure, f, indent=2, ensure_ascii=False)

        frappe.msgprint(f"Documentation generated successfully at: {output_path}")

    return doctype_structure


@frappe.whitelist()
def generate_doctype_documentation(doctype_name, return_json=False, level=0):
    """
    Whitelisted method to generate DocType documentation.
    Can be called from the frontend or bench command.

    Args:
        doctype_name (str): Name of the DocType to document
        return_json (bool): If True, return JSON structure instead of saving to file
        level (int): Maximum recursion depth for nested links (0 for infinite)

    Returns:
        dict: Result with file path/data and status
    """
    try:
        level = frappe.parse_json(level) if isinstance(level, str) else level
        max_depth = level if level > 0 else float('inf')

        if frappe.utils.cstr(return_json).lower() in {"true", "1"}:
            structure = generate_doctype_json(doctype_name, output_path=False, max_depth=max_depth)
            return {
                "success": True,
                "data": structure,
                "message": f"Documentation generated for {doctype_name}",
            }
        else:
            _ = generate_doctype_json(doctype_name, max_depth=max_depth)
            site_path = frappe.get_site_path()
            file_path = os.path.join(
                site_path,
                "public",
                "files",
                "doctype_docs",
                f"{doctype_name.replace(' ', '_')}.json",
            )
            return {
                "success": True,
                "file_path": file_path,
                "message": f"Documentation generated for {doctype_name}",
            }
    except Exception as e:  # noqa: BLE001
        frappe.log_error(f"Error generating documentation for {doctype_name}: {str(e)}")
        return {"success": False, "message": str(e)}


def document_doctype(doctype_name):
    """
    Console/Bench command wrapper for generating DocType documentation.
    Usage: bench --site [sitename] console
    Then: document_doctype("Sales Order")
    """
    result = generate_doctype_json(doctype_name)
    print(json.dumps(result, indent=2))
    return result


def execute_from_bench(doctype_name):
    """
    Direct execution from bench execute command.
    Usage: bench --site [sitename] execute doctype_explorer.explorer.execute_from_bench --args "['Sales Order']"
    """
    return generate_doctype_json(doctype_name)


@frappe.whitelist()
def bulk_generate_documentation(doctypes=None, module=None):
    """
    Generate documentation for multiple DocTypes at once.

    Args:
        doctypes (list | None): List of DocType names (if None, uses module filter)
        module (str | None): Generate for all DocTypes in a module

    Returns:
        dict: Results for all DocTypes
    """
    results = []

    if module:
        # Get all DocTypes in module
        doctypes = frappe.get_all("DocType", filters={"module": module}, pluck="name")

    if not doctypes:
        return {"success": False, "message": "No DocTypes specified"}

    for dt in doctypes:
        try:
            result = generate_doctype_documentation(dt)
            results.append(
                {
                    "doctype": dt,
                    "success": result["success"],
                    "file_path": result.get("file_path", ""),
                }
            )
        except Exception as e:  # noqa: BLE001
            results.append({"doctype": dt, "success": False, "error": str(e)})

    return {
        "success": True,
        "results": results,
        "total": len(doctypes),
        "successful": len([r for r in results if r["success"]]),
    }


@frappe.whitelist()
def compare_doctypes(doctype1, doctype2):
    """
    Compare two DocTypes and find differences.

    Args:
        doctype1 (str): First DocType name
        doctype2 (str): Second DocType name

    Returns:
        dict: Comparison results
    """
    try:
        dt1_data = generate_doctype_json(doctype1, output_path=False)
        dt2_data = generate_doctype_json(doctype2, output_path=False)

        # Compare fields
        fields1 = {f["fieldname"]: f for f in dt1_data["fields"]}
        fields2 = {f["fieldname"]: f for f in dt2_data["fields"]}

        comparison = {
            "doctype1": doctype1,
            "doctype2": doctype2,
            "fields_only_in_dt1": list(set(fields1.keys()) - set(fields2.keys())),
            "fields_only_in_dt2": list(set(fields2.keys()) - set(fields1.keys())),
            "common_fields": list(set(fields1.keys()) & set(fields2.keys())),
            "field_type_differences": [],
            "summary": {
                "total_fields_dt1": len(fields1),
                "total_fields_dt2": len(fields2),
                "common_fields_count": len(set(fields1.keys()) & set(fields2.keys())),
            },
        }

        # Check field type differences in common fields
        for fieldname in comparison["common_fields"]:
            if fields1[fieldname]["fieldtype"] != fields2[fieldname]["fieldtype"]:
                comparison["field_type_differences"].append(
                    {
                        "fieldname": fieldname,
                        "type_in_dt1": fields1[fieldname]["fieldtype"],
                        "type_in_dt2": fields2[fieldname]["fieldtype"],
                    }
                )

        return {"success": True, "comparison": comparison}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_doctype_dependencies(doctype_name, depth=1):
    """
    Get all DocTypes that this DocType depends on (via Links and Tables).

    Args:
        doctype_name (str): DocType name
        depth (int): How many levels deep to search

    Returns:
        dict: Dependency tree
    """
    try:
        meta = get_meta(doctype_name)
        dependencies = {
            "doctype": doctype_name,
            "direct_links": [],
            "child_tables": [],
            "total_dependencies": 0,
        }

        # Get direct links
        for field in meta.fields:
            if field.fieldtype == "Link" and field.options:
                dependencies["direct_links"].append(
                    {"field": field.fieldname, "linked_to": field.options}
                )
            elif field.fieldtype == "Table" and field.options:
                dependencies["child_tables"].append(
                    {"field": field.fieldname, "child_doctype": field.options}
                )

        dependencies["total_dependencies"] = len(dependencies["direct_links"]) + len(
            dependencies["child_tables"]
        )

        # Recursive dependencies if depth > 1
        if int(depth) > 1:
            nested_deps = {}
            for link in dependencies["direct_links"]:
                nested_deps[link["linked_to"]] = get_doctype_dependencies(
                    link["linked_to"], int(depth) - 1
                )
            dependencies["nested_dependencies"] = nested_deps

        return {"success": True, "dependencies": dependencies}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def export_to_html(doctype_name):
    """
    Export DocType documentation as a formatted HTML file.

    Args:
        doctype_name (str): DocType name

    Returns:
        str: Path to HTML file
    """
    data = generate_doctype_json(doctype_name, output_path=False)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{doctype_name} Documentation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #3498db; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background: #f8f9fa; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
            .required {{ background: #e74c3c; color: white; }}
            .optional {{ background: #95a5a6; color: white; }}
            .meta-info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class=\"container\"> 
            <h1>{doctype_name}</h1>
            <div class=\"meta-info\">
                <p><strong>Module:</strong> {data['module']}</p>
                <p><strong>Submittable:</strong> {data['is_submittable']}</p>
                <p><strong>Total Fields:</strong> {data['meta_info']['total_fields']}</p>
                <p><strong>Required Fields:</strong> {data['meta_info']['required_fields_count']}</p>
                <p><strong>Generated:</strong> {data['generated_at']}</p>
            </div>

            <h2>Fields</h2>
            <table>
                <tr>
                    <th>Field Name</th>
                    <th>Label</th>
                    <th>Type</th>
                    <th>Linked DocType</th>
                    <th>Required</th>
                </tr>
    """

    for field in data["fields"]:
        required_badge = (
            '<span class="badge required">Required</span>'
            if field["required"]
            else '<span class="badge optional">Optional</span>'
        )
        linked_doctype_name = (
            field["options"] if field["fieldtype"] == "Link" and field["options"] else "-"
        )
        html += f"""
                <tr>
                    <td>{field['fieldname']}</td>
                    <td>{field['label']}</td>
                    <td>{field['fieldtype']}</td>
                    <td>{linked_doctype_name}</td>
                    <td>{required_badge}</td>
                </tr>
        """

    html += """
            </table>
        </div>
    </body>
    </html>
    """

    site_path = frappe.get_site_path()
    output_dir = os.path.join(site_path, "public", "files", "doctype_docs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{doctype_name.replace(' ', '_')}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


@frappe.whitelist(allow_guest=True)
def get_doctype_api():
    """
    API endpoint to get DocType documentation via GET request.
    Requires AUTH-KEY for authentication.
    
    GET Parameters:
        AUTH-KEY (str, required): Authentication key
        doctype_name (str, required): Name of the DocType to document
        level (int, optional): Maximum recursion depth (0 for infinite, default: 0)
    
    Headers (alternative):
        AUTH-KEY: Can be passed in headers instead of GET parameters
    
    Returns:
        dict: JSON response with DocType structure or error message
    
    Example:
        GET /api/method/doctype_explorer.explorer.get_doctype_api?AUTH-KEY=your_key&doctype_name=Sales Order&level=2
    """
    # Get AUTH-KEY from GET parameters or headers
    auth_key = frappe.form_dict.get('AUTH-KEY') or frappe.request.headers.get('AUTH-KEY')
    
    if not auth_key:
        frappe.throw(
            'AUTH-KEY is required. Please provide AUTH-KEY as GET parameter or in headers.',
            frappe.AuthenticationError
        )
    
    # Validate AUTH-KEY
    # Priority: Environment variable > Site config > System Settings custom field
    valid_auth_key = (
        os.environ.get('DOCTYPE_EXPLORER_AUTH_KEY') or
        frappe.conf.get('doctype_explorer_auth_key') or
        frappe.db.get_value('System Settings', 'System Settings', 'custom_doctype_explorer_auth_key')
    )
    
    # If no auth key is configured, throw error
    if not valid_auth_key:
        frappe.throw(
            'AUTH-KEY validation not configured. Please set doctype_explorer_auth_key in site config, '
            'environment variable DOCTYPE_EXPLORER_AUTH_KEY, or System Settings custom field.',
            frappe.AuthenticationError
        )
    
    if auth_key != valid_auth_key:
        frappe.throw('Invalid AUTH-KEY', frappe.AuthenticationError)
    
    # Get required parameters
    doctype_name = frappe.form_dict.get('doctype_name')
    if not doctype_name:
        frappe.throw('doctype_name is required as GET parameter', frappe.ValidationError)
    
    # Get optional parameters
    level = frappe.form_dict.get('level', 0)
    try:
        level = int(level) if level else 0
    except (ValueError, TypeError):
        level = 0
    
    # Generate documentation
    try:
        max_depth = level if level > 0 else float('inf')
        structure = generate_doctype_json(
            doctype_name,
            output_path=False,
            max_depth=max_depth
        )
        
        response_data = {
            'success': True,
            'data': structure,
            'message': f'Documentation generated for {doctype_name}',
            'doctype_name': doctype_name,
            'level': level
        }
        
        # Return formatted JSON response
        formatted_json = json.dumps(response_data, indent=2, ensure_ascii=False, default=str)
        response = Response(
            formatted_json,
            mimetype='application/json',
            status=200
        )
        return response
        
    except Exception as e:  # noqa: BLE001
        frappe.log_error(
            f"Error in get_doctype_api for {doctype_name}: {str(e)}",
            "DocType Explorer API Error"
        )
        error_data = {
            'success': False,
            'message': str(e),
            'error': 'Failed to generate documentation'
        }
        
        # Return formatted JSON response for errors too
        formatted_json = json.dumps(error_data, indent=2, ensure_ascii=False, default=str)
        response = Response(
            formatted_json,
            mimetype='application/json',
            status=500
        )
        return response
