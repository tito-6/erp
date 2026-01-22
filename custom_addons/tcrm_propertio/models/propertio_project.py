from tcrm import models, fields

class PropertioProject(models.Model):
    _name = 'propertio.project'
    _description = 'Real Estate Project'
    _order = 'name'

    name = fields.Char(string='Project Name', required=True, index=True)
    city = fields.Char(string='City', index=True)
    type_id = fields.Many2one('propertio.project.type', string='Project Type')
    stage_id = fields.Many2one('propertio.project.stage', string='Stage')
    properties = fields.Properties('Properties', definition='type_id.properties_definition')
    
    gdv = fields.Monetary(string='Gross Development Value', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    block_ids = fields.One2many('propertio.block', 'project_id', string='Blocks')
    unit_ids = fields.One2many('propertio.unit', 'project_id', string='Units')
    unit_count = fields.Integer(string='Total Units', compute='_compute_unit_count')
    
    standard_feature_ids = fields.Many2many('propertio.feature', 'project_standard_feature_rel', 
                                          'project_id', 'feature_id', string='Standard Amenities')
    extra_feature_ids = fields.Many2many('propertio.feature', 'project_extra_feature_rel', 
                                        'project_id', 'feature_id', string='Available Upgrades')

    def _compute_unit_count(self):
        for record in self:
            record.unit_count = self.env['propertio.unit'].search_count([('project_id', '=', record.id)])

class PropertioProjectType(models.Model):
    _name = 'propertio.project.type'
    _description = 'Project Type'
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    properties_definition = fields.PropertiesDefinition('Unit Properties')

class PropertioProjectStage(models.Model):
    _name = 'propertio.project.stage'
    _description = 'Project Stage'
    _order = 'sequence'
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

class PropertioBlock(models.Model):
    _name = 'propertio.block'
    _description = 'Project Block'
    _order = 'name'

    name = fields.Char(string='Block Name', required=True)
    project_id = fields.Many2one('propertio.project', string='Project', required=True, ondelete='cascade')
    unit_ids = fields.One2many('propertio.unit', 'block_id', string='Units')
