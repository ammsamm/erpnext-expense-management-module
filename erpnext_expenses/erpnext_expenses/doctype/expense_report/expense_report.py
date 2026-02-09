import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class ExpenseReport(Document):
    def on_update(self):
        """When report moves back to Draft, revert associated expenses to Draft."""
        if self.workflow_state == 'Draft':
            self.revert_expenses_to_draft()

    def revert_expenses_to_draft(self):
        """Revert associated expenses from Submitted back to Draft."""
        expense_details = frappe.db.get_all(
            'Expense Detail',
            filters={'parent': self.name},
            fields=['expense_id']
        )

        for detail in expense_details:
            expense_id = detail.expense_id
            current_docstatus = frappe.db.get_value('Expense', expense_id, 'docstatus')

            if current_docstatus == 1:
                # Direct update to revert docstatus
                # Required because Frappe doesn't support docstatus 1→0 via normal save
                frappe.db.set_value('Expense', expense_id, 'docstatus', 0)


@frappe.whitelist()
def create_journal_entries(report, paying_account=None):
    """Create journal entries for an expense report."""
    # Input validation
    if not report or not isinstance(report, str):
        frappe.throw('Invalid report parameter')

    # Verify user has write permission on the expense report
    if not frappe.has_permission('Expense Report', 'write', report):
        frappe.throw('You do not have permission to modify this expense report', frappe.PermissionError)

    try:
        fields = [
            'name',
            'company',
            'paying_account'
        ]

        expense_report = frappe.db.get_all(
            'Expense Report',
            filters={'name': report},
            fields=fields
        )

        if not expense_report:
            frappe.throw(f"Expense Report {report} not found")

        expense_report = expense_report[0]

        # Use paying_account passed from client, fall back to DB value
        if paying_account:
            expense_report.paying_account = paying_account
            # Persist to DB for future reference
            frappe.db.set_value('Expense Report', report, 'paying_account', paying_account)

        if not expense_report.paying_account:
            frappe.throw(
                'Please set the Paying Account before creating journal entries.',
                title='Missing Paying Account'
            )

        # Check for existing journal entries to prevent duplicates
        existing_jv = frappe.db.sql("""
            SELECT name FROM `tabJournal Entry`
            WHERE remark = %s
            AND docstatus = 1
            LIMIT 1
        """, (f'Expense Report: {report}',))

        if existing_jv:
            frappe.throw(
                f'Journal Entry {existing_jv[0][0]} already exists for this Expense Report.',
                title='Duplicate Journal Entry'
            )

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

                    if not tax_account:
                        frappe.throw(
                            f'Tax "{tax_exists.vat}" does not have a Tax Account configured. '
                            'Please set a Tax Account in the Expense Taxes master.',
                            title='Missing Tax Account'
                        )

                    if tax_account not in tax_amounts:
                        tax_amounts[tax_account] = 0
                    tax_amounts[tax_account] += tax_exists.vat_amount

                    # Track tax per expense for correct deduction
                    expense_tax_totals[expense_id] += tax_exists.vat_amount

        # Get the associated expense value from the expenses child table
        expense_details = frappe.db.get_all(
            'Expense Detail',
            filters={'parent': report},
            fields=['expense_id', 'subtotal', 'description', 'expense_date']
        )

        expense_total = sum(item.subtotal for item in expense_details)

        # FIX #6: Use the latest expense date as posting date
        expense_dates = [item.expense_date for item in expense_details if item.expense_date]
        posting_date = max(expense_dates) if expense_dates else nowdate()

        # Create the journal entries
        jv = frappe.new_doc('Journal Entry')
        jv.voucher_type = 'Journal Entry'
        jv.naming_series = 'ACC-JV-.YYYY.-'
        jv.posting_date = posting_date
        jv.company = expense_report.company
        jv.remark = f'Expense Report: {expense_report.name}'

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


def _update_report_workflow_state(report_name, target_state):
    """Update expense report workflow state via direct DB update.

    Args:
        report_name: Name of the Expense Report document
        target_state: Target workflow state name (e.g. 'Journals Created')
    """
    try:
        frappe.db.set_value('Expense Report', report_name, 'workflow_state', target_state)
    except Exception as e:
        frappe.log_error(f"Error updating expense report workflow state: {str(e)}")
        raise
