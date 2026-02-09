// Copyright (c) 2024, Karani Geoffrey and contributors
// For license information, please see license.txt

// Attachment configuration (must match server-side values)
const ATTACHMENT_CONFIG = {
    maxFiles: 5,
    maxFileSizeMB: 5,
    maxTotalSizeMB: 15,
    allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'doc', 'docx', 'xls', 'xlsx']
};

frappe.ui.form.on("Expense", {
	refresh: function(frm) {
        // paying_account is managed on Expense Report, hide on individual Expense form
        frm.toggle_display('paying_account', false);

        if (frm.doc.docstatus === 0 && !frm.is_new()) {
            frm.add_custom_button(__('Create Report'), function() {
                frappe.call({
                    method: 'erpnext_expenses.erpnext_expenses.doctype.expense.expense.create_expense_report',
                    args: {
                        'expense': frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Creating Expense Report...'),
                    callback: function(r) {
                        if (r.message && r.message.response === 'Success') {
                            frappe.set_route("Form", "Expense Report", r.message.expense);
                        } else {
                            frappe.msgprint({
                                title: __('Error'),
                                indicator: 'red',
                                message: r.message && r.message.message
                                    ? r.message.message
                                    : __('An error was encountered. Please see the error logs for details.')
                            });
                        }
                    }
                });
            });
        }

        // Show attachment limits info and view button
        updateAttachmentInfo(frm);
        setupAttachmentViewing(frm);
    },

    onload: function(frm) {
        if (frm.is_new()) {
            frappe.call({
                method: 'erpnext_expenses.erpnext_expenses.doctype.expense.expense.get_logged_in_employee',
                callback: function(response) {
                    if (response.message) {
                        frm.set_value('employee', response.message.employee);
                        frm.set_value('employee_name', response.message.employee_name);
                        frm.set_value('company', response.message.company);
                    }
                }
            });
        }

        // Lock employee and company fields for non-managers
        let is_manager = frappe.user.has_role('Accounts Manager') || frappe.user.has_role('System Manager');
        frm.set_df_property('employee', 'read_only', is_manager ? 0 : 1);
        frm.set_df_property('company', 'read_only', is_manager ? 0 : 1);
    },

    employee: function(frm) {
        // When manager changes employee, update company from that employee's record
        if (frm.doc.employee) {
            frappe.db.get_value('Employee', frm.doc.employee, ['employee_name', 'company'], function(r) {
                if (r) {
                    frm.set_value('employee_name', r.employee_name);
                    frm.set_value('company', r.company);
                }
            });
        }
    },

    validate: function(frm) {
        const total_expense_amount = frm.doc.total;
        calculateTotalAmount(frm, total_expense_amount);
        validateAttachments(frm);
    },

    table_jkwj_add: function(frm) {
        // Calculate running total when row is added to splitting table
        if (!frm.doc.table_jkwj) return;

        let total = 0;
        frm.doc.table_jkwj.forEach(function(row) {
            total += row.amount || 0;
        });
    },

    expense_date: function(frm) {
        if (frm.doc.expense_date > frappe.datetime.nowdate()) {
            frm.set_value('expense_date', '');
            frappe.throw(__('The expense date cannot be in the future.'));
        }
    }
});


// Attachment child table events
frappe.ui.form.on("Expense Attachment", {
    attachments_add: function(frm, cdt, cdn) {
        // Check if adding this row exceeds the limit
        if (frm.doc.attachments && frm.doc.attachments.length > ATTACHMENT_CONFIG.maxFiles) {
            frappe.model.clear_doc(cdt, cdn);
            frm.refresh_field('attachments');
            frappe.msgprint({
                title: __('Attachment Limit Reached'),
                indicator: 'orange',
                message: __('Maximum {0} attachments allowed per expense.', [ATTACHMENT_CONFIG.maxFiles])
            });
        }
        updateAttachmentInfo(frm);
    },

    attachments_remove: function(frm) {
        updateAttachmentInfo(frm);
    },

    form_render: function(frm, cdt, cdn) {
        // Add view button when child table row is expanded
        const row = locals[cdt][cdn];
        if (!row.attachment) return;

        const grid_row = frm.fields_dict.attachments.grid.grid_rows_by_docname[cdn];
        if (!grid_row || !grid_row.grid_form) return;

        const $form = $(grid_row.grid_form.wrapper);
        $form.find('.btn-view-attachment').remove();

        const $btn = $(`<button class="btn btn-xs btn-primary btn-view-attachment"
            style="margin-top: 8px; margin-bottom: 8px;">
            <i class="fa fa-eye"></i> ${__('View Attachment')}
        </button>`);

        $btn.on('click', function(e) {
            e.stopPropagation();
            openAttachment(row.attachment, row.file_name);
        });

        $form.find('.frappe-control[data-fieldname="attachment"]').append($btn);
    },

    attachment: function(frm, cdt, cdn) {
        // Validate file when attached
        const row = locals[cdt][cdn];
        if (!row.attachment) return;

        const fileName = row.attachment.split('/').pop();
        const extension = fileName.split('.').pop().toLowerCase();

        // Validate extension
        if (!ATTACHMENT_CONFIG.allowedExtensions.includes(extension)) {
            frappe.model.set_value(cdt, cdn, 'attachment', '');
            frappe.msgprint({
                title: __('Invalid File Type'),
                indicator: 'red',
                message: __('File type ".{0}" is not allowed. Allowed types: {1}',
                    [extension, ATTACHMENT_CONFIG.allowedExtensions.join(', ')])
            });
            return;
        }

        // Auto-populate file name
        frappe.model.set_value(cdt, cdn, 'file_name', fileName);
        updateAttachmentInfo(frm);
    }
});


// Get the total in real time as it is added to the splitting child table
frappe.ui.form.on("Expense Splitting Detail", "amount", function(frm, cdt, cdn) {
    if (!frm.doc.table_jkwj) return;

    let split_total = 0;
    frm.doc.table_jkwj.forEach(function(item) {
        split_total += item.amount || 0;
    });

    frm.set_value('split_total', split_total);
});

frappe.ui.form.on("Expense Splitting Detail", "vat", function(frm, cdt, cdn) {
    const item = locals[cdt][cdn];

    if (item.vat) {
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Expense Taxes',
                name: item.vat
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    const vat_amount = (item.amount || 0) * (doc.tax_percentage || 0) / 100;
                    item.vat_amount = vat_amount;
                    frm.refresh_field('table_jkwj');
                }
            }
        });
    } else {
        item.vat_amount = 0;
        frm.refresh_field('table_jkwj');
    }
});


