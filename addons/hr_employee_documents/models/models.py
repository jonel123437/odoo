from odoo import models, fields


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
