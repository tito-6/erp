from tcrm import models, fields, api

class PropertioUnit(models.Model):
    _name = 'propertio.unit'
    _description = 'Real Estate Unit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project_id, block_id, unit_number'
    # Use name_search or display_name to show Project - Block - Unit

    name = fields.Char(string='Unit Number', required=True, index=True)
    unit_number = fields.Char(string='Unit No', related='name', store=True) # visual alias
    
    project_id = fields.Many2one('propertio.project', string='Project', required=True, index=True)
    block_id = fields.Many2one('propertio.block', string='Block', domain="[('project_id', '=', project_id)]", index=True)
    
    floor = fields.Char(string='Floor')
    entrance = fields.Char(string='Entrance')
    view_type = fields.Char(string='View') # e.g. "Sea View", "Garden"
    
    gross_m2 = fields.Float(string='Gross M²', digits=(10, 2))
    net_m2 = fields.Float(string='Net M²', digits=(10, 2))
    general_gross_m2 = fields.Float(string='General Gross M²', digits=(10, 2), help="Common areas included")
    balcony_m2 = fields.Float(string='Balcony M²', digits=(10, 2))
    terrace_m2 = fields.Float(string='Terrace M²', digits=(10, 2))
    garden_m2 = fields.Float(string='Garden M²', digits=(10, 2))
    floor_gross_m2 = fields.Float(string='Floor Gross M²', digits=(10, 2))
    ground_floor_m2 = fields.Float(string='Ground Floor M²', digits=(10, 2))
    normal_floor_m2 = fields.Float(string='Normal Floor M²', digits=(10, 2))
    
    facade = fields.Char(string='Facade', help="North, South, etc.")
    parking_no = fields.Char(string='Parking Slot No')
    parking_type = fields.Selection([('open', 'Open'), ('closed', 'Closed')], string='Parking Type')
    
    unit_code = fields.Char(string='Unit Code')
    tapu_ref = fields.Char(string='Tapu (Title Deed) Ref')
    accounting_code = fields.Char(string='Accounting Code')
    category_id = fields.Many2one('propertio.unit.category', string='Property Category')
    status_id = fields.Many2one('propertio.unit.status', string='Custom Status')
    properties = fields.Properties('Custom Attributes', definition='category_id.properties_definition')
    
    state = fields.Selection([
        ('available', 'Available'),
        ('option', 'Option'),
        ('sold', 'Sold'),
        ('handover', 'Handover')
    ], string='Status', default='available', required=True, index=True, tracking=True)
    
    list_price = fields.Monetary(string='List Price', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='project_id.currency_id', readonly=True)
    
    standard_feature_ids = fields.Many2many('propertio.feature', 'unit_standard_feature_rel', 
                                            'unit_id', 'feature_id', string='Standard Amenities')
    extra_feature_ids = fields.Many2many('propertio.feature', 'unit_extra_feature_rel', 
                                        'unit_id', 'feature_id', string='Addable Features')
    
    # Digital Assets / Media
    # In the view, use <field name="attachment_ids" widget="many2many_binary"/> or standard attachment box
    # If a specific relationship is needed for the "Digital Assets" tab logic:
    attachment_ids = fields.Many2many('ir.attachment', string='Digital Assets', help='Attach Catalogs, Factsheets, Renders here.')

    # Reporting Fields
    sale_ids = fields.One2many('propertio.sale', 'unit_id', string='Sales History')
    current_sale_id = fields.Many2one('propertio.sale', compute='_compute_sale_metrics', store=True)
    
    sold_value = fields.Monetary(string='Sold Value', compute='_compute_sale_metrics', store=True, currency_field='currency_id')
    collected_amount = fields.Monetary(string='Collected', compute='_compute_sale_metrics', store=True, currency_field='currency_id')
    receivable_amount = fields.Monetary(string='Receivable', compute='_compute_sale_metrics', store=True, currency_field='currency_id')

    @api.depends('sale_ids.state', 'sale_ids.sale_price', 'sale_ids.total_paid')
    def _compute_sale_metrics(self):
        for unit in self:
            # Find active sale (confirmed or draft if no confirmed? standard is confirmed)
            # Logic: Last confirmed sale, or last draft if none.
            # Ideally state='sold' implies confirmed sale.
            active_sale = unit.sale_ids.filtered(lambda s: s.state == 'confirmed')
            # Take the latest one
            sale = active_sale[:1]
            
            unit.current_sale_id = sale.id
            if sale:
                unit.sold_value = sale.sale_price
                unit.collected_amount = sale.total_paid
                unit.receivable_amount = sale.balance
            else:
                unit.sold_value = 0.0
                unit.collected_amount = 0.0
                unit.receivable_amount = 0.0

    def name_get(self):
        result = []
        for unit in self:
            name = f"{unit.project_id.name} - {unit.block_id.name} - {unit.name}" if unit.block_id else f"{unit.project_id.name} - {unit.name}"
            result.append((unit.id, name))
        return result

    def action_view_sales_history(self):
        self.ensure_one()
        return {
            'name': 'Sales History',
            'type': 'ir.actions.act_window',
            'res_model': 'propertio.sale',
            'view_mode': 'list,form',
            'domain': [('unit_id', '=', self.id)],
            'context': {'default_unit_id': self.id},
            'target': 'current',
        }

class PropertioFeature(models.Model):
    _name = 'propertio.feature'
    _description = 'Unit Feature'

    name = fields.Char(string='Feature', required=True)
    color = fields.Integer(string='Color')
    icon = fields.Char(string='Icon Class', help="FontAwesome class, e.g. fa-swimming-pool")

class PropertioUnitCategory(models.Model):
    _name = 'propertio.unit.category'
    _description = 'Unit Category'
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    properties_definition = fields.PropertiesDefinition('Extra Attributes')

class PropertioUnitStatus(models.Model):
    _name = 'propertio.unit.status'
    _description = 'Unit Detailed Status'
    name = fields.Char(required=True)
    color = fields.Integer(string='Color')
    active = fields.Boolean(default=True)