// Function to calculate total amount in the child table
function calculateTotalAmount(frm, total_expense_amount) {
    if (!frm.doc.table_jkwj || frm.doc.table_jkwj.length === 0) {
        return true;
    }

    let total_amount = 0;
    let hasValue = false;

    frm.doc.table_jkwj.forEach(function(item) {
        if (item.amount) {
            hasValue = true;
            total_amount += item.amount;
        }
    });

    if (hasValue && total_expense_amount !== total_amount) {
        frappe.throw(__("The split amount ({0}) does not match the expense total ({1}).",
            [total_amount, total_expense_amount]));
    }

    return true;
}


// Validate attachments before save
function validateAttachments(frm) {
    if (!frm.doc.attachments || frm.doc.attachments.length === 0) {
        return true;
    }

    // Check count
    if (frm.doc.attachments.length > ATTACHMENT_CONFIG.maxFiles) {
        frappe.throw(__('Maximum {0} attachments allowed. You have {1}.',
            [ATTACHMENT_CONFIG.maxFiles, frm.doc.attachments.length]));
    }

    // Validate each attachment
    frm.doc.attachments.forEach(function(row, idx) {
        if (!row.attachment) return;

        const fileName = row.attachment.split('/').pop();
        const extension = fileName.split('.').pop().toLowerCase();

        if (!ATTACHMENT_CONFIG.allowedExtensions.includes(extension)) {
            frappe.throw(__('Attachment #{0}: File type ".{1}" is not allowed.',
                [idx + 1, extension]));
        }
    });

    return true;
}


