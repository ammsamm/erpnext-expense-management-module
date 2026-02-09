# Copyright (c) 2024, Karani Geoffrey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import os

# Attachment configuration
MAX_ATTACHMENTS = 5
MAX_FILE_SIZE_MB = 5
MAX_TOTAL_SIZE_MB = 15
ALLOWED_EXTENSIONS = {
	'pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp',
	'doc', 'docx', 'xls', 'xlsx'
}


class Expense(Document):
	def before_submit(self):
		"""Ensure expense is linked to an Expense Report before submission."""
		linked = frappe.db.exists('Expense Detail', {'expense_id': self.name})
		if not linked:
			frappe.throw(
				'Expenses must be submitted via an Expense Report. '
				'Use the "Create Report" button to submit this expense.',
				title='Direct Submission Not Allowed'
			)

	def validate(self):
		"""Validate expense document before saving."""
		self.validate_attachments()

	def validate_attachments(self):
		"""Validate attachment count, file types, and sizes."""
		if not self.attachments:
			return

		# Check attachment count
		if len(self.attachments) > MAX_ATTACHMENTS:
			frappe.throw(
				f'Maximum {MAX_ATTACHMENTS} attachments allowed per expense. '
				f'You have {len(self.attachments)}.',
				title='Too Many Attachments'
			)

		total_size = 0

		for idx, attachment in enumerate(self.attachments, 1):
			if not attachment.attachment:
				continue

			# Get file info
			file_url = attachment.attachment
			file_doc = frappe.get_doc('File', {'file_url': file_url})

			if not file_doc:
				continue

			# Validate file extension
			file_name = file_doc.file_name or ''
			extension = os.path.splitext(file_name)[1].lower().lstrip('.')

			if extension not in ALLOWED_EXTENSIONS:
				frappe.throw(
					f'Attachment #{idx}: File type ".{extension}" is not allowed. '
					f'Allowed types: {", ".join(sorted(ALLOWED_EXTENSIONS))}',
					title='Invalid File Type'
				)

			# Validate individual file size
			file_size_mb = (file_doc.file_size or 0) / (1024 * 1024)

			if file_size_mb > MAX_FILE_SIZE_MB:
				frappe.throw(
					f'Attachment #{idx}: File size ({file_size_mb:.1f}MB) exceeds '
					f'maximum allowed size of {MAX_FILE_SIZE_MB}MB.',
					title='File Too Large'
				)

			total_size += file_doc.file_size or 0

			# Auto-populate file name
			if not attachment.file_name:
				attachment.file_name = file_name

		# Validate total size
		total_size_mb = total_size / (1024 * 1024)
		if total_size_mb > MAX_TOTAL_SIZE_MB:
			frappe.throw(
				f'Total attachment size ({total_size_mb:.1f}MB) exceeds '
				f'maximum allowed total of {MAX_TOTAL_SIZE_MB}MB.',
				title='Total Size Exceeded'
			)


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
				_check_expense_not_in_active_report(detail.get('expense_id'))
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

				_submit_expense(detail.get('expense_id'))
		else:
			_check_expense_not_in_active_report(expense)
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

			_submit_expense(expense)

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


def _check_expense_not_in_active_report(expense_id):
	"""Ensure expense is in Draft and not already linked to an active report."""
	# Check if expense is already submitted (e.g. journals already created)
	docstatus = frappe.db.get_value('Expense', expense_id, 'docstatus')
	if docstatus and docstatus != 0:
		frappe.throw(
			f'Expense {expense_id} has already been submitted and cannot be added to a new report.',
			title='Expense Already Submitted'
		)

	# Check if expense is already linked to an active (non-cancelled) report
	existing = frappe.db.sql("""
		SELECT ed.parent FROM `tabExpense Detail` ed
		JOIN `tabExpense Report` er ON er.name = ed.parent
		WHERE ed.expense_id = %s AND er.docstatus != 2
		LIMIT 1
	""", (expense_id,), as_dict=True)

	if existing:
		frappe.throw(
			f'Expense {expense_id} is already linked to Expense Report {existing[0].parent}.',
			title='Expense Already in Report'
		)


def _submit_expense(expense_name):
	"""Submit an expense document (docstatus 0 → 1).

	Args:
		expense_name: Name of the Expense document
	"""
	try:
		doc = frappe.get_doc('Expense', expense_name)
		doc.submit()
	except Exception as e:
		frappe.log_error(f"Error submitting expense: {str(e)}")
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
