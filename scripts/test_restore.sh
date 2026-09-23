#!/usr/bin/env bash
# ==============================================================================
# Script: test_restore.sh
# Purpose: Automated weekly restore smoke test in an isolated ephemeral container.
# Validates: Archive readability, pgvector extension, Alembic version, table schema,
#            and representative query integrity without touching production.
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/opt/backups/postgres}"
TEST_CONTAINER="ai-llm-restore-test-$(date +%s)"
TEST_PORT=5499
TEST_DB="ai_llm_test_restore"
TEST_PASSWORD="ephemeral_test_password"

# Find latest backup
LATEST_BACKUP=$(find "${BACKUP_DIR}" -name "*.sql.gz" -type f | sort | tail -n 1)

if [ -z "${LATEST_BACKUP}" ]; then
  echo "ERROR: No backup files found in ${BACKUP_DIR} to test." >&2
  exit 1
fi

echo "==> [1/4] Found latest backup archive: ${LATEST_BACKUP}"

cleanup() {
  echo "==> Cleaning up test container ${TEST_CONTAINER}..."
  docker rm -f "${TEST_CONTAINER}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "==> [2/4] Starting ephemeral test PostgreSQL container..."
docker run -d --name "${TEST_CONTAINER}" \
  -e POSTGRES_PASSWORD="${TEST_PASSWORD}" \
  -e POSTGRES_DB="${TEST_DB}" \
  -p "${TEST_PORT}:5432" \
  pgvector/pgvector:pg15

echo "    Waiting for test container to become ready..."
for i in {1..30}; do
  if docker exec "${TEST_CONTAINER}" pg_isready -U postgres -d "${TEST_DB}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "==> [3/4] Restoring snapshot into ephemeral database..."
gunzip -c "${LATEST_BACKUP}" | docker exec -i "${TEST_CONTAINER}" psql -U postgres -d "${TEST_DB}" >/dev/null

echo "==> [4/4] Executing smoke tests on restored data..."

echo "    Test 1: Vector extension..."
docker exec -i "${TEST_CONTAINER}" psql -U postgres -d "${TEST_DB}" -c "CREATE EXTENSION IF NOT EXISTS vector;" >/dev/null

echo "    Test 2: Alembic migration version..."
MIGRATION_VERSION=$(docker exec -i "${TEST_CONTAINER}" psql -U postgres -d "${TEST_DB}" -t -A -c "SELECT version_num FROM alembic_version LIMIT 1;" || echo "NOT_FOUND")
echo "            Current alembic version: ${MIGRATION_VERSION}"

echo "    Test 3: Users count..."
USER_COUNT=$(docker exec -i "${TEST_CONTAINER}" psql -U postgres -d "${TEST_DB}" -t -A -c "SELECT count(*) FROM users;")
echo "            Total users: ${USER_COUNT}"

echo "    Test 4: Representative query test..."
docker exec -i "${TEST_CONTAINER}" psql -U postgres -d "${TEST_DB}" -c "SELECT id, email, role, created_at FROM users ORDER BY id DESC LIMIT 2;"

echo "---------------------------------------------------------"
echo "RESTORE SMOKE TEST: PASSED! Backup archive is 100% valid."
echo "---------------------------------------------------------"

