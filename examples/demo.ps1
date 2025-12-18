Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$db = Join-Path $PSScriptRoot "hotelmanager.demo.db"

Write-Host "== HotelManager Demo (PowerShell) ==" -ForegroundColor Cyan
Write-Host "DB: $db"

python -m hotelmanager init --db $db

python -m hotelmanager room add --number 101 --type single --capacity 1 --price 399.00 --db $db
python -m hotelmanager room add --number 102 --type double --capacity 2 --price 599.00 --db $db

python -m hotelmanager guest add --name "Alice" --email "alice@example.com" --phone "13800000000" --db $db

python -m hotelmanager booking quote --room 101 --start 2025-12-20 --end 2025-12-22 --db $db
python -m hotelmanager booking create --room 101 --guest-email "alice@example.com" --start 2025-12-20 --end 2025-12-22 --db $db

Write-Host "`n== booking list ==" -ForegroundColor Cyan
python -m hotelmanager booking list --db $db

Write-Host "`n== booking list (overlap filter) ==" -ForegroundColor Cyan
python -m hotelmanager booking list --from 2025-12-21 --to 2025-12-23 --db $db

Write-Host "`n== reschedule ==" -ForegroundColor Cyan
python -m hotelmanager booking reschedule --id 1 --start 2025-12-24 --end 2025-12-26 --db $db

Write-Host "`n== stats revenue ==" -ForegroundColor Cyan
python -m hotelmanager stats revenue --start 2025-12-20 --end 2025-12-30 --db $db

Write-Host "`n== export bookings CSV ==" -ForegroundColor Cyan
python -m hotelmanager export bookings --db $db

Write-Host "`nDemo finished." -ForegroundColor Green

