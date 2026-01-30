# -*- coding: utf-8 -*-
"""
Propertio Report Generator - Multi-Format Export Engine
Generates: XLSX, CSV, PDF (reportlab), HTML
"""

import base64
import io
import csv
from datetime import datetime
from .report_base import ReportStyleMixin, COLORS


class ReportGenerator(ReportStyleMixin):
    """Generates reports in multiple formats with consistent styling"""
    
    def __init__(self, report_data):
        self.report_data = report_data
        self.title = report_data.get_title()
        self.headers = report_data.get_headers()
        self.data = report_data.get_data()
        self.summary = report_data.get_summary()
        self.column_widths = report_data.get_column_widths()
    
    def generate_xlsx(self):
        """Generate Excel file with formatting and colors"""
        try:
            import xlsxwriter
        except ImportError:
            raise Exception('xlsxwriter not installed. Run: pip install xlsxwriter')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.title[:31])  # Sheet name max 31 chars
        
        formats = self.get_excel_formats(workbook)
        
        # Set column widths
        for col, width in enumerate(self.column_widths):
            worksheet.set_column(col, col, width)
        
        # Title row
        title_format = workbook.add_format({
            'bold': True, 'font_size': 16, 'font_color': COLORS['header']['bg'],
            'bottom': 2, 'bottom_color': COLORS['header']['bg']
        })
        worksheet.merge_range(0, 0, 0, len(self.headers) - 1, self.title, title_format)
        
        # Metadata row
        meta_format = workbook.add_format({'font_size': 10, 'font_color': '#718096'})
        meta_text = f"Generated: {self.report_data.generated_at.strftime('%Y-%m-%d %H:%M')}"
        if self.report_data.date_from or self.report_data.date_to:
            meta_text += f" | Period: {self.report_data.date_from or 'Start'} to {self.report_data.date_to or 'End'}"
        worksheet.merge_range(1, 0, 1, len(self.headers) - 1, meta_text, meta_format)
        
        # Summary section if available
        row_offset = 3
        if self.summary:
            summary_title_fmt = workbook.add_format({
                'bold': True, 'font_size': 12, 'font_color': COLORS['header']['bg']
            })
            worksheet.write(row_offset, 0, 'Summary', summary_title_fmt)
            row_offset += 1
            
            col = 0
            for key, value in self.summary.items():
                label_fmt = workbook.add_format({'font_color': '#718096', 'font_size': 10})
                value_fmt = workbook.add_format({
                    'bold': True, 'font_size': 14, 'font_color': COLORS['header']['bg'],
                    'num_format': '#,##0.00' if isinstance(value, (int, float)) else '@'
                })
                worksheet.write(row_offset, col, key, label_fmt)
                worksheet.write(row_offset + 1, col, value, value_fmt)
                col += 1
            row_offset += 3
        
        # Headers
        for col, header in enumerate(self.headers):
            worksheet.write(row_offset, col, header, formats['header'])
        row_offset += 1
        
        # Data rows
        for row_data in self.data:
            row_status = row_data.get('_status', None) if isinstance(row_data, dict) else None
            
            for col, header in enumerate(self.headers):
                value = row_data.get(header, '') if isinstance(row_data, dict) else (
                    row_data[col] if col < len(row_data) else ''
                )
                
                # Determine format based on value type and status
                cell_format = formats['normal']
                
                if header.lower() in ['status', 'payment_status', 'payment status']:
                    status_key = str(value).lower()
                    cell_format = formats.get(f'status_{status_key}', formats['normal'])
                elif header.lower() in ['state', 'unit_state', 'unit state']:
                    status_key = str(value).lower()
                    cell_format = formats.get(f'unit_{status_key}', formats['normal'])
                elif row_status:
                    cell_format = formats.get(f'row_{row_status}', formats['normal'])
                elif isinstance(value, (int, float)) and any(x in header.lower() for x in ['amount', 'price', 'value', 'total', 'paid', 'balance', 'residual']):
                    cell_format = formats['currency']
                elif isinstance(value, (int, float)) and '%' in header:
                    cell_format = formats['percent']
                
                worksheet.write(row_offset, col, value, cell_format)
            row_offset += 1
        
        # Totals row if we have numeric columns
        totals = self._calculate_totals()
        if totals:
            for col, header in enumerate(self.headers):
                value = totals.get(header, '')
                if col == 0:
                    value = 'TOTAL'
                worksheet.write(row_offset, col, value, formats['total'])
        
        workbook.close()
        output.seek(0)
        return output.read()
    
    def generate_csv(self):
        """Generate CSV file"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Title and metadata
        writer.writerow([self.title])
        writer.writerow([f"Generated: {self.report_data.generated_at.strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow([])
        
        # Summary
        if self.summary:
            for key, value in self.summary.items():
                writer.writerow([key, value])
            writer.writerow([])
        
        # Headers
        writer.writerow(self.headers)
        
        # Data
        for row_data in self.data:
            if isinstance(row_data, dict):
                row = [row_data.get(h, '') for h in self.headers]
            else:
                row = list(row_data)
            writer.writerow(row)
        
        # Totals
        totals = self._calculate_totals()
        if totals:
            row = ['TOTAL'] + [totals.get(h, '') for h in self.headers[1:]]
            writer.writerow(row)
        
        return output.getvalue().encode('utf-8')
    
    def generate_pdf(self):
        """Generate PDF using reportlab (no wkhtmltopdf needed)"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm, inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.colors import HexColor
        except ImportError:
            raise Exception('reportlab not installed. Run: pip install reportlab')
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output, 
            pagesize=landscape(A4),
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#1a365d'),
            spaceAfter=12
        )
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#718096'),
            spaceAfter=20
        )
        
        # Title
        elements.append(Paragraph(self.title, title_style))
        
        # Metadata
        meta_text = f"Generated: {self.report_data.generated_at.strftime('%Y-%m-%d %H:%M')}"
        if self.report_data.date_from or self.report_data.date_to:
            meta_text += f" | Period: {self.report_data.date_from or 'Start'} to {self.report_data.date_to or 'End'}"
        elements.append(Paragraph(meta_text, meta_style))
        
        # Summary table if available
        if self.summary:
            summary_data = [[k, str(v)] for k, v in self.summary.items()]
            summary_table = Table(summary_data, colWidths=[100, 100])
            summary_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#718096')),
                ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#1a365d')),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 20))
        
        # Main data table
        table_data = [self.headers]
        for row_data in self.data:
            if isinstance(row_data, dict):
                row = [str(row_data.get(h, '')) for h in self.headers]
            else:
                row = [str(v) for v in row_data]
            table_data.append(row)
        
        # Add totals
        totals = self._calculate_totals()
        if totals:
            totals_row = ['TOTAL'] + [str(totals.get(h, '')) for h in self.headers[1:]]
            table_data.append(totals_row)
        
        # Calculate column widths
        page_width = landscape(A4)[0] - 30*mm
        num_cols = len(self.headers)
        col_widths = [page_width / num_cols] * num_cols
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Table styling
        table_style = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), HexColor('#f7fafc')))
        
        # Color code status columns
        for row_idx, row_data in enumerate(self.data, start=1):
            if isinstance(row_data, dict):
                for col_idx, header in enumerate(self.headers):
                    if header.lower() in ['status', 'payment_status', 'payment status']:
                        status = str(row_data.get(header, '')).lower()
                        color_map = {
                            'paid': '#d4edda',
                            'overdue': '#f8d7da', 
                            'upcoming': '#fff3cd',
                            'future': '#e2e3e5'
                        }
                        if status in color_map:
                            table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), HexColor(color_map[status])))
        
        # Totals row styling
        if totals:
            last_row = len(table_data) - 1
            table_style.append(('BACKGROUND', (0, last_row), (-1, last_row), HexColor('#edf2f7')))
            table_style.append(('FONTNAME', (0, last_row), (-1, last_row), 'Helvetica-Bold'))
            table_style.append(('LINEABOVE', (0, last_row), (-1, last_row), 2, HexColor('#1a365d')))
        
        table.setStyle(TableStyle(table_style))
        elements.append(table)
        
        doc.build(elements)
        output.seek(0)
        return output.read()
    
    def generate_html(self, include_print_button=True):
        """Generate HTML report"""
        html_styles = self.get_html_styles()
        
        # Build summary cards
        summary_html = ''
        if self.summary:
            cards = ''
            for key, value in self.summary.items():
                card_class = ''
                if any(x in key.lower() for x in ['paid', 'collected', 'received']):
                    card_class = 'success'
                elif any(x in key.lower() for x in ['overdue', 'outstanding']):
                    card_class = 'danger'
                elif any(x in key.lower() for x in ['upcoming', 'pending']):
                    card_class = 'warning'
                
                formatted_value = f"{value:,.2f}" if isinstance(value, (int, float)) else value
                cards += f'''
                <div class="summary-card {card_class}">
                    <div class="label">{key}</div>
                    <div class="value">{formatted_value}</div>
                </div>
                '''
            summary_html = f'<div class="summary-cards">{cards}</div>'
        
        # Build table headers
        headers_html = ''.join(f'<th>{h}</th>' for h in self.headers)
        
        # Build table rows
        rows_html = ''
        for row_data in self.data:
            row_class = ''
            if isinstance(row_data, dict):
                status = row_data.get('Payment Status', row_data.get('Status', '')).lower()
                if status in ['paid', 'overdue', 'upcoming', 'future']:
                    row_class = f'row-{status}'
                
                cells = ''
                for header in self.headers:
                    value = row_data.get(header, '')
                    cell_class = ''
                    
                    # Format status as badge
                    if header.lower() in ['status', 'payment_status', 'payment status']:
                        badge_class = f'badge-{str(value).lower()}'
                        value = f'<span class="badge {badge_class}">{value}</span>'
                    elif header.lower() in ['state', 'unit_state', 'unit state']:
                        badge_class = f'badge-{str(value).lower()}'
                        value = f'<span class="badge {badge_class}">{value}</span>'
                    # Format currency
                    elif isinstance(value, (int, float)) and any(x in header.lower() for x in ['amount', 'price', 'value', 'total', 'paid', 'balance', 'residual']):
                        cell_class = 'currency'
                        if value < 0:
                            cell_class += ' negative'
                        elif value > 0 and any(x in header.lower() for x in ['paid', 'collected']):
                            cell_class += ' positive'
                        value = f"{value:,.2f}"
                    
                    cells += f'<td class="{cell_class}">{value}</td>'
                rows_html += f'<tr class="{row_class}">{cells}</tr>'
            else:
                cells = ''.join(f'<td>{v}</td>' for v in row_data)
                rows_html += f'<tr>{cells}</tr>'
        
        # Totals row
        totals = self._calculate_totals()
        if totals:
            cells = '<td><strong>TOTAL</strong></td>'
            for header in self.headers[1:]:
                value = totals.get(header, '')
                if isinstance(value, (int, float)):
                    value = f"<strong>{value:,.2f}</strong>"
                cells += f'<td class="currency">{value}</td>'
            rows_html += f'<tr class="total-row">{cells}</tr>'
        
        # Metadata
        meta_text = f"Generated: {self.report_data.generated_at.strftime('%Y-%m-%d %H:%M')}"
        if self.report_data.date_from or self.report_data.date_to:
            meta_text += f" | Period: {self.report_data.date_from or 'Start'} to {self.report_data.date_to or 'End'}"
        
        # Print button
        print_button = ''
        if include_print_button:
            print_button = '''
            <div class="no-print" style="margin-bottom: 20px;">
                <button onclick="window.print()" style="padding: 10px 20px; background: #1a365d; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                    Print / Save as PDF
                </button>
                <span style="margin-left: 15px; color: #718096; font-size: 12px;">
                    Tip: Use your browser's print function (Ctrl+P) to save as PDF
                </span>
            </div>
            '''
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.title}</title>
            {html_styles}
        </head>
        <body>
            <div class="report-container">
                {print_button}
                <div class="report-header">
                    <h1>{self.title}</h1>
                    <div class="meta">{meta_text}</div>
                </div>
                {summary_html}
                <table>
                    <thead>
                        <tr>{headers_html}</tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        '''
        
        return html.encode('utf-8')
    
    def _calculate_totals(self):
        """Calculate totals for numeric columns"""
        if not self.data:
            return {}
        
        totals = {}
        for header in self.headers:
            values = []
            for row_data in self.data:
                if isinstance(row_data, dict):
                    value = row_data.get(header)
                else:
                    idx = self.headers.index(header)
                    value = row_data[idx] if idx < len(row_data) else None
                
                if isinstance(value, (int, float)):
                    values.append(value)
            
            if values and any(x in header.lower() for x in ['amount', 'price', 'value', 'total', 'paid', 'balance', 'residual', 'collected', 'receivable']):
                totals[header] = sum(values)
        
        return totals
