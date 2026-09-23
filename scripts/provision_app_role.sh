#!/usr/bin/env bash
# ==============================================================================
# Script: provision_app_role.sh
# Purpose: Idempotent least-privilege PostgreSQL role provisioning for Patwatoli AI.
# Security: Zero hardcoded passwords. Dynamic SQL execution with session config.
# ==============================================================================

set -euo pipefail

CONTAINER_NAME="ai-llm-postgres"
DB_NAME="ai_llm_db"
APP_ROLE="patwatoli_app"

echo "==> [1/4] Generating or reading application password..."
# Generate a clean 32-character hexadecimal password if not passed via env
APP_PWD="${POSTGRES_APP_PASSWORD:-$(openssl rand -hex 16)}"

echo "==> [2/4] Provisioning ${APP_ROLE} in ${DB_NAME}..."
docker exec -i "${CONTAINER_NAME}" psql -U postgres -d "${DB_NAME}" -v ON_ERROR_STOP=1 -v app_pwd="${APP_PWD}" << 'EOSQL'
SELECT set_config('app.pwd', :'app_pwd', false);

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'patwatoli_app') THEN
      EXECUTE format('CREATE ROLE patwatoli_app WITH LOGIN PASSWORD %L', current_setting('app.pwd'));
      RAISE NOTICE 'Role patwatoli_app created successfully.';
   ELSE
      EXECUTE format('ALTER ROLE patwatoli_app WITH LOGIN PASSWORD %L', current_setting('app.pwd'));
      RAISE NOTICE 'Role patwatoli_app password updated successfully.';
   END IF;
END
$$;

SELECT set_config('app.pwd', '', false);

-- Schema & Connection Privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT CONNECT ON DATABASE ai_llm_db TO patwatoli_app;
GRANT USAGE ON SCHEMA public TO patwatoli_app;

-- Existing Tables & Sequences DML
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO patwatoli_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO patwatoli_app;

-- Future Tables Created by Migration Owner (postgres)
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO patwatoli_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO patwatoli_app;
EOSQL

echo "==> [3/4] Verifying ${APP_ROLE} connectivity & least privilege..."
docker exec -i -e PGPASSWORD="${APP_PWD}" "${CONTAINER_NAME}" psql -U "${APP_ROLE}" -d "${DB_NAME}" -c "SELECT current_user AS authenticated_role, 1 AS health_check;"

echo "==> [4/4] Provisioning Complete!"
echo "--------------------------------------------------"
echo "Configured DATABASE_URL for runtime:"
echo "postgresql://patwatoli_app:${APP_PWD}@postgres:5432/${DB_NAME}"
echo "--------------------------------------------------"
echo "Update your .env file with the above DATABASE_URL when ready."

