
# ERPNext Expense Management Module

This package contains an Expense Management Module for ERPNext.

## Compatibility

| ERPNext Version | Compatible |
|-----------------|------------|
| ERPNext 15      | Yes        |
| Frappe 15       | Yes        |
| Python          | >= 3.10    |

## Required Data
All the required data like Workflows, and all the associated information comes with this package. No need to stress about that. You can however change it to suit your specific requirements.

## How to Install

On your instance terminal, run the below command to grab the code from GitHub to your instance:

```bash
bench get-app https://github.com/ammsamm/erpnext-expense-management-module.git
```

Once the command has completed the execution, you will need to install the app in every site where you want the app to run. You can install this app with the below command:

```bash
bench --site [SITE_NAME] install-app erpnext_expenses
```

When this command completes, the application is installed in your site. You will however need to run the migrate command, which ensures that all changes to the database have been effected to your site's database. If your site is in development mode, ensure that bench is running. If you are on production, supervisor will take care of this. The command to effect the migrations is as below:

```bash
bench --site [SITE_NAME] migrate
```

At this point, your app is fully installed and database changes migrated. All you need to do is restart your instance. The commands to do that are below:

### Development Environment

```bash
bench start
```

If you receive a warning that bench is already running, run the below command:

```bash
bench restart
```

### Production Environment

```bash
sudo supervisorctl restart all
```

## Changes from Original (ERPNext 15 Compatibility Fixes)

This fork includes the following improvements for ERPNext 15 compatibility:

### Security Fixes
- **SQL Injection Prevention**: Replaced f-string SQL queries with parameterized queries in `expense_report.py`

### API Updates
- **Deprecated JS API Fix**: Replaced `frappe.db.get_doc()` 3-parameter syntax with `frappe.call()` using `frappe.client.get`
- **Workflow API**: Use `frappe.model.workflow.apply_workflow()` for proper workflow state transitions
- **Validation Pattern**: Replaced `frappe.validated = false` with `frappe.throw()` for proper error handling

### Bug Fixes
- **Tax Calculation Logic**: Fixed incorrect tax deduction in journal entries (was deducting all taxes from each expense instead of per-expense taxes)
- **Error Handling**: Added proper transaction rollback on failures
- **Null Safety**: Added proper null checks and `.get()` methods for dictionary access

### Code Quality
- Added `required_apps = ["frappe", "erpnext"]` to hooks.py for proper dependency management
- Proper variable declarations (`const`/`let`) in JavaScript
- Added docstrings and improved code documentation
- Consistent use of strict equality (`===`) in JavaScript

## License

MIT
