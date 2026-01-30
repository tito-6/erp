from tcrm import models, fields, api, _
from tcrm.exceptions import UserError

class PropertioPayment(models.Model):
    _name = 'propertio.payment'
    _description = 'Property Collection/Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payment_date desc'

    name = fields.Char(string='Payment Ref', required=True, copy=False, readonly=True, default='New')
    
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    sale_id = fields.Many2one('propertio.sale', string='Sale Contract', required=True, domain="[('partner_id', '=', partner_id)]")
    
    amount = fields.Monetary(string='Amount Paid', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Payment Currency', required=True, default=lambda self: self.env.company.currency_id)
    
    payment_method = fields.Selection([
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('senet', 'Senet (Promissory Note)')
    ], string='Method', required=True, default='bank')
    
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.context_today)
    
    # Exchange Rate Logic
    # We store the rate used: how many [Sale Currency] units does 1 [Payment Currency] unit buy?
    # Or typically: Sale Currency Amount = Payment Amount * Rate (if rate is defined as Pay -> Sale)
    # Let's use TCRM standard: Rate = 1 / rate in database usually.
    # Let's make it simple for the user: "Covered Amount in Sale Currency"
    
    exchange_rate = fields.Float(string='Exchange Rate', digits=(12, 6), help="Rate to convert Payment Currency to Sale Currency", default=1.0)
    covered_amount = fields.Monetary(string='Covered Amount (Sale Curr)', currency_field='sale_currency_id', compute='_compute_covered_amount', store=True, readonly=False)
    sale_currency_id = fields.Many2one('res.currency', related='sale_id.currency_id', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.onchange('payment_date', 'currency_id', 'sale_id')
    def _onchange_rate(self):
        if self.currency_id and self.sale_id and self.payment_date:
            if self.currency_id == self.sale_id.currency_id:
                self.exchange_rate = 1.0
            else:
                # Fetch rate from database for payment_date
                # We need conversion: Payment -> Sale
                # TCRM conversion: amount_to_text = currency_id._convert(amount, sale_currency, company, date)
                # We want the rate factor.
                
                # Check if we have TCMB rate integration?
                # The prompt implies we should auto-fetch or match.
                # Assuming _convert handles it if rates are in system.
                
                # Let's derive rate from _convert of 1.0 unit
                rate = self.currency_id._convert(1.0, self.sale_id.currency_id, self.env.company, self.payment_date)
                self.exchange_rate = rate

    @api.depends('amount', 'exchange_rate')
    def _compute_covered_amount(self):
        for record in self:
            record.covered_amount = record.amount * record.exchange_rate

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('propertio.payment') or 'New'
        return super(PropertioPayment, self).create(vals_list)

    def action_post(self):
        for record in self:
            if record.amount <= 0:
                raise UserError(_("Payment amount must be positive."))
            
            # Allocation Logic (FIFO)
            to_allocate = record.covered_amount
            
            # Find unpaid installments, sorted by date
            installments = self.env['propertio.installment'].search([
                ('sale_id', '=', record.sale_id.id),
                ('is_paid', '=', False)
            ], order='date_due asc')
            
            for inst in installments:
                if to_allocate <= 0:
                    break
                
                needed = inst.residual
                if to_allocate >= needed:
                    # Fully cover this installment
                    inst.amount_paid += needed
                    to_allocate -= needed
                else:
                    # Partial cover
                    inst.amount_paid += to_allocate
                    to_allocate = 0
            
            # If to_allocate > 0, it means overpayment? 
            # For now, we ignore or leave it as extra? 
            # Spec doesn't define overpayment. We just stop when installments are exhausted.
            # Real world: Create a "Credit Note" or "Advance". For MVP, we simply update state.
            
            record.state = 'posted'

    def action_cancel(self):
        for record in self:
            # Revert allocation?
            # Complex to track exactly WHICH installments were paid by THIS payment if multiple payments exist.
            # To handle this properly, we'd need a Many2many or One2many link table "propertio.installment.payment.rel"
            # keeping track of (payment_id, installment_id, amount_allocated).
            # The prompt request is relatively high-level ("Automation: ... Knock Off"). 
            # I will omit strict Revert logic for this MVP step unless requested, as it requires a Join Table.
            # For strict correctness, I'll block cancel if it was posted, or implement the join table.
            # Given constraints and prompt style ("Propertio - The Real Estate Engine"), a Join Table is better Architecture.
            pass
        # Implementing Join Table logic in next step if needed, or keeping simple for now. 
        # Simplicity First: Block Cancel for now.
        raise UserError(_("Cannot cancel posted payments in this version. Request Admin assistance."))
