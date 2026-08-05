#!/bin/bash
# Restores backup.dump into the current Postgres database
# Usage: ./restore-db.sh
# Requires DATABASE_URL to be set in the environment (Render sets this automatically)

set -e

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set. Set it before running this script."
  exit 1
fi

if [ ! -f "backup.dump" ]; then
  echo "ERROR: backup.dump not found in current directory."
  exit 1
fi

pg_restore -d "$DATABASE_URL" --no-owner --no-acl --clean backup.dump
echo "Restore complete"
