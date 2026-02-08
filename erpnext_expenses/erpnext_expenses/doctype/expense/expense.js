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

        if (frm.doc.workflow_state === 'Draft') {
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

        // Show attachment limits info
        updateAttachmentInfo(frm);
    },

    onload: function(frm) {
        if (frm.is_new()) {
            frappe.call({
                method: 'erpnext_expenses.erpnext_expenses.doctype.expense.expense.get_logged_in_employee',
                callback: function(response) {
                    if (response.message) {
                        frm.set_value('employee', response.message.employee);
                        frm.set_value('employee_name', response.message.employee_name);
                    }
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
