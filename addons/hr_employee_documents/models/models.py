from odoo import models, fields, api
from odoo.exceptions import ValidationError


# Custom model to store employee documents (your new database table)
class EmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'Employee Document'
    _order = 'expiry_date asc, name'

    # Document Name - shown in list and form view
    name = fields.Char(string='Document Name', required=True)

    # Document Type - dropdown shown in list and form view
    document_type = fields.Selection([
        ('contract', 'Employment Contract'),
        ('gov_id', 'Government ID'),
        ('prc', 'PRC License'),
        ('medical', 'Medical Record'),
        ('certificate', 'Certificate'),
        ('driving_license', 'Driving License'),
        ('work_permit', 'Work Permit'),
        ('other', 'Other'),
    ], string='Document Type', required=True, default='other')

    # Links this document to an employee, auto-deletes if employee is deleted
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, ondelete='cascade',
    )

    # The actual uploaded file
    attachment = fields.Binary(string='File', attachment=True)

    # Stores the filename string, used internally by the attachment widget
    attachment_filename = fields.Char(string='Filename')

    # Date the document was issued
    issue_date = fields.Date(string='Issue Date')

    # Date the document expires, also used for default sort order
    expiry_date = fields.Date(string='Expiry Date')

    # Document status shown in list and form view
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='draft', string='Status')

    # Optional notes, hidden in form view for Built-in docs
    notes = fields.Text(string='Notes')

    # Tracks if document came from custom module or built-in employee profile
    source = fields.Selection([
        ('custom', 'Custom'),
        ('builtin', 'Built-in'),
    ], string='Source', default='custom', readonly=True)

    # Stores which built-in field this mirrors (e.g. 'id_card'), used by sync logic
    builtin_field = fields.Char(string='Built-in Field Ref', readonly=True)

    # Prevents user from deleting Built-in documents from this module
    def unlink(self):
        for record in self:
            if record.source == 'builtin' and not self.env.context.get('sync_unlink'):
                raise ValidationError(
                    f"Cannot delete '{record.name}' — it is managed from the Employee Profile. "
                    "To remove it, go to the employee's profile and delete the file there."
                )
        return super().unlink()


# Extends Odoo's built-in hr.employee model to add sync logic
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Maps built-in field names to display name and document type
    BUILTIN_DOCS = [
        ('id_card',         'ID Card Copy',    'gov_id'),
        ('driving_license', 'Driving License', 'driving_license'),
        ('has_work_permit', 'Work Permit',     'work_permit'),
    ]

    # Checks each built-in field and creates/updates/deletes mirror records
    def _sync_builtin_documents(self):
        Document = self.env['hr.employee.document']
        for employee in self:
            for field_name, doc_name, doc_type in self.BUILTIN_DOCS:
                file_data = employee[field_name]

                # Find existing mirror record for this field
                existing = Document.search([
                    ('employee_id', '=', employee.id),
                    ('builtin_field', '=', field_name),
                ], limit=1)

                # File uploaded and no mirror yet - create one
                if file_data and not existing:
                    Document.create({
                        'name': doc_name,
                        'document_type': doc_type,
                        'employee_id': employee.id,
                        'attachment': file_data,
                        'attachment_filename': doc_name,
                        'source': 'builtin',
                        'builtin_field': field_name,
                        'state': 'active',
                    })
                # File updated and mirror exists - update the file
                elif file_data and existing:
                    existing.write({'attachment': file_data})

                # File deleted from employee profile - remove mirror record
                elif not file_data and existing:
                    existing.with_context(sync_unlink=True).unlink()

    # Intercepts every employee save to trigger sync if a built-in doc field changed
    def write(self, vals):
        res = super().write(vals)
        builtin_fields = {'id_card', 'driving_license', 'has_work_permit'}
        if any(f in vals for f in builtin_fields):
            self._sync_builtin_documents()
        return res