#!/usr/bin/env bash
# Apply migrations to a throwaway Postgres database and run the RLS test.
# Usage: supabase/tests/run.sh   (needs psql and PG* env vars or a local superuser)
set -euo pipefail
cd "$(dirname "$0")/.."
DB=${TEST_DB:-lab_rls_test}
dropdb --if-exists "$DB" && createdb "$DB"
psql -q -v ON_ERROR_STOP=1 -d "$DB" -f tests/00_supabase_stub.sql
for f in migrations/*.sql; do psql -q -v ON_ERROR_STOP=1 -d "$DB" -f "$f"; done
psql -q -v ON_ERROR_STOP=1 -d "$DB" -f tests/rls_test.sql
dropdb "$DB"
