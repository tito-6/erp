{
    'name': 'Propertio',
    'version': '1.1',
    'category': 'Real Estate',
    'summary': 'The TCRM Real Estate Engine',
    'description': """
        Propertio - High-performance Real Estate Module
        -----------------------------------------------
        Replaces legacy systems by handling the entire lifecycle of Real Estate development:
        - Inventory (Projects, Blocks, Units)
        - Sales & Payment Plans
        - Collections
        - Advanced Reporting (28 report types with multi-format export)
        
        Export Formats: XLSX, CSV, PDF, HTML
        All reports maintain consistent color coding and professional layouts.
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
        'views/wizards/unified_report_wizard.xml',
        'views/propertio_menus_actions.xml',
        'views/propertio_reporting_views.xml',
        'views/propertio_reports_menu.xml',
        'reports/propertio_reports.xml',
        'views/propertio_export_wizard.xml',
    ],
    'external_dependencies': {
        'python': ['xlsxwriter', 'reportlab'],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
