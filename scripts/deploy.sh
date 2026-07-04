#!/bin/bash
# scripts/deploy.sh — the ONLY way to deploy booklab-site
# Deploys from a clean temp directory. _src/ never touches Cloudflare.
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR=$(mktemp -d)

echo "📦 Building clean deploy directory..."

# Copy everything EXCEPT source/dev files
rsync -a \
  --exclude='_src' \
  --exclude='_archive' \
  --exclude='.backups' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='*.py' \
  --exclude='*.md' \
  --exclude='*.txt' \
  --exclude='scripts' \
  --exclude='.cfignore' \
  --exclude='node_modules' \
  "$SITE_DIR/" "$DEPLOY_DIR/"

# Sanity check — fail hard if _src leaked through
if [ -d "$DEPLOY_DIR/_src" ]; then
  echo "❌ FATAL: _src/ found in deploy dir. Aborting."
  rm -rf "$DEPLOY_DIR"
  exit 1
fi

echo "✅ Clean deploy dir ready (no _src/)"
echo "   Files: $(find "$DEPLOY_DIR" -type f | wc -l)"
echo ""

# Deploy
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN env var}" \
CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID env var}" \
npx wrangler pages deploy "$DEPLOY_DIR" --project-name=booklab-site --branch=main

# Cleanup
rm -rf "$DEPLOY_DIR"
echo ""
echo "✅ Deployed successfully (clean, no _src/)"
