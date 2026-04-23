# from odoo import http


# class HrEmployeeDocuments(http.Controller):
#     @http.route('/hr_employee_documents/hr_employee_documents', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_employee_documents/hr_employee_documents/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_employee_documents.listing', {
#             'root': '/hr_employee_documents/hr_employee_documents',
#             'objects': http.request.env['hr_employee_documents.hr_employee_documents'].search([]),
#         })

#     @http.route('/hr_employee_documents/hr_employee_documents/objects/<model("hr_employee_documents.hr_employee_documents"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_employee_documents.object', {
#             'object': obj
#         })