// Setup attachment viewing: add "View Attachments" button on form
function setupAttachmentViewing(frm) {
    const attachments = (frm.doc.attachments || []).filter(function(a) { return a.attachment; });
    if (!attachments.length || frm.is_new()) return;

    frm.add_custom_button(__('View Attachments'), function() {
        showAttachmentsGallery(frm);
    });
}


// Open a single attachment: image preview dialog or new tab for other files
function openAttachment(url, fileName) {
    const name = fileName || url.split('/').pop();
    const ext = name.split('.').pop().toLowerCase();
    const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp'];

    if (imageTypes.includes(ext)) {
        const d = new frappe.ui.Dialog({
            title: name,
            fields: [{
                fieldtype: 'HTML',
                fieldname: 'preview',
                options: '<div style="text-align: center;">'
                    + '<img src="' + url + '" style="max-width: 100%; max-height: 70vh;">'
                    + '</div>'
            }],
            primary_action_label: __('Open in New Tab'),
            primary_action: function() {
                window.open(url, '_blank');
            }
        });
        d.show();
        d.$wrapper.find('.modal-dialog').css('max-width', '800px');
    } else {
        window.open(url, '_blank');
    }
}


// Show gallery dialog with all attachments
function showAttachmentsGallery(frm) {
    const attachments = (frm.doc.attachments || []).filter(function(a) { return a.attachment; });
    if (!attachments.length) {
        frappe.msgprint(__('No attachments found.'));
        return;
    }

    const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
    let html = '';

    attachments.forEach(function(att, idx) {
        const url = att.attachment;
        const fileName = att.file_name || url.split('/').pop();
        const ext = fileName.split('.').pop().toLowerCase();
        const isImage = imageTypes.includes(ext);
        const iconClass = isImage ? 'fa-image' : (ext === 'pdf' ? 'fa-file-pdf-o' : 'fa-file-o');

        html += '<div style="margin-bottom: 12px; padding: 10px; border: 1px solid var(--border-color); border-radius: 4px;">';

        if (isImage) {
            html += '<div style="text-align: center; margin-bottom: 8px;">'
                + '<a href="' + url + '" target="_blank">'
                + '<img src="' + url + '" style="max-width: 100%; max-height: 200px; border-radius: 4px; cursor: pointer;">'
                + '</a></div>';
        }

        html += '<div style="display: flex; align-items: center; gap: 8px;">'
            + '<i class="fa ' + iconClass + '"></i> '
            + '<a href="' + url + '" target="_blank" style="font-weight: 500;">'
            + frappe.utils.escape_html(fileName)
            + '</a></div>';

        if (att.description) {
            html += '<div style="color: var(--text-muted); font-size: 12px; margin-top: 4px;">'
                + frappe.utils.escape_html(att.description)
                + '</div>';
        }

        html += '</div>';
    });

    const d = new frappe.ui.Dialog({
        title: __('Attachments ({0})', [attachments.length]),
        fields: [{
            fieldtype: 'HTML',
            fieldname: 'gallery',
            options: html
        }],
        size: 'large'
    });
    d.show();
}


// Update attachment info display
function updateAttachmentInfo(frm) {
    const count = (frm.doc.attachments || []).filter(a => a.attachment).length;
    const remaining = ATTACHMENT_CONFIG.maxFiles - count;

    // Update section label with count
    const section = frm.get_field('attachments_section');
    if (section) {
        const label = count > 0
            ? __('Invoice Attachments ({0}/{1})', [count, ATTACHMENT_CONFIG.maxFiles])
            : __('Invoice Attachments');
        section.df.label = label;
        section.refresh();
    }

    // Show warning if near limit
    if (remaining === 1) {
        frm.dashboard.set_headline_alert(
            __('You can add 1 more attachment.'),
            'orange'
        );
    } else if (remaining === 0) {
        frm.dashboard.set_headline_alert(
            __('Maximum attachments reached ({0} files).', [ATTACHMENT_CONFIG.maxFiles]),
            'red'
        );
    } else {
        frm.dashboard.clear_headline();
    }
}
