{
    'name': 'Propertio',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'The TCRM Real Estate Engine',
    'description': """
        Propertio - High-performance Real Estate Module
        -----------------------------------------------
        Replaces legacy systems by handling the entire lifecycle of Real Estate development:
        - Inventory (Projects, Blocks, Units)
        - Sales & Payment Plans
        - Collections
        - Reporting
    """,
    'author': 'Tcrm S.A.',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/propertio_data.xml',
        'reports/contract_template.xml',
        'views/propertio_menus.xml',
        'views/propertio_project_views.xml',
        'views/propertio_unit_views.xml',
        'views/sale/propertio_sale_search.xml',
        'views/sale/propertio_sale_list.xml',
        'views/wizards/print_wizard.xml',
        'views/sale/propertio_sale_form.xml',
        'views/payment/propertio_payment_views.xml',
        'views/wizards/sale_wizard.xml',
        'views/propertio_menus_actions.xml',
        'views/propertio_reporting_views.xml',
        'reports/propertio_reports.xml',
        'views/propertio_export_wizard.xml',
    ],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
