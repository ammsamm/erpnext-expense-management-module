import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from frappe.utils import nowdate


class ExpenseReport(Document):
    pass


@frappe.whitelist()
def create_journal_entries(report):
    """Create journal entries for an expense report."""
    # Input validation
    if not report or not isinstance(report, str):
        frappe.throw('Invalid report parameter')

    # Verify user has write permission on the expense report
    if not frappe.has_permission('Expense Report', 'write', report):
        frappe.throw('You do not have permission to modify this expense report', frappe.PermissionError)

    try:
        fields = [
            'company',
            'paying_account',
            'description'
        ]

        expense_report = frappe.db.get_all(
            'Expense Report',
            filters={'name': report},
            fields=fields
        )

        if not expense_report:
            frappe.throw(f"Expense Report {report} not found")

        expense_report = expense_report[0]

        # Get all the expense IDs for the expenses in the report
        report_expenses = frappe.db.get_all(
            'Expense Detail',
            filters={'parent': report},
            fields=['expense_id']
        )

        # Dictionary to store tax amounts for each tax type
        tax_amounts = {}

        # Dictionary to store tax amounts per expense (for correct deduction)
        expense_tax_totals = {}

        # Iterate through each expense to calculate tax amounts
        for report_expense in report_expenses:
            expense_id = report_expense.expense_id
            expense_tax_totals[expense_id] = 0

            expense_vat = frappe.db.get_all(
                'Expense Splitting Detail',
                filters={'parent': expense_id},
                fields=['vat', 'vat_amount']
            )

            for tax_exists in expense_vat:
                if tax_exists.vat_amount and tax_exists.vat_amount > 0:
                    # Get the tax account associated with the tax found
                    tax_account = frappe.db.get_value(
                        'Expense Taxes',
                        tax_exists.vat,
                        'tax_account'
                    )

                    if tax_account:
                        # Add tax amount to the corresponding tax type in the dictionary
                        if tax_account not in tax_amounts:
                            tax_amounts[tax_account] = 0
                        tax_amounts[tax_account] += tax_exists.vat_amount

                        # Track tax per expense for correct deduction
                        expense_tax_totals[expense_id] += tax_exists.vat_amount

        # Get the associated expense value from the expenses child table
        expense_details = frappe.db.get_all(
            'Expense Detail',
            filters={'parent': report},
            fields=['expense_id', 'subtotal', 'description']
        )

        expense_total = sum(item.subtotal for item in expense_details)

        # Create the journal entries
        jv = frappe.new_doc('Journal Entry')
        jv.voucher_type = 'Journal Entry'
        jv.naming_series = 'ACC-JV-.YYYY.-'
        jv.posting_date = nowdate()
        jv.company = expense_report.company
        jv.remark = expense_report.description or ''

        # Entry to the Credit Side
        jv.append('accounts', {
            'account': expense_report.paying_account,
            'credit': float(expense_total),
            'debit': float(0),
            'debit_in_account_currency': float(0),
            'credit_in_account_currency': float(expense_total),
        })

        # Entry to the Debit Side for each expense category
        # Using parameterized query to prevent SQL injection
        expense_account_sql = """
            SELECT
                ec.expense_account,
                ed.subtotal,
                ed.expense_id
            FROM
                `tabExpense Category` ec
            JOIN
                `tabExpense` e
            ON
                ec.name = e.category
            JOIN
                `tabExpense Detail` ed
            ON
                e.name = ed.expense_id
            WHERE
                ed.parent = %s
        """

        expense_accounts = frappe.db.sql(expense_account_sql, (report,), as_dict=True)

        for acc in expense_accounts:
            # Deduct only the tax for THIS specific expense, not all taxes
            expense_tax = expense_tax_totals.get(acc.expense_id, 0)
            amount_less_tax = acc.subtotal - expense_tax

            # Entry to the Debit Side
            jv.append('accounts', {
                'account': acc.expense_account,
                'debit': float(amount_less_tax),
                'credit': float(0),
                'credit_in_account_currency': float(0),
                'debit_in_account_currency': float(amount_less_tax)
            })

        # Entry to the tax accounts
        for tax_account, tax_amount in tax_amounts.items():
            jv.append('accounts', {
                'account': tax_account,
                'debit': float(tax_amount),
                'credit': float(0),
                'credit_in_account_currency': float(0),
                'debit_in_account_currency': float(tax_amount)
            })

        jv.save()
        jv.submit()

        # Change the workflow state of the Expense Report
        _update_report_workflow_state(report, 'Journals Created')

        frappe.db.commit()

        return {'response': 'Success', 'journal_entry': jv.name}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error creating journal entries: {str(e)}")
        frappe.throw(f"Error creating journal entries: {str(e)}")


def _update_report_workflow_state(report_name, state):
    """Update expense report workflow state using proper workflow API."""
    try:
        doc = frappe.get_doc('Expense Report', report_name)
        try:
            apply_workflow(doc, state)
        except Exception:
            # Fallback to direct assignment if workflow action doesn't exist
            doc.workflow_state = state
            doc.save()
    except Exception as e:
        frappe.log_error(f"Error updating expense report workflow state: {str(e)}")
        raise
