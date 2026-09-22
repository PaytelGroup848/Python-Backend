#!/usr/bin/env bash
# ==============================================================================
# Script: backup_database.sh
# Purpose: Production-grade automated PostgreSQL backup with concurrency locking,
#          dynamic disk pre-check, gzip verification, and off-host DR sync.
# ==============================================================================

set -euo pipefail

LOCK_FILE="/var/lock/patwatoli_db_backup.lock"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/postgres}"
CONTAINER_NAME="ai-llm-postgres"
DB_NAME="ai_llm_db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

# 1. Concurrency Locking
exec 200>"${LOCK_FILE}"
if ! flock -n 200; then
  echo "WARNING: Backup job is already running. Exiting." >&2
  exit 0
fi

mkdir -p "${BACKUP_DIR}"

echo "==> [1/5] Checking disk space pre-requisites..."
# Query database size in KB
DB_SIZE_KB=$(docker exec "${CONTAINER_NAME}" psql -U postgres -d "${DB_NAME}" -t -A -c "SELECT pg_database_size('${DB_NAME}') / 1024;" || echo "0")
if [ -z "$DB_SIZE_KB" ] || [ "$DB_SIZE_KB" -eq 0 ]; then
  echo "ERROR: Failed to retrieve database size from ${CONTAINER_NAME}." >&2
  exit 1
fi

# Required: at least (2x estimated DB size) + 1GB (1048576 KB) safety floor
REQUIRED_KB=$(( (DB_SIZE_KB * 2) + 1048576 ))
AVAILABLE_KB=$(df -k "${BACKUP_DIR}" | awk 'NR==2 {print $4}')

echo "    Database size: $((DB_SIZE_KB / 1024)) MB"
echo "    Required space (with 1GB safety): $((REQUIRED_KB / 1024)) MB"
echo "    Available space: $((AVAILABLE_KB / 1024)) MB"

if [ "${AVAILABLE_KB}" -lt "${REQUIRED_KB}" ]; then
  echo "CRITICAL ERROR: Insufficient disk space for backup! Required: ${REQUIRED_KB} KB, Available: ${AVAILABLE_KB} KB" >&2
  exit 1
fi

echo "==> [2/5] Creating database snapshot with pg_dump..."
docker exec "${CONTAINER_NAME}" pg_dump -U postgres -d "${DB_NAME}" --clean --if-exists --no-owner --no-privileges | gzip -9 > "${DUMP_FILE}"

echo "==> [3/5] Validating archive integrity..."
if ! gzip -t "${DUMP_FILE}"; then
  echo "CRITICAL ERROR: Corrupted backup archive! Deleting bad file: ${DUMP_FILE}" >&2
  rm -f "${DUMP_FILE}"
  exit 1
fi

FILE_SIZE_MB=$(du -m "${DUMP_FILE}" | cut -f1)
echo "    Archive verified successfully (${FILE_SIZE_MB} MB): ${DUMP_FILE}"

echo "==> [4/5] Off-host Remote Replication (Disaster Recovery)..."
REMOTE_SYNC_FAILED=0
if [ -n "${REMOTE_BACKUP_DEST:-}" ]; then
  echo "    Syncing to remote destination: ${REMOTE_BACKUP_DEST}..."
  if command -v rclone &>/dev/null; then
    rclone copy "${DUMP_FILE}" "${REMOTE_BACKUP_DEST}" || REMOTE_SYNC_FAILED=1
  elif command -v aws &>/dev/null; then
    aws s3 cp "${DUMP_FILE}" "${REMOTE_BACKUP_DEST}" || REMOTE_SYNC_FAILED=1
  else
    echo "WARNING: Neither rclone nor aws-cli found. Remote sync skipped."
  fi
  
  if [ "${REMOTE_SYNC_FAILED}" -eq 1 ]; then
    echo "ALERT: Off-host backup sync FAILED! Status: DEGRADED" >&2
  fi
else
  echo "    No REMOTE_BACKUP_DEST configured in environment. Stored locally."
fi

echo "==> [5/5] Pruning local backups older than ${RETENTION_DAYS} days..."
# Retention prune runs ONLY after current backup has been verified
find "${BACKUP_DIR}" -name "${DB_NAME}_*.sql.gz" -type f -mtime +"${RETENTION_DAYS}" -delete
echo "    Prune completed."

if [ "${REMOTE_SYNC_FAILED}" -eq 1 ]; then
  echo "==> Backup completed locally with warnings (Remote sync degraded)."
  exit 2
fi

echo "==> Backup pipeline completed successfully!"
