from tcrm import models, fields, api, _
from tcrm.exceptions import UserError
from dateutil.relativedelta import relativedelta
import datetime

class PropertioSale(models.Model):
    _name = 'propertio.sale'
    _description = 'Property Sale Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Contract Reference', required=True, copy=False, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    unit_id = fields.Many2one('propertio.unit', string='Unit', required=True, tracking=True, domain="[('state', '=', 'available')]")
    stage_id = fields.Many2one('propertio.sale.stage', string='Sale Stage')
    project_id = fields.Many2one('propertio.project', related='unit_id.project_id', string='Project', store=True)
    block_id = fields.Many2one('propertio.block', related='unit_id.block_id', string='Block', store=True)
    
    # Unit related fields for list view
    entrance = fields.Char(related='unit_id.entrance', string='Entrance', store=True)
    floor = fields.Char(related='unit_id.floor', string='Floor', store=True)
    gross_m2 = fields.Float(related='unit_id.gross_m2', string='Gross M2', store=True)
    net_m2 = fields.Float(related='unit_id.net_m2', string='Net M2', store=True)
    general_gross_m2 = fields.Float(related='unit_id.general_gross_m2', string='Gen. Gross M2', store=True)
    facade = fields.Char(related='unit_id.facade', string='Facade', store=True)
    view_type = fields.Char(related='unit_id.view_type', string='View', store=True)
    property_category_id = fields.Many2one('propertio.unit.category', related='unit_id.category_id', string='Property Category', store=True)
    status_id = fields.Many2one('propertio.unit.status', related='unit_id.status_id', string='Master Status', store=True)
    properties = fields.Properties('Contract Attributes', definition='stage_id.properties_definition')
    parking_no = fields.Char(related='unit_id.parking_no', string='Parking No', store=True)
    parking_type = fields.Selection(related='unit_id.parking_type', string='Parking Type', store=True)
    unit_code = fields.Char(related='unit_id.unit_code', string='Unit Code', store=True)
    tapu_ref = fields.Char(related='unit_id.tapu_ref', string='Tapu Ref', store=True)
    balcony_m2 = fields.Float(related='unit_id.balcony_m2', string='Balcony M2', store=True)
    terrace_m2 = fields.Float(related='unit_id.terrace_m2', string='Terrace M2', store=True)
    garden_m2 = fields.Float(related='unit_id.garden_m2', string='Garden M2', store=True)
    floor_gross_m2 = fields.Float(related='unit_id.floor_gross_m2', string='Floor Gross M2', store=True)
    ground_floor_m2 = fields.Float(related='unit_id.ground_floor_m2', string='Ground M2', store=True)
    normal_floor_m2 = fields.Float(related='unit_id.normal_floor_m2', string='Normal M2', store=True)
    
    sale_price = fields.Monetary(string='Sale Price', required=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    
    # Agency & Personnel
    agency_id = fields.Many2one('res.partner', string='Agency 1', domain=[('is_company', '=', True)])
    agency_2_id = fields.Many2one('res.partner', string='Agency 2', domain=[('is_company', '=', True)])
    sales_person_id = fields.Many2one('res.users', string='Sales Person 1', default=lambda self: self.env.user)
    sales_person_2_id = fields.Many2one('res.users', string='Sales Person 2')
    sales_office = fields.Char(string='Sales Office')
    department_name = fields.Char(string='Department')
    contact_person_id = fields.Many2one('res.users', string='Contact Person')
    activity_person_id = fields.Many2one('res.users', string='Activity Person')
    
    # Customer Details (Extended)
    customer_pid = fields.Char(string='TC/National ID')
    customer_passport = fields.Char(string='Passport No')
    father_name = fields.Char(string='Father Name')
    spouse_name = fields.Char(string='Spouse Name')
    accounting_code = fields.Char(string='Accounting Code')
    status_detail = fields.Char(string='Status Detail')
    is_vip = fields.Boolean(string='VIP Customer')
    vip_note = fields.Text(string='VIP Note')
    
    # Contract Details
    contract_no = fields.Char(string='Manual Contract No')
    contract_date = fields.Date(string='Contract Date', default=fields.Date.context_today)
    notary_date = fields.Datetime(string='Notary Date')
    notary_no = fields.Char(string='Notary Ref No')
    is_notarized = fields.Boolean(string='Notarized?')
    notary_note = fields.Text(string='Notary Note')
    
    # Financial Details
    payment_method_type = fields.Char(string='Payment Method Detail') # e.g. "Cash + Installment"
    bank_approved = fields.Boolean(string='Bank Validated?')
    bank_approval_date = fields.Date(string='Bank Approval Date')
    discount_amount = fields.Monetary(string='Discount Amount', currency_field='currency_id')
    calc_discount_amount = fields.Monetary(string='Calc. Discount', currency_field='currency_id')
    maturity_diff = fields.Monetary(string='Maturity Diff.', currency_field='currency_id')
    calc_maturity_diff = fields.Monetary(string='Calc. Maturity Diff.', currency_field='currency_id')
    invoice_status = fields.Selection([('to_invoice', 'To Invoice'), ('invoiced', 'Invoiced')], string='Invoice Status')
    
    bank_doc_status = fields.Selection([
        ('none', 'None'),
        ('prepared', 'Prepared'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Bank Doc Status', default='none')
    
    reserve_date = fields.Date(string='Reserve Date')
    credit_usage_date = fields.Date(string='Credit Usage Date')
    
    feature_balcony_notes = fields.Char(string='Balcony Details (Ref: ES.KRK-01)')
    feature_window_notes = fields.Char(string='Window Details (Ref: ES.KRK-02)')
    
    # Exchange Rates Snapshot
    rate_tcmb = fields.Float(string='TCMB Rate', digits=(12, 6))
    rate_down_payment = fields.Float(string='Down Payment Rate', digits=(12, 6))
    rate_installment = fields.Float(string='Installment Rate', digits=(12, 6))
    
    group_customer_names = fields.Text(string='Group Customer Names')
    credit_term = fields.Integer(string='Credit Term (Months)')
    is_project_active = fields.Boolean(string='Project Active?', default=True)
    
    date_sale = fields.Date(string='Sale Date', default=fields.Date.context_today, required=True)
    
    installment_ids = fields.One2many('propertio.installment', 'sale_id', string='Payment Plan')
    
    total_paid = fields.Monetary(string='Total Paid', compute='_compute_totals', store=True)
    balance = fields.Monetary(string='Balance', compute='_compute_totals', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.depends('installment_ids.amount', 'installment_ids.amount_paid')
    def _compute_totals(self):
        for record in self:
            paid = sum(inst.amount_paid for inst in record.installment_ids)
            total = sum(inst.amount for inst in record.installment_ids)
            record.total_paid = paid
            record.balance = record.sale_price - paid

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('propertio.sale') or 'New'
        return super(PropertioSale, self).create(vals_list)
    
    def action_rebalance_plan(self):
        """ Checks total vs price and creates a balancing installment or adjusts the last one """
        self.ensure_one()
        current_total = sum(self.installment_ids.mapped('amount'))
        diff = self.sale_price - current_total
        
        if abs(diff) > 0.01:
            last_date = fields.Date.context_today(self)
            if self.installment_ids:
                sorted_inst = self.installment_ids.sorted('date_due')
                last_date = sorted_inst[-1].date_due
            
            self.env['propertio.installment'].create({
                'sale_id': self.id,
                'name': 'Balance Adjustment',
                'date_due': last_date,
                'amount': diff,
                'type': 'balloon',
                'sequence': 999
            })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            record.unit_id.state = 'sold'

    def action_view_installments(self):
        self.ensure_one()
        return {
            'name': 'Installments & Collections',
            'type': 'ir.actions.act_window',
            'res_model': 'propertio.installment',
            'view_mode': 'list,graph,pivot,form',
            'domain': [('sale_id', '=', self.id)],
            'context': {'default_sale_id': self.id},
            'target': 'current',
        }

    def action_view_unit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'propertio.unit',
            'view_mode': 'form',
            'res_id': self.unit_id.id,
            'target': 'current',
        }

    def action_view_customer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.partner_id.id,
            'res_id': self.partner_id.id,
            'target': 'current',
        }


    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'Actual Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'propertio.payment',
            'view_mode': 'list,form',
            'domain': [('sale_id', '=', self.id)],
            'context': {'default_sale_id': self.id, 'default_partner_id': self.partner_id.id},
            'target': 'current',
        }

    def action_download_word(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/propertio/contract_word/{self.id}',
            'target': 'self',
        }

    def action_print_contract_html(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/report/html/tcrm_propertio.report_contract_document/{self.id}',
            'target': 'new',
        }

    def name_get(self):
        result = []
        for sale in self:
            name = f"#{sale.name} | {sale.partner_id.name} - {sale.unit_id.name}"
            result.append((sale.id, name))
        return result

    def action_export_batch_word(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/propertio/contract_word/batch?ids={",".join(map(str, self.ids))}',
            'target': 'self',
        }

    def action_download_pdf(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/propertio/contract_pdf/{self.id}',
            'target': 'self',
        }

    def action_open_full_screen(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'propertio.sale',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }



class PropertioSaleStage(models.Model):
    _name = 'propertio.sale.stage'
    _description = 'Sale Stage'
    _order = 'sequence'
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    properties_definition = fields.PropertiesDefinition('Contract Details View')


class PropertioInstallment(models.Model):
    _name = 'propertio.installment'
    _description = 'Payment Installment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, date_due'

    sale_id = fields.Many2one('propertio.sale', string='Sale Contract', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    partner_id = fields.Many2one('res.partner', related='sale_id.partner_id', string='Customer', store=True)
    name = fields.Char(string='Description', required=True) # e.g. "Down Payment", "Installment 1/12"
    payment_method = fields.Char(string='Payment Method Detail', related='sale_id.payment_method_type')
    
    date_due = fields.Date(string='Due Date', required=True)
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='sale_id.currency_id', readonly=True)
    
    amount_paid = fields.Monetary(string='Paid Amount', currency_field='currency_id', tracking=True)
    residual = fields.Monetary(string='Residual', compute='_compute_residual', store=True, currency_field='currency_id')
    is_paid = fields.Boolean(string='Paid', compute='_compute_residual', store=True, tracking=True)
    
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('upcoming', 'Upcoming'),
        ('future', 'Future')
    ], string='Payment Status', compute='_compute_payment_status', store=True)

    type = fields.Selection([
        ('down_payment', 'Down Payment'),
        ('installment', 'Installment'),
        ('balloon', 'Balloon Payment')
    ], string='Type', default='installment')

    @api.depends('amount', 'amount_paid')
    def _compute_residual(self):
        for record in self:
            record.residual = record.amount - record.amount_paid
            if abs(record.residual) < 0.01: # Float tolerance
                record.residual = 0.0
                record.is_paid = True
            else:
                record.is_paid = False

    @api.depends('is_paid', 'date_due')
    def _compute_payment_status(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.is_paid:
                record.payment_status = 'paid'
            elif record.date_due < today:
                record.payment_status = 'overdue'
            elif record.date_due <= today + relativedelta(days=30):
                record.payment_status = 'upcoming'
            else:
                record.payment_status = 'future'



