// Copyright (c) 2024, Karani Geoffrey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense", {
	refresh: function(frm) {
        // Check if the workflow state is "pending_finance_approval"
        if (frm.doc.workflow_state === 'pending_finance_approval') {
            frm.toggle_display('paying_account', true);
        } else {
            frm.toggle_display('paying_account', false);
        }

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
