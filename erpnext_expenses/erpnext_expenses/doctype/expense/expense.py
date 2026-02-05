# Copyright (c) 2024, Karani Geoffrey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
import json


class Expense(Document):
	pass


@frappe.whitelist()
def get_logged_in_employee():
	"""Get the employee record associated with the logged-in user."""
	try:
		user = frappe.session.user

		# Use get_value with as_dict for safer handling
		employee_data = frappe.db.get_value(
			'Employee',
			{'user_id': user},
			['name', 'employee_name'],
			as_dict=True
		)

		if not employee_data:
			return None

		return {
			'employee': employee_data.name,
			'employee_name': employee_data.employee_name
		}

	except Exception as e:
		frappe.log_error(f"Error getting logged in employee: {str(e)}")
		return None


@frappe.whitelist()
def create_expense_report(expense, details=None):
	"""Create an expense report from one or more expenses."""
	# Input validation
	if not expense or not isinstance(expense, str):
		return {'response': 'Error', 'message': 'Invalid expense parameter'}

	# Verify user has read permission on the expense
	if not frappe.has_permission('Expense', 'read', expense):
		frappe.throw('You do not have permission to access this expense', frappe.PermissionError)

	report = None

	try:
		fields = [
			'expense_description',
			'category',
			'total',
			'employee',
			'expense_date',
			'company',
			'paid_by'
		]

		# Get the data from the Expense doctype
		expense_data = frappe.db.get_all('Expense', filters={'name': expense}, fields=fields)

		if not expense_data:
			return {'response': 'Error', 'message': 'Expense not found'}

		expense_data = expense_data[0]

		# Create a record in the Expense report doctype
		report = frappe.get_doc({
			'doctype': 'Expense Report',
			'employee': expense_data.employee,
			'paid_by': expense_data.paid_by,
			'company': expense_data.company,
		})
		report.insert()

		if details:
			for detail in details:
				report_detail = frappe.get_doc({
					'doctype': 'Expense Detail',
					'parent': report.name,
					'parentfield': 'expense',
					'parenttype': 'Expense Report',
					'expense_id': detail.get('expense_id'),
					'expense_date': detail.get('expense_date'),
					'category': detail.get('category'),
					'description': detail.get('description'),
					'subtotal': detail.get('subtotal')
				})
				report_detail.insert()

				# Change the workflow state of the Expense using proper workflow API
				_update_expense_workflow_state(detail.get('expense_id'), 'Submitted')
		else:
			report_detail = frappe.get_doc({
				'doctype': 'Expense Detail',
				'parent': report.name,
				'parentfield': 'expense',
				'parenttype': 'Expense Report',
				'expense_id': expense,
				'expense_date': expense_data.expense_date,
				'category': expense_data.category,
				'description': expense_data.expense_description,
				'subtotal': expense_data.total
			})
			report_detail.insert()

			# Change the workflow state of the Expense using proper workflow API
			_update_expense_workflow_state(expense, 'Submitted')

		frappe.db.commit()

		return {
			'response': 'Success',
			'expense': report.name
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Error creating expense report: {str(e)}")

		# Only delete if report was created
		if report and report.name:
			try:
				frappe.delete_doc('Expense Report', report.name, force=True)
			except Exception as cleanup_error:
				frappe.log_error(f"Failed to cleanup expense report {report.name}: {str(cleanup_error)}")

		return {'response': 'Error', 'message': str(e)}


def _update_expense_workflow_state(expense_name, state):
	"""Update expense workflow state using proper workflow API."""
	try:
		doc = frappe.get_doc('Expense', expense_name)
		# Try to use workflow API if available
		try:
			apply_workflow(doc, state)
		except Exception:
			# Fallback to direct assignment if workflow action doesn't exist
			doc.workflow_state = state
			doc.save()
	except Exception as e:
		frappe.log_error(f"Error updating expense workflow state: {str(e)}")
		raise


@frappe.whitelist()
def create_bulk_expense_report(selected):
	"""Create an expense report from multiple selected expenses."""
	# Input validation
	if not selected or not isinstance(selected, str):
		return {'response': 'Error', 'message': 'Invalid selection parameter'}

	# Parse the JSON array into a Python list of dictionaries
	try:
		json_list = json.loads(selected)
	except json.JSONDecodeError:
		return {'response': 'Error', 'message': 'Invalid JSON format'}

	if not isinstance(json_list, list):
		return {'response': 'Error', 'message': 'Selection must be a list'}

	if not json_list:
		return {'response': 'Error', 'message': 'No expenses selected'}

	details = []
	last_expense = None

	for expense in json_list:
		last_expense = expense.get('name')
		details.append({
			'expense_id': expense.get('name'),
			'expense_date': expense.get('expense_date'),
			'category': expense.get('category'),
			'description': expense.get('expense_description'),
			'subtotal': expense.get('total')
		})

	# Pass the information for processing
	return create_expense_report(last_expense, details)
