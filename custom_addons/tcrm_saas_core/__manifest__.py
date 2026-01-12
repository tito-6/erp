{
    'name': 'TCRM SaaS Core',
    'version': '1.0',
    'summary': 'Master module for TCRM Multi-tenancy',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/tenant_views.xml',
    ],
    'installable': True,
    'application': True,
}
