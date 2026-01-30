# -*- coding: utf-8 -*-
"""
Propertio Unified Report Wizard
Supports all 28 reports with XLSX, CSV, PDF, HTML export formats
"""

import base64
from datetime import datetime, date, timedelta
from tcrm import models, fields, api
from tcrm.exceptions import UserError

from ..reports.report_definitions import REPORT_REGISTRY
from ..reports.report_generator import ReportGenerator


class PropertioUnifiedReportWizard(models.TransientModel):
    _name = 'propertio.unified.report.wizard'
    _description = 'Unified Report Export Wizard'
    
    # Report selection with all 28 reports
    report_type = fields.Selection([
        # Collection & Payment Reports
        ('sales_collection_summary', '1. Sales Collection Summary'),
        ('payment_plan_table', '14. Payment Plan Table'),
        ('expected_payment_list', '15. Expected Payment List'),
        ('payment_plan_vat', '26. Payment Plan (VAT Included)'),
        ('incoming_payments_chart', '8. Incoming & Expected Payments'),
        
        # Sales Reports
        ('sales_report', '4. Sales Report'),
        ('type_based_sales', '2. Type-Based Sales & Inventory'),
        ('approval_based_sales', '6. Approval-Based Sales'),
        ('total_sales_chart', '7. Total Sales Chart'),
        ('daily_sales_quantity', '10. Daily Sales Quantity'),
        ('sales_status', '13. Sales Status'),
        ('sales_exchange_rate', '17. Sales Exchange Rate Analysis'),
        
        # Customer Reports
        ('customer_journey', '3. Customer Journey'),
        ('customer_journey_individual', '20. Individual Customer Journey'),
        ('customer_overall_status', '25. Customer Overall Status'),
        
        # Financial Reports
        ('cash_register', '5. Cash Register Report'),
        ('daily_cash_register', '18. Daily Cash Register'),
        ('cash_flow_statement', '11. Cash Flow Statement'),
        
        # Performance Reports
        ('employee_performance', '12. Employee Performance'),
        ('end_of_day_meeting', '9. End-of-Day Meeting'),
        
        # Property Reports
        ('independent_units', '22. Independent Units'),
        ('construction_progress', '23. Construction Progress'),
        ('title_deed_invoice', '21. Title Deed & Invoice'),
        
        # Admin & Compliance
        ('authorization_matrix', '16. Authorization Matrix'),
        ('crm_log_records', '19. CRM Activity Log'),
        
        # Marketing & Leads
        ('lead_report', '27. Lead Report'),
        ('advertising_leads', '28. Advertising Leads'),
        ('web_form_tracking', '24. Web Form Tracking'),
    ], string='Report Type', required=True, default='sales_collection_summary')
    
    # Export format
    export_format = fields.Selection([
        ('xlsx', 'Excel (XLSX)'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('html', 'HTML (View in Browser)'),
    ], string='Export Format', required=True, default='xlsx')
    
    # Date filters
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    
    # Quick date filters
    date_filter = fields.Selection([
        ('custom', 'Custom Range'),
        ('today', 'Today'),
        ('yesterday', 'Yesterday'),
        ('this_week', 'This Week'),
        ('last_week', 'Last Week'),
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
        ('last_year', 'Last Year'),
        ('all', 'All Time'),
    ], string='Date Filter', default='this_month')
    
    # Additional filters
    project_id = fields.Many2one('propertio.project', string='Project')
    partner_id = fields.Many2one('res.partner', string='Customer')
    user_id = fields.Many2one('res.users', string='Salesperson')
    
    # Output
    file_data = fields.Binary(string='File', readonly=True)
    file_name = fields.Char(string='File Name', readonly=True)
    state = fields.Selection([
        ('draft', 'Configure'),
        ('done', 'Download Ready')
    ], default='draft')
    
    # Preview for HTML
    html_preview = fields.Html(string='Report Preview', readonly=True)
    
    @api.onchange('date_filter')
    def _onchange_date_filter(self):
        """Set date range based on quick filter"""
        today = date.today()
        
        if self.date_filter == 'today':
            self.date_from = self.date_to = today
        elif self.date_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            self.date_from = self.date_to = yesterday
        elif self.date_filter == 'this_week':
            self.date_from = today - timedelta(days=today.weekday())
            self.date_to = today
        elif self.date_filter == 'last_week':
            self.date_from = today - timedelta(days=today.weekday() + 7)
            self.date_to = today - timedelta(days=today.weekday() + 1)
        elif self.date_filter == 'this_month':
            self.date_from = today.replace(day=1)
            self.date_to = today
        elif self.date_filter == 'last_month':
            first_of_month = today.replace(day=1)
            self.date_to = first_of_month - timedelta(days=1)
            self.date_from = self.date_to.replace(day=1)
        elif self.date_filter == 'this_quarter':
            quarter = (today.month - 1) // 3
            self.date_from = today.replace(month=quarter * 3 + 1, day=1)
            self.date_to = today
        elif self.date_filter == 'this_year':
            self.date_from = today.replace(month=1, day=1)
            self.date_to = today
        elif self.date_filter == 'last_year':
            self.date_from = today.replace(year=today.year - 1, month=1, day=1)
            self.date_to = today.replace(year=today.year - 1, month=12, day=31)
        elif self.date_filter == 'all':
            self.date_from = False
            self.date_to = False
    
    def _get_report_data_instance(self):
        """Get report data class instance"""
        report_class = REPORT_REGISTRY.get(self.report_type)
        if not report_class:
            raise UserError(f'Report type {self.report_type} not found')
        
        return report_class(
            env=self.env,
            date_from=self.date_from,
            date_to=self.date_to,
            project_id=self.project_id.id if self.project_id else None,
            partner_id=self.partner_id.id if self.partner_id else None,
            user_id=self.user_id.id if self.user_id else None,
        )
    
    def action_generate_report(self):
        """Generate the report in selected format"""
        self.ensure_one()
        
        # Get report data
        report_data = self._get_report_data_instance()
        generator = ReportGenerator(report_data)
        
        # Generate based on format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_name = self.report_type.replace('_', '-')
        
        if self.export_format == 'xlsx':
            content = generator.generate_xlsx()
            filename = f'{report_name}_{timestamp}.xlsx'
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        elif self.export_format == 'csv':
            content = generator.generate_csv()
            filename = f'{report_name}_{timestamp}.csv'
            mimetype = 'text/csv'
        
        elif self.export_format == 'pdf':
            content = generator.generate_pdf()
            filename = f'{report_name}_{timestamp}.pdf'
            mimetype = 'application/pdf'
        
        elif self.export_format == 'html':
            content = generator.generate_html(include_print_button=True)
            filename = f'{report_name}_{timestamp}.html'
            mimetype = 'text/html'
            
            # For HTML, also set preview
            self.html_preview = content.decode('utf-8')
        
        # Save file
        self.write({
            'file_data': base64.b64encode(content),
            'file_name': filename,
            'state': 'done'
        })
        
        # Return view
        if self.export_format == 'html':
            # Open HTML in new tab
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content?model=propertio.unified.report.wizard&id={self.id}&field=file_data&download=false&filename={filename}',
                'target': 'new',
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'propertio.unified.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
    
    def action_download(self):
        """Download the generated file"""
        self.ensure_one()
        if not self.file_data:
            raise UserError('Please generate the report first')
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=propertio.unified.report.wizard&id={self.id}&field=file_data&download=true&filename={self.file_name}',
            'target': 'self',
        }
    
    def action_view_html(self):
        """Open HTML report in browser"""
        self.ensure_one()
        if not self.file_data:
            raise UserError('Please generate the report first')
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=propertio.unified.report.wizard&id={self.id}&field=file_data&download=false&filename={self.file_name}',
            'target': 'new',
        }
    
    def action_print_pdf(self):
        """Generate and open PDF for printing"""
        self.export_format = 'html'
        return self.action_generate_report()
    
    def action_reset(self):
        """Reset wizard to initial state"""
        self.write({
            'state': 'draft',
            'file_data': False,
            'file_name': False,
            'html_preview': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'propertio.unified.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
