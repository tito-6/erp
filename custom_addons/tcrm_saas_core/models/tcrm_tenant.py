from tcrm import models, fields, api
import tcrm.service.db
import logging

_logger = logging.getLogger(__name__)

class TcRmTenant(models.Model):
    _name = 'tcrm.tenant'
    _description = 'TCRM Tenant'

    name = fields.Char(string='Subdomain / Database', required=True, help="Database name (will be used for dbfilter)")
    client_name = fields.Char(string='Client Name')
    active = fields.Boolean(default=True)
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active')], default='draft')

    @api.model
    def create(self, vals):
        record = super(TcRmTenant, self).create(vals)
        if vals.get('name'):
            self._create_tenant_db(vals['name'])
        return record

    def _create_tenant_db(self, db_name):
        if tcrm.service.db.exp_db_exist(db_name):
            _logger.warning(f"Database {db_name} already exists.")
            return

        try:
            _logger.info(f"Creating database {db_name}...")
            # Create DB with admin password 'admin' (default for now)
            # Note: In production, use strong passwords and storing them securely.
            tcrm.service.db.exp_create_database(db_name, demo=False, lang='en_US')
            _logger.info(f"Database {db_name} created successfully.")
            
            # Optional: Install base modules using exp_install_module?
            # Or just let it be handled by Tcrm's auto-init?
            # Generally exp_create_database installs base.
            
        except Exception as e:
            _logger.error(f"Failed to create database {db_name}: {e}")
