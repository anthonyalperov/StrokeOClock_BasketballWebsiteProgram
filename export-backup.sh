#!/bin/bash
# Uploads backup.dump to a temporary file host so you can download it
# from outside the Render Shell (which has no built-in file download).
# Usage: ./export-backup.sh
#
# The link this prints is temporary and PUBLIC to anyone who has it -
# download your copy promptly, then let it expire.

set -e

if [ ! -f "backup.dump" ]; then
  echo "ERROR: backup.dump not found. Run ./backup-db.sh first."
  exit 1
fi

echo "Uploading backup.dump..."
URL=$(curl -s --upload-file backup.dump https://transfer.sh/backup.dump)

if [ -z "$URL" ]; then
  echo "ERROR: Upload failed. Your Render service may not allow outbound access to transfer.sh."
  exit 1
fi

echo ""
echo "Download your backup from:"
echo "$URL"
echo ""
echo "This link is public - download it now, then don't share it further."
