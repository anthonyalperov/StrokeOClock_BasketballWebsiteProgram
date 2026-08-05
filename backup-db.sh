#!/bin/bash
# Backs up the current Postgres database to backup.dump
# Usage: ./backup-db.sh
# Requires DATABASE_URL to be set in the environment (Render sets this automatically)

set -e

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set. Set it before running this script."
  exit 1
fi

pg_dump "$DATABASE_URL" -F c -f backup.dump
echo "Backup saved to backup.dump"
