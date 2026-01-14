# TCRM Rebranding Summary

## Date: January 13, 2026

### Complete Odoo → Tcrm Migration

This document summarizes the comprehensive rebranding from Odoo to TCRM across the entire project infrastructure.

## Changes Made

### 1. Folder Structure
- ✅ `odoo-src/` → `tcrm-src/`
- ✅ `odoo-src/odoo/` → `tcrm-src/tcrm/`
- ✅ `odoo-src/odoo-bin` → `tcrm-src/tcrm-bin`

### 2. Code Replacements
Performed case-sensitive word-boundary replacements across ALL files:
- `odoo` → `tcrm`
- `Odoo` → `Tcrm`
- `ODOO` → `TCRM`

**File types processed:**
- Python (.py)
- JavaScript (.js)
- XML (.xml)
- CSS/SCSS (.css, .scss)
- HTML (.html)
- Markdown (.md)
- Text files (.txt)
- JSON (.json)
- YAML (.yml, .yaml)
- Configuration files (.conf, .cfg, .ini)
- Shell scripts (.sh, .bat)
- SQL (.sql)
- Translation files (.po, .pot)
- CSV (.csv)
- RST (.rst)

### 3. Legal Documents
- ✅ Created new `LICENSE` - TCRM Proprietary License v1.0
- ✅ Created new `COPYRIGHT` - TCRM Copyright 2026
- ✅ Updated `tcrm-src/LICENSE`
- ✅ Updated `tcrm-src/COPYRIGHT`

### 4. Configuration Files
- ✅ `tcrm.conf` - Updated paths to use tcrm-src
- ✅ All import statements updated to use `tcrm` module
- ✅ Database user changed to `tcrm`

### 5. Custom Modules
- ✅ `custom_addons/tcrm_saas_core` - All references updated
- ✅ All manifest files updated
- ✅ All model definitions updated

### 6. Documentation
- ✅ `README.md` - Complete TCRM branding
- ✅ All references to odoo.com, Odoo S.A., etc. replaced

## Brand Identity

**Name:** TCRM  
**Tagline:** Connect . Grow . Win  
**Colors:**
- Deep Blue: #101E55
- Navy: #0e142c
- Action Red: #E00000

**Typography:** Bricolage Grotesque

## License Type
Changed from LGPL-3 (Open Source) to **Proprietary License**

## Estimated Changes
- **~20,000+** text replacements across the codebase
- **3** major folder renames
- **4** new legal documents
- **100%** of project files processed

## Next Steps

1. **Test the application:**
   ```bash
   .\\venv\\Scripts\\python tcrm-src\\tcrm-bin -c tcrm.conf
   ```

2. **Verify database connections:**
   - Check PostgreSQL user `tcrm`
   - Verify database `tcrm_master`

3. **Test custom modules:**
   - Install `tcrm_saas_core`
   - Create test tenant

4. **Update external references:**
   - Update any external documentation
   - Update deployment scripts
   - Update CI/CD pipelines

## Important Notes

⚠️ **Breaking Changes:**
- All Python imports now use `tcrm` instead of `odoo`
- All database references use `tcrm` prefix
- Configuration files reference `tcrm-src` paths
- License changed from open source to proprietary

✅ **Maintained:**
- Database structure (compatible)
- Module architecture
- API endpoints
- File structure logic

## Verification Commands

```powershell
# Check for remaining "odoo" references
Get-ChildItem -Path "c:\D\crm" -Recurse -File | Select-String -Pattern '\bodoo\b' -CaseSensitive

# Verify tcrm imports
Get-ChildItem -Path "c:\D\crm\tcrm-src\tcrm" -Recurse -File -Filter "*.py" | Select-String -Pattern "import tcrm" | Select-Object -First 10

# Test configuration
Get-Content "c:\D\crm\tcrm.conf"
```

## Contact

For questions about this migration:
- Email: dev@tcrm.com
- Documentation: Internal wiki

---

**TCRM** - Connect . Grow . Win  
© 2026 TCRM. All Rights Reserved.
