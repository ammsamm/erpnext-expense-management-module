# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Invoice Attachments**: New "Expense Attachment" child doctype allowing multiple file attachments per expense
- New collapsible "Invoice Attachments" section in Expense form with attachment table
- **Attachment Validation**:
  - Maximum 5 files per expense
  - Allowed file types: PDF, images (jpg, png, gif, webp), documents (doc, docx, xls, xlsx)
  - Maximum 5MB per file, 15MB total per expense
  - Client-side validation with instant feedback
  - Server-side validation for security
  - Dynamic counter showing attachments used (e.g., "Invoice Attachments (3/5)")

### Security
- **CRITICAL**: Fixed SQL injection vulnerability in `expense_report.py` - replaced f-string interpolation with parameterized query using `%s` placeholder ([CWE-89](https://cwe.mitre.org/data/definitions/89.html))
- Added input validation on all whitelisted API endpoints
- Added permission checks to verify user access before operations
- Added JSON parse error handling for bulk operations

### Fixed
- **Tax Calculation Bug**: Journal entries now correctly deduct per-expense taxes instead of deducting total taxes from each expense line item
- **Transaction Safety**: Added `frappe.db.rollback()` on exceptions to prevent partial data corruption
- **Null Reference Error**: Fixed potential `NameError` when deleting expense report on failure (report variable may not exist)
- **Missing Return Value**: `create_bulk_expense_report()` now returns the response from `create_expense_report()`
- **Null Safety**: Replaced direct dictionary access (`expense['name']`) with `.get()` methods to prevent `KeyError`
- **Wrong Field Reference**: Fixed `table_jkwj_add` handler that referenced non-existent `frm.doc.amount` field
- **Dead Code**: Removed unreachable code after `frappe.throw()` in date validation
- **Circular Logic**: Removed problematic `after_workflow_action` hook that could cause duplicate journal entries
- **Silent Failures**: Cleanup errors now logged instead of silently swallowed

### Changed
- **Workflow State Updates**: Replaced direct `workflow_state` assignment with `frappe.model.workflow.apply_workflow()` API for proper workflow rule enforcement
- **JavaScript API**: Replaced deprecated `frappe.db.get_doc()` 3-parameter syntax with `frappe.call()` using `frappe.client.get` method
- **Validation Pattern**: Replaced `frappe.validated = false` with `frappe.throw()` for proper error handling in Frappe v15
- **Employee Lookup**: Changed `frappe.db.get_value()` to use `as_dict=True` for safer tuple unpacking
- **Strict Equality**: Changed all `==` comparisons to `===` in JavaScript for type-safe comparisons
- **Variable Declarations**: Added proper `const`/`let` declarations to prevent implicit globals

### Added
- `required_apps = ["frappe", "erpnext"]` in hooks.py for proper dependency management
- Helper functions `_update_expense_workflow_state()` and `_update_report_workflow_state()` for reusable workflow updates
- Success messages and `frm.reload_doc()` after journal entry creation
- Null check for `frm.doc.table_jkwj` before iteration
- Docstrings for all public functions
- Compatibility documentation in README.md
- This CHANGELOG.md file
- Freeze UI with loading message during async operations
- Error callback handlers for failed API calls
- Better error messages showing actual amounts in split validation

### Documentation
- Updated README.md with ERPNext 15 compatibility table
- Added installation instructions with proper GitHub URL
- Documented all changes made for v15 compatibility
- Converted HTML code blocks to Markdown fenced blocks
