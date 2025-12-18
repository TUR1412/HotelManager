#!/usr/bin/env bash
set -euo pipefail

DB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/hotelmanager.demo.db"

echo "== HotelManager Demo (bash) =="
echo "DB: $DB"

python -m hotelmanager init --db "$DB"

python -m hotelmanager room add --number 101 --type single --capacity 1 --price 399.00 --db "$DB"
python -m hotelmanager room add --number 102 --type double --capacity 2 --price 599.00 --db "$DB"

python -m hotelmanager guest add --name "Alice" --email "alice@example.com" --phone "13800000000" --db "$DB"

python -m hotelmanager booking quote --room 101 --start 2025-12-20 --end 2025-12-22 --db "$DB"
python -m hotelmanager booking create --room 101 --guest-email "alice@example.com" --start 2025-12-20 --end 2025-12-22 --db "$DB"

echo ""
echo "== booking list =="
python -m hotelmanager booking list --db "$DB"

echo ""
echo "== booking list (overlap filter) =="
python -m hotelmanager booking list --from 2025-12-21 --to 2025-12-23 --db "$DB"

echo ""
echo "== reschedule =="
python -m hotelmanager booking reschedule --id 1 --start 2025-12-24 --end 2025-12-26 --db "$DB"

echo ""
echo "== stats revenue =="
python -m hotelmanager stats revenue --start 2025-12-20 --end 2025-12-30 --db "$DB"

echo ""
echo "== export bookings CSV =="
python -m hotelmanager export bookings --db "$DB"

echo ""
echo "Demo finished."

