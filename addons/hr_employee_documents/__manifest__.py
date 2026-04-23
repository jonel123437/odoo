{
    'name': "Employee Documents",
    'summary': "Manage employee 201 file documents",
    'description': """
Upload and track employee documents such as contracts, government IDs,
and certifications — with issue/expiry dates and status tracking.
    """,
    'author': "Jonel",
    'category': 'Human Resources',
    'version': '19.0.1.0.0',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
