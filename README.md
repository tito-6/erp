# TCRM - Multi-Tenant SaaS Platform

**Connect . Grow . Win**

A white-labeled, multi-tenant SaaS platform based on Odoo Community Edition, fully customized with TCRM branding.

## Features

- ✅ **Complete TCRM Branding**: Deep Blue (#101E55) and Navy (#0e142c) color scheme
- ✅ **Custom Typography**: Bricolage Grotesque font family
- ✅ **Multi-Tenancy**: Isolated databases per client with automated provisioning
- ✅ **SaaS Core Module**: `tcrm_saas_core` for tenant management
- ✅ **Professional UI**: Modern, clean interface with custom logos and favicons

## Installation

### Prerequisites

- Python 3.10
- PostgreSQL 16
- Windows OS (native support)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tito-6/erp.git
   cd erp
   ```

2. **Create virtual environment:**
   ```bash
   py -3.10 -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install psycopg2-binary pypiwin32
   pip install -r odoo-src\requirements.txt
   ```

4. **Start PostgreSQL:**
   ```bash
   & "C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe" -D "C:\D\crm\db_data" -l "C:\D\crm\db.log" -o "-p 5433" start
   ```

5. **Initialize master database:**
   ```bash
   .\venv\Scripts\python odoo-src\odoo-bin -c tcrm.conf -d tcrm_master -i base --without-demo=all --stop-after-init
   ```

6. **Start TCRM server:**
   ```bash
   .\venv\Scripts\python odoo-src\odoo-bin -c tcrm.conf
   ```

## Access

- **URL:** `http://localhost:8069`
- **Email:** `admin`
- **Password:** `admin`
- **Master Password:** `admin`

## Configuration

The `tcrm.conf` file contains:
- Database filter: `tcrm_master`
- HTTP port: `8069`
- PostgreSQL port: `5433`
- Custom addons path: `custom_addons`

## Project Structure

```
C:\D\crm\
├── odoo-src/              # Odoo source code (modified)
├── custom_addons/         # TCRM custom modules
│   └── tcrm_saas_core/   # SaaS tenant management
├── TCRM/                  # Brand assets (logos, fonts)
├── db_data/               # PostgreSQL data directory
├── tcrm.conf              # Odoo configuration
└── venv/                  # Python virtual environment
```

## Branding

### Colors
- **Deep Blue**: #101E55 (Primary brand color)
- **Navy**: #0e142c (Buttons and accents)
- **Action Red**: #E00000 (Reserved for alerts)

### Typography
- **Primary Font**: Bricolage Grotesque
- **Fallback**: SF Pro Display, System fonts

### Assets
- Favicon: `icon-2.png`
- Logo: `LOGO-png.png`
- Icon: `icon.svg`

## Modules

### tcrm_saas_core
Multi-tenant SaaS management module with:
- Tenant model (`tcrm.tenant`)
- Automatic database creation
- Client subscription management
- Isolated data per tenant

## Development

### Updating Web Assets
After modifying SCSS or JS files:
```bash
.\venv\Scripts\python odoo-src\odoo-bin -c tcrm.conf -d tcrm_master -u web --stop-after-init
```

### Creating New Tenant
Access TCRM Master menu → Tenants → Create

## License

Based on Odoo Community Edition (LGPL-3)
TCRM Customizations © 2026

## Support

For issues or questions, contact the TCRM development team.

---

**TCRM** - Connect . Grow . Win
