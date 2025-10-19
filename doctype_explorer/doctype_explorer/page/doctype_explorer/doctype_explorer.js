frappe.pages['doctype_explorer'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('DocType Explorer'),
        single_column: true
    });

    const $container = $(wrapper).find('.layout-main-section');
    $container.empty();

    const html = `
    <div class="dt-explorer frappe-card" style="padding:20px;">
      <div class="form-group" style="margin-bottom: 16px;">
        <label class="control-label">${__('DocType Name')}</label>
        <div id="dt-name-wrapper" style="max-width: 280px;"></div>
      </div>
      <div class="form-group" style="margin-bottom: 16px;">
        <label class="control-label">${__('Level (0 for infinite)')}</label>
        <div id="dt-level-wrapper" style="max-width: 280px;"></div>
      </div>
      <div class="form-group">
        <button class="btn btn-primary" id="btn-generate-json">${__('Generate JSON')}</button>
        <button class="btn btn-default" id="btn-copy-json">${__('Copy JSON')}</button>
        <button class="btn btn-default" id="btn-export-html">${__('Export HTML')}</button>
      </div>
      <pre id="json-output" style="white-space: pre-wrap; background: var(--background-color-light); padding:12px; border-radius:4px; border:1px solid var(--border-color); max-height: 50vh; overflow:auto;"></pre>
    </div>
  `;

    $container.append(html);

    const $name_wrapper = $container.find('#dt-name-wrapper');
    const $level_wrapper = $container.find('#dt-level-wrapper');
    const $output = $container.find('#json-output');

    let doctype_name_control = frappe.ui.form.make_control({
        parent: $name_wrapper,
        df: {
            fieldtype: 'Link',
            fieldname: 'doctype_name',
            options: 'DocType',
            placeholder: __('Enter DocType name')
        },
        render_input: true
    });
    doctype_name_control.refresh();

    let level_control = frappe.ui.form.make_control({
        parent: $level_wrapper,
        df: {
            fieldtype: 'Int',
            fieldname: 'level',
            default: 0,
            placeholder: __('Enter level (0 for infinite)')
        },
        render_input: true
    });
    level_control.refresh();

    function getName() {
        return doctype_name_control.get_value() || '';
    }

    function getLevel() {
        return level_control.get_value() || 0;
    }

    function notifyError(msg) {
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: msg
        });
    }

    $container.find('#btn-generate-json').on('click', function() {
        const name = getName();
        const level = getLevel();
        if (!name) { return notifyError(__('Please enter a DocType name.')); }
        frappe.call({
            method: 'doctype_explorer.explorer.generate_doctype_documentation',
            args: { doctype_name: name, return_json: true, level: level },
            freeze: true,
            callback: (r) => {
                if (r && r.message && r.message.success) {
                    $output.text(JSON.stringify(r.message.data, null, 2));
                } else {
                    notifyError((r && r.message && r.message.message) || __('Failed to generate'));
                }
            }
        });
    });

    $container.find('#btn-copy-json').on('click', function() {
        const text = $output.text();
        if (!text) { return notifyError(__('No JSON to copy.')); }
        navigator.clipboard.writeText(text).then(() => {
            frappe.show_alert({ message: __('Copied to clipboard'), indicator: 'green' });
        }).catch(() => notifyError(__('Clipboard failed')));
    });

    $container.find('#btn-export-html').on('click', function() {
        const name = getName();
        if (!name) { return notifyError(__('Please enter a DocType name.')); }
        frappe.call({
            method: 'doctype_explorer.explorer.export_to_html',
            args: { doctype_name: name },
            freeze: true,
            callback: (r) => {
                // export_to_html returns a path string directly, so r.message is the path
                const path = r && r.message;
                if (path) {
                    frappe.show_alert({ message: __('HTML exported: ') + path, indicator: 'green' });
                    window.open('/files/doctype_docs/' + name.replace(/\s+/g, '_') + '.html', '_blank');
                } else {
                    notifyError(__('Failed to export HTML'));
                }
            }
        });
    });
};
