# TCRM Verification Script
# Run this to verify the rebranding was successful

Write-Host "=== TCRM Rebranding Verification ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check folder structure
Write-Host "1. Checking folder structure..." -ForegroundColor Yellow
$folders = @(
    "c:\D\crm\tcrm-src",
    "c:\D\crm\tcrm-src\tcrm",
    "c:\D\crm\custom_addons"
)
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Write-Host "   ✓ $folder exists" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $folder NOT FOUND" -ForegroundColor Red
    }
}

# 2. Check key files
Write-Host ""
Write-Host "2. Checking key files..." -ForegroundColor Yellow
$files = @(
    "c:\D\crm\tcrm-src\tcrm-bin",
    "c:\D\crm\tcrm.conf",
    "c:\D\crm\LICENSE",
    "c:\D\crm\COPYRIGHT"
)
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file NOT FOUND" -ForegroundColor Red
    }
}

# 3. Check for old "odoo" folder
Write-Host ""
Write-Host "3. Checking for old odoo folders..." -ForegroundColor Yellow
if (Test-Path "c:\D\crm\odoo-src") {
    Write-Host "   ✗ WARNING: odoo-src folder still exists!" -ForegroundColor Red
} else {
    Write-Host "   ✓ No odoo-src folder found" -ForegroundColor Green
}

# 4. Verify imports in tcrm-bin
Write-Host ""
Write-Host "4. Verifying tcrm-bin imports..." -ForegroundColor Yellow
$binContent = Get-Content "c:\D\crm\tcrm-src\tcrm-bin" -Raw
if ($binContent -match "import tcrm") {
    Write-Host "   ✓ tcrm-bin uses 'import tcrm'" -ForegroundColor Green
} else {
    Write-Host "   ✗ tcrm-bin does NOT import tcrm correctly" -ForegroundColor Red
}

# 5. Check configuration file
Write-Host ""
Write-Host "5. Verifying configuration..." -ForegroundColor Yellow
$confContent = Get-Content "c:\D\crm\tcrm.conf" -Raw
if ($confContent -match "tcrm-src") {
    Write-Host "   ✓ tcrm.conf references tcrm-src" -ForegroundColor Green
} else {
    Write-Host "   ✗ tcrm.conf does NOT reference tcrm-src" -ForegroundColor Red
}

# 6. Count remaining "odoo" references
Write-Host ""
Write-Host "6. Counting remaining 'odoo' references..." -ForegroundColor Yellow
Write-Host "   (This may take a moment...)" -ForegroundColor Gray
$odooCount = (Get-ChildItem -Path "c:\D\crm\tcrm-src" -Recurse -File -Include *.py,*.xml,*.js | 
              Select-String -Pattern '\bodoo\b' -CaseSensitive | 
              Measure-Object).Count
Write-Host "   Found $odooCount instances of 'odoo' in code files" -ForegroundColor $(if ($odooCount -lt 100) { "Green" } else { "Yellow" })

# 7. Check license
Write-Host ""
Write-Host "7. Verifying license..." -ForegroundColor Yellow
$licenseContent = Get-Content "c:\D\crm\LICENSE" -Raw
if ($licenseContent -match "TCRM PROPRIETARY") {
    Write-Host "   ✓ LICENSE is TCRM Proprietary" -ForegroundColor Green
} else {
    Write-Host "   ✗ LICENSE is NOT TCRM Proprietary" -ForegroundColor Red
}

# 8. Summary
Write-Host ""
Write-Host "=== Verification Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the application: .\\venv\\Scripts\\python tcrm-src\\tcrm-bin -c tcrm.conf"
Write-Host "2. Check database connectivity"
Write-Host "3. Verify custom modules load correctly"
Write-Host ""
