from odoo import models, fields, api


class EmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'Employee Document'
    _order = 'expiry_date asc, name'

    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection([
        ('contract', 'Employment Contract'),
        ('gov_id', 'Government ID'),
        ('prc', 'PRC License'),
        ('medical', 'Medical Record'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ], string='Document Type', required=True, default='other')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, ondelete='cascade',
    )
    attachment = fields.Binary(string='File', attachment=True)
    attachment_filename = fields.Char(string='Filename')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='draft', string='Status')
    notes = fields.Text(string='Notes')

    source = fields.Selection([
        ('custom', 'Custom'),
        ('builtin', 'Built-in'),
    ], string='Source', default='custom', readonly=True)

    builtin_field = fields.Char(string='Built-in Field Ref', readonly=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    BUILTIN_DOCS = [
        ('id_card',         'ID Card Copy',   'gov_id'),
        ('driving_license', 'Driving License','other'),
        ('has_work_permit', 'Work Permit',    'other'),
    ]

    def _sync_builtin_documents(self):
        """Create or delete hr.employee.document records mirroring built-in fields."""
        Document = self.env['hr.employee.document']
        for employee in self:
            for field_name, doc_name, doc_type in self.BUILTIN_DOCS:
                file_data = employee[field_name]
                existing = Document.search([
                    ('employee_id', '=', employee.id),
                    ('builtin_field', '=', field_name),
                ], limit=1)

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
                elif file_data and existing:
                    existing.write({'attachment': file_data})
                elif not file_data and existing:
                    existing.unlink()

    def write(self, vals):
        res = super().write(vals)
        builtin_fields = {'id_card', 'driving_license', 'has_work_permit'}
        if any(f in vals for f in builtin_fields):
            self._sync_builtin_documents()
        return res