#!/bin/sh
set -eu

echo "=== Dane Agentic AI Portfolio: n8n verification ==="

echo "Importing synthetic support orchestration workflow..."
n8n import:workflow --input=/opt/portfolio/workflow.json

echo "Resolving imported workflow ID..."
n8n export:workflow --all --output=/tmp/workflows.json
WORKFLOW_ID="$(node - <<'NODE'
const fs = require('fs');
const raw = fs.readFileSync('/tmp/workflows.json', 'utf8');
const parsed = JSON.parse(raw);
const items = Array.isArray(parsed) ? parsed : [parsed];
const match = items.find(w => w.name === 'Dane Support Orchestration Verification');
if (!match || !match.id) {
  console.error('Could not resolve imported workflow ID');
  process.exit(2);
}
process.stdout.write(String(match.id));
NODE
)"

echo "Executing workflow ID: ${WORKFLOW_ID}"
n8n execute --id "${WORKFLOW_ID}" | tee /tmp/n8n-verification.log

echo "N8N_VERIFICATION_COMPLETE"
echo "Starting n8n editor/server..."
exec n8n start
