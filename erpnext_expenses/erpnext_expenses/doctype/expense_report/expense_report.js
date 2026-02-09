// Copyright (c) 2024, Karani Geoffrey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Report", {
	refresh(frm) {
        // Show "Create Journal Entries" button only when approved and user has permission
        if (frm.doc.workflow_state === 'Approved' && frappe.user.has_role('Accounts User')) {
            frm.add_custom_button(__('Create Journal Entries'), function() {
                // Save first to persist paying_account to DB, then let server validate
                frm.save().then(() => {
                    frappe.call({
                        method: 'erpnext_expenses.erpnext_expenses.doctype.expense_report.expense_report.create_journal_entries',
                        args: {
                            'report': frm.doc.name
                        },
                        freeze: true,
                        freeze_message: __('Creating Journal Entry...'),
                        callback: function(r) {
                            if (r.message && r.message.response === 'Success') {
                                frappe.msgprint({
                                    title: __('Success'),
                                    indicator: 'green',
                                    message: __('Journal Entry {0} created successfully.', [r.message.journal_entry])
                                });
                                frm.reload_doc();
                            }
                        },
                        error: function(r) {
                            frappe.msgprint({
                                title: __('Error'),
                                indicator: 'red',
                                message: __('Failed to create journal entry. Check error logs for details.')
                            });
                        }
                    });
                });
            });
        }
	}

    // Journal creation is only triggered via the custom "Create Journal Entries" button
    // when state is 'Approved'. The workflow transition was removed to prevent state
    // changes without actual journal creation.
});
