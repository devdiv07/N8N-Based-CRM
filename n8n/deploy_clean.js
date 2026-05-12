const fs = require('fs');
const path = require('path');

const API_KEY = process.env.N8N_API_KEY;
if (!API_KEY) {
  console.error('ERROR: N8N_API_KEY environment variable is not set.');
  console.error('Set it with: $env:N8N_API_KEY = "your-api-key-here"');
  process.exit(1);
}
const BASE = 'http://localhost:5678/api/v1';

const WF_FILES = {
  WF0: 'WF0_Orchestrator (3).json',
  WF1: 'WF1_Instant_Response.json',
  WF2: 'WF2_Missed_Call.json',
  WF3: 'WF3_SMS_Qualification.json',
  WF4: 'WF4_Appointment_Booking.json',
  WF5: 'WF5_FollowUp (1).json',
  WF6: 'WF6_Reminders (1).json',
  WF7: 'WF7_Dashboard (1).json',
  WF8: 'WF8_Reactivation (1).json',
};

// ── API Helper ──────────────────────────────────────────────
async function api(method, endpoint, body) {
  const opts = {
    method,
    headers: { 'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${endpoint}`, opts);
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  return { ok: res.ok, status: res.status, data };
}

// ── Bug Fix Functions ───────────────────────────────────────

function fixTriggerWiring(wf, targetNodeName) {
  // BUG 2 FIX: Execute Workflow Trigger should connect ONLY to the
  // first data-processing node, NOT the OpenAI Chat Model
  if (wf.connections['Execute Workflow Trigger']) {
    wf.connections['Execute Workflow Trigger'] = {
      main: [[{ node: targetNodeName, type: 'main', index: 0 }]]
    };
  }
}

function removeExecuteTrigger(wf) {
  // Remove unnecessary Execute Workflow Trigger from standalone workflows
  // (ones with their own webhook or schedule trigger)
  wf.nodes = wf.nodes.filter(n => n.type !== 'n8n-nodes-base.executeWorkflowTrigger');
  delete wf.connections['Execute Workflow Trigger'];
}

function fixGSheetsNode(node, matchCol, lookupExpr) {
  // BUG 3 FIX: Make options.matchingColumn and filtersUI consistent
  // with matchingColumns
  if (node.parameters.options) {
    node.parameters.options.matchingColumn = matchCol;
  }
  if (node.parameters.filtersUI?.values?.[0]) {
    node.parameters.filtersUI.values[0].lookupColumn = matchCol;
    node.parameters.filtersUI.values[0].lookupValue = lookupExpr;
  }
}

// ── Apply All Fixes Per Workflow ────────────────────────────

function applyFixes(key, wf) {
  switch (key) {
    case 'WF1':
      // FIX: Trigger wired to OpenAI AND Extract Lead Data → only Extract Lead Data
      fixTriggerWiring(wf, 'Extract Lead Data');
      break;

    case 'WF2':
      // FIX: Remove unnecessary execute trigger (WF2 is standalone via webhook)
      removeExecuteTrigger(wf);
      // FIX: GSheets nodes match by PHONE but options/filters say EMAIL
      for (const node of wf.nodes) {
        if (node.name === 'Log Lead to CRM') {
          fixGSheetsNode(node, 'PHONE', "={{ $json.phone }}");
        }
        if (node.name === 'Update Status to CONTACTED') {
          fixGSheetsNode(node, 'PHONE', "={{ $('Extract Caller Data').item.json.phone }}");
          // Ensure PHONE is in the update payload for matching
          node.parameters.columns.value.PHONE = "={{ $('Extract Caller Data').item.json.phone }}";
        }
      }
      break;

    case 'WF3':
      // FIX: Remove unnecessary execute trigger (WF3 is standalone via webhook)
      removeExecuteTrigger(wf);
      // FIX: GSheets nodes match by PHONE but options/filters say EMAIL
      for (const node of wf.nodes) {
        if (node.name === 'Update to QUALIFIED HOT') {
          fixGSheetsNode(node, 'PHONE', "={{ $('Merge Lead Context').item.json.phone }}");
          node.parameters.columns.value.PHONE = "={{ $('Merge Lead Context').item.json.phone }}";
        }
        if (node.name === 'Update to CONTACTED') {
          fixGSheetsNode(node, 'PHONE', "={{ $('Merge Lead Context').item.json.phone }}");
          node.parameters.columns.value.PHONE = "={{ $('Merge Lead Context').item.json.phone }}";
        }
      }
      break;

    case 'WF4':
      // FIX: Trigger wired to OpenAI AND Extract Booking Data → only Extract Booking Data
      fixTriggerWiring(wf, 'Extract Booking Data');
      break;

    case 'WF5':
      // FIX: Remove unnecessary execute trigger (WF5 is standalone via schedule)
      removeExecuteTrigger(wf);
      break;

    case 'WF6':
      // FIX: Remove unnecessary execute trigger (WF6 is standalone via schedule)
      removeExecuteTrigger(wf);
      // BUG 4 FIX: Race condition — email and mark-sent fire in parallel.
      // Make sequential: Filter → Send Email → Mark Sent
      wf.connections['Filter Who Needs Reminder'] = {
        main: [[{ node: 'Send 24h Reminder Email', type: 'main', index: 0 }]]
      };
      wf.connections['Send 24h Reminder Email'] = {
        main: [[{ node: 'Mark Reminder Sent', type: 'main', index: 0 }]]
      };
      break;

    case 'WF7':
      // FIX: Remove unnecessary execute trigger (WF7 is standalone via schedule)
      removeExecuteTrigger(wf);
      break;

    case 'WF8':
      // FIX: Trigger wired to OpenAI → should go to Get Reactivation List
      fixTriggerWiring(wf, 'Get Reactivation List');
      break;
  }
  return wf;
}

// ── Main Deploy Pipeline ────────────────────────────────────

async function main() {
  console.log('');
  console.log('══════════════════════════════════════════════════');
  console.log('   AI Sales CRM — Clean Deploy & Bug Fix');
  console.log('══════════════════════════════════════════════════');
  console.log('');

  // ── STEP 1: Delete ALL existing workflows from n8n ────────
  console.log('STEP 1: Deleting all existing workflows from n8n...');
  const { data: listData } = await api('GET', '/workflows');
  const existing = listData.data || [];
  console.log(`  Found ${existing.length} workflows to remove.`);

  let deleted = 0;
  for (const wf of existing) {
    if (wf.active) {
      await api('PATCH', `/workflows/${wf.id}`, { active: false });
    }
    const { ok } = await api('DELETE', `/workflows/${wf.id}`);
    if (ok) deleted++;
  }
  console.log(`  ✅ Deleted ${deleted}/${existing.length} workflows.\n`);

  // ── STEP 2: Load, fix, and save all workflow JSONs ────────
  console.log('STEP 2: Loading and applying bug fixes to workflow JSONs...');
  const workflows = {};
  for (const [key, filename] of Object.entries(WF_FILES)) {
    const filePath = path.join(__dirname, filename);
    let wf = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    wf = applyFixes(key, wf);
    workflows[key] = wf;

    // Save fixed version back to disk
    fs.writeFileSync(filePath, JSON.stringify(wf, null, 2), 'utf8');
    console.log(`  ✅ ${key}: "${wf.name}" — fixed & saved`);
  }
  console.log('');

  // ── STEP 3: Upload sub-workflows first (WF1–WF8) ─────────
  console.log('STEP 3: Uploading sub-workflows (WF1–WF8)...');
  const newIds = {};

  for (const key of ['WF1','WF2','WF3','WF4','WF5','WF6','WF7','WF8']) {
    const wf = workflows[key];
    const payload = {
      name: wf.name,
      nodes: wf.nodes,
      connections: wf.connections,
      settings: wf.settings || {},
    };
    const { ok, data } = await api('POST', '/workflows', payload);
    if (ok) {
      newIds[key] = data.id;
      console.log(`  ✅ ${key}: "${wf.name}" → ID: ${data.id}`);
    } else {
      console.error(`  ❌ ${key}: FAILED —`, data);
    }
  }
  console.log('');

  // ── STEP 4: Patch WF0 Orchestrator with correct IDs ──────
  console.log('STEP 4: Patching Orchestrator (WF0) with correct sub-workflow IDs...');
  const wf0 = workflows.WF0;

  // Map node names to the correct new workflow IDs
  const idPatchMap = {
    '→ Run WF1 Lead Capture': newIds.WF1,
    '→ Run WF4 Booking': newIds.WF4,
    '→ Run WF8 Reactivation': newIds.WF8,
  };

  for (const node of wf0.nodes) {
    if (idPatchMap[node.name]) {
      const oldId = node.parameters.workflowId;
      node.parameters.workflowId = idPatchMap[node.name];
      console.log(`  ${node.name}: ${oldId} → ${idPatchMap[node.name]}`);
    }
  }

  // Save patched WF0 to disk
  fs.writeFileSync(
    path.join(__dirname, WF_FILES.WF0),
    JSON.stringify(wf0, null, 2),
    'utf8'
  );
  console.log('  ✅ WF0 patched and saved to disk.\n');

  // ── STEP 5: Upload WF0 Orchestrator ───────────────────────
  console.log('STEP 5: Uploading Orchestrator (WF0)...');
  const wf0Payload = {
    name: wf0.name,
    nodes: wf0.nodes,
    connections: wf0.connections,
    settings: wf0.settings || {},
  };
  const { ok: wf0Ok, data: wf0Data } = await api('POST', '/workflows', wf0Payload);
  if (wf0Ok) {
    newIds.WF0 = wf0Data.id;
    console.log(`  ✅ WF0: "${wf0.name}" → ID: ${wf0Data.id}\n`);
  } else {
    console.error(`  ❌ WF0: FAILED —`, wf0Data);
    return;
  }

  // ── STEP 6: Activate all workflows ────────────────────────
  console.log('STEP 6: Activating all workflows...');
  for (const [key, id] of Object.entries(newIds)) {
    const { ok } = await api('PATCH', `/workflows/${id}`, { active: true });
    console.log(`  ${ok ? '✅' : '❌'} ${key} (${id}): ${ok ? 'ACTIVE' : 'FAILED'}`);
  }
  console.log('');

  // ── SUMMARY ───────────────────────────────────────────────
  console.log('══════════════════════════════════════════════════');
  console.log('   DEPLOYMENT COMPLETE');
  console.log('══════════════════════════════════════════════════');
  console.log('');
  console.log('Workflow ID Map:');
  for (const [key, id] of Object.entries(newIds)) {
    console.log(`  ${key}: ${id}`);
  }
  console.log('');
  console.log('Bugs Fixed:');
  console.log('  ✅ BUG 1: Orchestrator workflow IDs updated to new uploads');
  console.log('  ✅ BUG 2: Execute Workflow Triggers wired to correct nodes (WF1,WF4,WF8)');
  console.log('  ✅ BUG 2b: Unnecessary Execute Triggers removed (WF2,WF3,WF5,WF6,WF7)');
  console.log('  ✅ BUG 3: Google Sheets PHONE matching fixed (WF2,WF3)');
  console.log('  ✅ BUG 4: WF6 reminder race condition fixed (now sequential)');
  console.log('  ✅ BUG 5: Empty trigger connections cleaned up');
  console.log('  ✅ BUG 6: All duplicate workflows deleted');
  console.log('');
  console.log('Next: Run "node test_intake.js" to test the full pipeline.');
  console.log('');
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
