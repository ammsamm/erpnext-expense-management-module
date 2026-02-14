"""
Centralized Arabic translations for the Expense Management system.

Translations are inserted into the Translation DocType (Frappe's global translation system)
so both erpnext_expenses and POSNext pick them up via get_all_translations("ar").

Runs on every `bench migrate` via after_migrate hook.
"""

import frappe


# All Arabic translations for expense-related strings across both apps
TRANSLATIONS = {
    # ── erpnext_expenses: Python (expense.py) ──
    "Expenses must be submitted via an Expense Report. "
    'Use the "Create Report" button to submit this expense.':
        "يجب تقديم المصروفات عبر تقرير المصروفات. "
        'استخدم زر "إنشاء تقرير" لتقديم هذا المصروف.',
    "Direct Submission Not Allowed": "التقديم المباشر غير مسموح",
    "An error occurred while creating the expense report":
        "حدث خطأ أثناء إنشاء تقرير المصروفات",
    "You can only create expenses for your own employee record.":
        "يمكنك فقط إنشاء مصروفات لسجل الموظف الخاص بك.",
    "Permission Denied": "تم رفض الإذن",
    "Maximum {0} attachments allowed per expense. You have {1}.":
        "الحد الأقصى {0} مرفقات مسموح بها لكل مصروف. لديك {1}.",
    "Too Many Attachments": "عدد المرفقات كثير جداً",
    "Attachment #{0}: File type \".{1}\" is not allowed. Allowed types: {2}":
        "المرفق #{0}: نوع الملف \".{1}\" غير مسموح. الأنواع المسموحة: {2}",
    "Invalid File Type": "نوع ملف غير صالح",
    "Attachment #{0}: File size ({1}MB) exceeds maximum allowed size of {2}MB.":
        "المرفق #{0}: حجم الملف ({1} ميجابايت) يتجاوز الحد الأقصى المسموح {2} ميجابايت.",
    "File Too Large": "حجم الملف كبير جداً",
    "Total attachment size ({0}MB) exceeds maximum allowed total of {1}MB.":
        "إجمالي حجم المرفقات ({0} ميجابايت) يتجاوز الحد الأقصى المسموح {1} ميجابايت.",
    "Total Size Exceeded": "تجاوز الحجم الإجمالي",
    "Invalid expense parameter": "معامل مصروف غير صالح",
    "You do not have permission to access this expense":
        "ليس لديك صلاحية للوصول إلى هذا المصروف",
    "Expense not found": "المصروف غير موجود",
    "Expense {0} has already been submitted and cannot be added to a new report.":
        "المصروف {0} تم تقديمه بالفعل ولا يمكن إضافته إلى تقرير جديد.",
    "Expense Already Submitted": "المصروف مُقدَّم بالفعل",
    "Expense {0} is already linked to Expense Report {1}.":
        "المصروف {0} مرتبط بالفعل بتقرير المصروفات {1}.",
    "Expense Already in Report": "المصروف موجود في تقرير بالفعل",
    "Invalid selection parameter": "معامل اختيار غير صالح",
    "Invalid JSON format": "تنسيق JSON غير صالح",
    "Selection must be a list": "يجب أن يكون الاختيار قائمة",
    "No expenses selected": "لم يتم اختيار أي مصروفات",

    # ── erpnext_expenses: Python (expense_report.py) ──
    "Invalid report parameter": "معامل تقرير غير صالح",
    "You do not have permission to modify this expense report":
        "ليس لديك صلاحية لتعديل تقرير المصروفات هذا",
    "Expense Report {0} not found": "تقرير المصروفات {0} غير موجود",
    "Please set the Paying Account before creating journal entries.":
        "يرجى تعيين حساب الدفع قبل إنشاء القيود المحاسبية.",
    "Missing Paying Account": "حساب الدفع مفقود",
    "Journal Entry {0} already exists for this Expense Report.":
        "القيد المحاسبي {0} موجود بالفعل لتقرير المصروفات هذا.",
    "Duplicate Journal Entry": "قيد محاسبي مكرر",
    'Tax "{0}" does not have a Tax Account configured. '
    "Please set a Tax Account in the Expense Taxes master.":
        'الضريبة "{0}" ليس لها حساب ضريبة معيّن. '
        "يرجى تعيين حساب ضريبة في بيانات ضرائب المصروفات.",
    "Missing Tax Account": "حساب الضريبة مفقود",
    "Error creating journal entries: {0}": "خطأ في إنشاء القيود المحاسبية: {0}",

    # ── erpnext_expenses: JS (expense.js) ──
    "Create Report": "إنشاء تقرير",
    "Creating Expense Report...": "جارٍ إنشاء تقرير المصروفات...",
    "Error": "خطأ",
    "An error was encountered. Please see the error logs for details.":
        "حدث خطأ. يرجى مراجعة سجلات الأخطاء للتفاصيل.",
    "The expense date cannot be in the future.": "لا يمكن أن يكون تاريخ المصروف في المستقبل.",
    "Attachment Limit Reached": "تم الوصول لحد المرفقات",
    "Maximum {0} attachments allowed per expense.":
        "الحد الأقصى {0} مرفقات مسموح بها لكل مصروف.",
    "View Attachment": "عرض المرفق",
    "File type \".{0}\" is not allowed. Allowed types: {1}":
        "نوع الملف \".{0}\" غير مسموح. الأنواع المسموحة: {1}",
    "The split amount ({0}) does not match the expense total ({1}).":
        "مبلغ التقسيم ({0}) لا يتطابق مع إجمالي المصروف ({1}).",
    "Maximum {0} attachments allowed. You have {1}.":
        "الحد الأقصى {0} مرفقات مسموح بها. لديك {1}.",
    "Attachment #{0}: File type \".{1}\" is not allowed.":
        "المرفق #{0}: نوع الملف \".{1}\" غير مسموح.",
    "View Attachments": "عرض المرفقات",
    "Open in New Tab": "فتح في تبويب جديد",
    "No attachments found.": "لم يتم العثور على مرفقات.",
    "Attachments ({0})": "المرفقات ({0})",
    "Invoice Attachments ({0}/{1})": "مرفقات الفاتورة ({0}/{1})",
    "Invoice Attachments": "مرفقات الفاتورة",
    "You can add 1 more attachment.": "يمكنك إضافة مرفق واحد إضافي.",
    "Maximum attachments reached ({0} files).":
        "تم الوصول للحد الأقصى من المرفقات ({0} ملفات).",

    # ── erpnext_expenses: JS (expense_report.js) ──
    "Create Journal Entries": "إنشاء القيود المحاسبية",
    "Please provide the paying account!": "يرجى تحديد حساب الدفع!",
    "Creating Journal Entry...": "جارٍ إنشاء القيد المحاسبي...",
    "Success": "تم بنجاح",
    "Journal Entry {0} created successfully.": "تم إنشاء القيد المحاسبي {0} بنجاح.",
    "Failed to create journal entry. Check error logs for details.":
        "فشل إنشاء القيد المحاسبي. تحقق من سجلات الأخطاء للتفاصيل.",

    # ── erpnext_expenses: fixtures/client_script.json ──
    "Processing entries...": "جارٍ معالجة الإدخالات...",
    "Please wait.": "يرجى الانتظار.",
    "Please select at least one expense from the list.":
        "يرجى اختيار مصروف واحد على الأقل من القائمة.",

    # ── POSNext: Python (expenses.py) ──
    "You can only access your own expenses.": "يمكنك الوصول إلى مصروفاتك الخاصة فقط.",
    "No active Employee record found for user {0}":
        "لم يتم العثور على سجل موظف نشط للمستخدم {0}",
    "Only draft expenses can be edited.": "يمكن تعديل المصروفات المسودة فقط.",
    "You can only edit your own expenses.": "يمكنك تعديل مصروفاتك الخاصة فقط.",
    "No active Employee record found.": "لم يتم العثور على سجل موظف نشط.",
    "You can only view your own expenses.": "يمكنك عرض مصروفاتك الخاصة فقط.",
    "You can only delete your own expenses.": "يمكنك حذف مصروفاتك الخاصة فقط.",
    "Only draft expenses can be deleted.": "يمكن حذف المصروفات المسودة فقط.",
    "The erpnext_expenses app is required for creating expense reports. "
    "Please install it.":
        "تطبيق erpnext_expenses مطلوب لإنشاء تقارير المصروفات. "
        "يرجى تثبيته.",
    "Action '{0}' is not allowed from POS.":
        "الإجراء '{0}' غير مسموح من نقطة البيع.",
    "You can only manage your own expense reports.":
        "يمكنك إدارة تقارير المصروفات الخاصة بك فقط.",

    # ── POSNext: Vue (ExpenseManagement.vue) ──
    "Expense Management": "إدارة المصروفات",
    "Refresh": "تحديث",
    "You are offline": "أنت غير متصل",
    "Expenses will sync when you reconnect.":
        "سيتم مزامنة المصروفات عند إعادة الاتصال.",
    "No Employee Record Found": "لم يتم العثور على سجل موظف",
    "Your user account must be linked to an active Employee record to manage expenses.":
        "يجب ربط حساب المستخدم الخاص بك بسجل موظف نشط لإدارة المصروفات.",
    "Tabs": "علامات التبويب",
    "Loading...": "جارٍ التحميل...",
    "All ({0})": "الكل ({0})",
    "Draft ({0})": "مسودة ({0})",
    "Submitted ({0})": "مُقدَّمة ({0})",
    "Create Report ({0})": "إنشاء تقرير ({0})",
    "+ New Expense": "+ مصروف جديد",
    "Loading expenses...": "جارٍ تحميل المصروفات...",
    "No Expenses": "لا توجد مصروفات",
    "Create your first expense to get started.":
        "أنشئ أول مصروف لك للبدء.",
    "Loading reports...": "جارٍ تحميل التقارير...",
    "No Expense Reports": "لا توجد تقارير مصروفات",
    "Create reports from your draft expenses.":
        "أنشئ تقارير من مصروفاتك المسودة.",
    "({0}) expenses waiting to sync": "({0}) مصروفات في انتظار المزامنة",
    "Syncing...": "جارٍ المزامنة...",
    "Sync Now": "مزامنة الآن",
    "Connect to the internet to sync expenses.":
        "اتصل بالإنترنت لمزامنة المصروفات.",
    "All Synced": "تمت المزامنة بالكامل",
    "No pending expenses to sync.": "لا توجد مصروفات معلقة للمزامنة.",
    "My Expenses": "مصروفاتي",
    "My Reports": "تقاريري",
    "Pending Sync": "في انتظار المزامنة",
    "Expense saved": "تم حفظ المصروف",
    "Expense saved offline — will sync when online":
        "تم حفظ المصروف بدون اتصال — ستتم المزامنة عند الاتصال",
    "Failed to save expense": "فشل حفظ المصروف",
    "Are you sure you want to delete this expense?":
        "هل أنت متأكد أنك تريد حذف هذا المصروف؟",
    "Expense deleted": "تم حذف المصروف",
    "Failed to delete expense": "فشل حذف المصروف",
    "Creating reports requires an internet connection":
        "إنشاء التقارير يتطلب اتصالاً بالإنترنت",
    "Expense report created": "تم إنشاء تقرير المصروفات",
    "Failed to create report": "فشل إنشاء التقرير",
    "{0} expenses synced successfully": "تمت مزامنة {0} مصروفات بنجاح",
    "{0} expenses failed to sync": "فشلت مزامنة {0} مصروفات",
    "Sync failed": "فشلت المزامنة",
    "Workflow actions require an internet connection":
        "إجراءات سير العمل تتطلب اتصالاً بالإنترنت",
    "{0}: {1}": "{0}: {1}",
    "Failed to apply action": "فشل تطبيق الإجراء",

    # ── POSNext: Vue (ExpenseFormDialog.vue) ──
    "Edit Expense": "تعديل المصروف",
    "New Expense": "مصروف جديد",
    "Description": "الوصف",
    "What is this expense for?": "ما الغرض من هذا المصروف؟",
    "Category": "الفئة",
    "Select Category": "اختر الفئة",
    "Amount": "المبلغ",
    "Paid By": "مدفوع بواسطة",
    "Date": "التاريخ",
    "Notes": "ملاحظات",
    "Additional notes...": "ملاحظات إضافية...",
    "Attachments": "المرفقات",
    "max {0} files, {1}MB each": "الحد الأقصى {0} ملفات، {1} ميجابايت لكل ملف",
    "Uploading...": "جارٍ الرفع...",
    "Add Receipt / Attachment": "إضافة إيصال / مرفق",
    "Cancel": "إلغاء",
    "Saving...": "جارٍ الحفظ...",
    "Save": "حفظ",
    "Maximum {0} attachments allowed": "الحد الأقصى {0} مرفقات مسموح بها",
    "File type .{0} is not allowed. Allowed: {1}":
        "نوع الملف .{0} غير مسموح. المسموح: {1}",
    "File {0} exceeds {1}MB limit": "الملف {0} يتجاوز حد {1} ميجابايت",
    "Total attachment size exceeds {0}MB limit":
        "إجمالي حجم المرفقات يتجاوز حد {0} ميجابايت",
    "Failed to upload {0}: {1}": "فشل رفع {0}: {1}",

    # ── POSNext: Vue (ExpenseCard.vue) ──
    "Edit": "تعديل",
    "Delete": "حذف",
    "Pending Sync": "في انتظار المزامنة",
    "Draft": "مسودة",
    "Submitted": "مُقدَّم",
    "Cancelled": "ملغي",

    # ── POSNext: Vue (ExpenseReportCard.vue) ──
    "Manager": "المدير",
    "Finance": "المالية",
    "Approved": "مُعتمد",
    "Complete": "مكتمل",
    "Rejected": "مرفوض",
    "Submit to Manager": "تقديم للمدير",
    "Recall": "استرجاع",
    "Revise": "مراجعة",

    # ── Common / Shared strings ──
    "Expense": "مصروف",
    "Expense Report": "تقرير المصروفات",
    "Expense Category": "فئة المصروفات",
    "Expense Taxes": "ضرائب المصروفات",
    "Employee": "موظف",
    "Company": "شركة",

    # ── DocType field labels ──
    "Expense Description": "وصف المصروف",
    "Expense Date": "تاريخ المصروف",
    "Total": "الإجمالي",
    "Employee Name": "اسم الموظف",
    "Paid By": "مدفوع بواسطة",
    "Paid by": "مدفوع بواسطة",
    "Paying Account": "حساب الدفع",
    "Amended From": "معدّل من",
    "Invoice Attachments": "مرفقات الفاتورة",
    "Expense Splitting": "تقسيم المصروف",
    "Split Total": "إجمالي التقسيم",
    "Expenses": "المصروفات",

    # ── Select field options ──
    "Employee (to reimburse)": "موظف (للتعويض)",
}


def setup_translations():
    """Insert or update Arabic translations in Frappe's Translation DocType.

    Called via after_migrate hook. Both erpnext_expenses and POSNext
    read from the same Translation table via get_all_translations("ar").
    """
    count_new = 0
    count_updated = 0

    for source_text, translated_text in TRANSLATIONS.items():
        existing = frappe.db.get_value(
            "Translation",
            {"language": "ar", "source_text": source_text},
            ["name", "translated_text"],
            as_dict=True,
        )

        if existing:
            if existing.translated_text != translated_text:
                frappe.db.set_value(
                    "Translation", existing.name, "translated_text", translated_text
                )
                count_updated += 1
        else:
            doc = frappe.get_doc({
                "doctype": "Translation",
                "language": "ar",
                "source_text": source_text,
                "translated_text": translated_text,
            })
            doc.insert(ignore_permissions=True)
            count_new += 1

    if count_new or count_updated:
        frappe.db.commit()
        # Clear translation cache so changes take effect immediately
        frappe.cache.delete_key("translations")
        frappe.cache.delete_key("lang_user_translations")

    if count_new or count_updated:
        print(
            f"Expense translations: {count_new} new, {count_updated} updated "
            f"(total {len(TRANSLATIONS)} entries)"
        )
