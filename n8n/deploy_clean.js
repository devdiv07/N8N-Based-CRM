const fs = require('fs');
const path = require('path');

const API_KEY = process.env.N8N_API_KEY;
const N8N_BASE_URL = (process.env.N8N_BASE_URL || 'http://localhost:5678').replace(/\/$/, '');
const BASE = `${N8N_BASE_URL}/api/v1`;
const APPLY = process.argv.includes('--apply');
const WORKFLOW_DIR = path.join(__dirname, 'workflows');

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

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

if (typeof fetch !== 'function') {
  fail('This script requires Node.js 18+ (global fetch is unavailable).');
}

if (APPLY && !API_KEY) {
  fail('N8N_API_KEY must be set when running with --apply.');
}

async function api(method, endpoint, body) {
  const opts = {
    method,
    headers: {
      'X-N8N-API-KEY': API_KEY,
      'Content-Type': 'application/json',
    },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${endpoint}`, opts);
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    throw new Error(`${method} ${endpoint} failed with HTTP ${res.status}: ${JSON.stringify(data)}`);
  }

  return data;
}

function workflowPath(filename) {
  return path.join(WORKFLOW_DIR, filename);
}

function fixTriggerWiring(wf, targetNodeName) {
  if (wf.connections['Execute Workflow Trigger']) {
    wf.connections['Execute Workflow Trigger'] = {
      main: [[{ node: targetNodeName, type: 'main', index: 0 }]],
    };
  }
}

function removeExecuteTrigger(wf) {
  wf.nodes = wf.nodes.filter(
    (node) => node.type !== 'n8n-nodes-base.executeWorkflowTrigger'
  );
  delete wf.connections['Execute Workflow Trigger'];
}

function fixGSheetsNode(node, matchCol, lookupExpr) {
  if (node.parameters.options) {
    node.parameters.options.matchingColumn = matchCol;
  }
  if (node.parameters.filtersUI?.values?.[0]) {
    node.parameters.filtersUI.values[0].lookupColumn = matchCol;
    node.parameters.filtersUI.values[0].lookupValue = lookupExpr;
  }
}

function applyFixes(key, wf) {
  switch (key) {
    case 'WF1':
      fixTriggerWiring(wf, 'Extract Lead Data');
      break;

    case 'WF2':
      removeExecuteTrigger(wf);
      for (const node of wf.nodes) {
        if (node.name === 'Log Lead to CRM') {
          fixGSheetsNode(node, 'PHONE', '={{ $json.phone }}');
        }
        if (node.name === 'Update Status to CONTACTED') {
          fixGSheetsNode(node, 'PHONE', "={{ $('Extract Caller Data').item.json.phone }}");
          node.parameters.columns.value.PHONE = "={{ $('Extract Caller Data').item.json.phone }}";
        }
      }
      break;

    case 'WF3':
      removeExecuteTrigger(wf);
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
      fixTriggerWiring(wf, 'Extract Booking Data');
      break;

    case 'WF5':
      removeExecuteTrigger(wf);
      break;

    case 'WF6':
      removeExecuteTrigger(wf);
      wf.connections['Filter Who Needs Reminder'] = {
        main: [[{ node: 'Send 24h Reminder Email', type: 'main', index: 0 }]],
      };
      wf.connections['Send 24h Reminder Email'] = {
        main: [[{ node: 'Mark Reminder Sent', type: 'main', index: 0 }]],
      };
      break;

    case 'WF7':
      removeExecuteTrigger(wf);
      break;

    case 'WF8':
      fixTriggerWiring(wf, 'Get Reactivation List');
      break;
  }

  return wf;
}

function loadWorkflows() {
  const workflows = {};

  for (const [key, filename] of Object.entries(WF_FILES)) {
    const filePath = workflowPath(filename);
    if (!fs.existsSync(filePath)) {
      fail(`Workflow file not found: ${filePath}`);
    }

    let wf;
    try {
      wf = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (error) {
      fail(`Could not parse ${filePath}: ${error.message}`);
    }

    if (!wf.name || !Array.isArray(wf.nodes) || typeof wf.connections !== 'object') {
      fail(`Workflow ${filename} is missing name/nodes/connections.`);
    }

    workflows[key] = applyFixes(key, wf);
  }

  return workflows;
}

function saveWorkflows(workflows) {
  for (const [key, wf] of Object.entries(workflows)) {
    fs.writeFileSync(
      workflowPath(WF_FILES[key]),
      `${JSON.stringify(wf, null, 2)}\n`,
      'utf8'
    );
  }
}

function payloadFor(wf) {
  return {
    name: wf.name,
    nodes: wf.nodes,
    connections: wf.connections,
    settings: wf.settings || {},
  };
}

async function removeExistingProjectWorkflows(projectNames) {
  const listData = await api('GET', '/workflows');
  const existing = Array.isArray(listData?.data) ? listData.data : [];
  const matches = existing.filter((wf) => projectNames.has(wf.name));

  console.log(`Found ${matches.length} existing workflow(s) belonging to this project.`);

  for (const wf of matches) {
    if (wf.active) {
      await api('PATCH', `/workflows/${wf.id}`, { active: false });
    }
    await api('DELETE', `/workflows/${wf.id}`);
    console.log(`  removed: ${wf.name} (${wf.id})`);
  }
}

async function uploadWorkflow(key, wf) {
  const data = await api('POST', '/workflows', payloadFor(wf));
  if (!data?.id) {
    throw new Error(`${key} upload returned no workflow id.`);
  }
  console.log(`  uploaded: ${key} — ${wf.name} (${data.id})`);
  return data.id;
}

async function main() {
  console.log('');
  console.log('AI Sales CRM — scoped clean deploy');
  console.log('==================================');
  console.log(`n8n: ${N8N_BASE_URL}`);
  console.log(`mode: ${APPLY ? 'APPLY' : 'DRY RUN'}`);
  console.log('');

  const workflows = loadWorkflows();
  const projectNames = new Set(Object.values(workflows).map((wf) => wf.name));

  console.log('Local workflows:');
  for (const [key, wf] of Object.entries(workflows)) {
    console.log(`  ${key}: ${wf.name}`);
  }
  console.log('');

  if (!APPLY) {
    console.log('Dry run complete. No local files or remote workflows were changed.');
    console.log('Run with --apply to save local fixes and replace only workflows with matching project names.');
    return;
  }

  saveWorkflows(workflows);
  console.log('Saved validated workflow fixes under n8n/workflows/.');
  console.log('');

  console.log('Removing only existing workflows whose names match this project...');
  await removeExistingProjectWorkflows(projectNames);
  console.log('');

  const newIds = {};
  console.log('Uploading sub-workflows...');
  for (const key of ['WF1', 'WF2', 'WF3', 'WF4', 'WF5', 'WF6', 'WF7', 'WF8']) {
    newIds[key] = await uploadWorkflow(key, workflows[key]);
  }

  const requiredSubflows = ['WF1', 'WF4', 'WF8'];
  for (const key of requiredSubflows) {
    if (!newIds[key]) {
      throw new Error(`Cannot upload orchestrator: missing ${key} workflow id.`);
    }
  }

  const wf0 = workflows.WF0;
  const idPatchMap = {
    '→ Run WF1 Lead Capture': newIds.WF1,
    '→ Run WF4 Booking': newIds.WF4,
    '→ Run WF8 Reactivation': newIds.WF8,
  };

  for (const node of wf0.nodes) {
    if (idPatchMap[node.name]) {
      node.parameters.workflowId = idPatchMap[node.name];
    }
  }

  fs.writeFileSync(
    workflowPath(WF_FILES.WF0),
    `${JSON.stringify(wf0, null, 2)}\n`,
    'utf8'
  );

  console.log('');
  console.log('Uploading orchestrator with fresh sub-workflow IDs...');
  newIds.WF0 = await uploadWorkflow('WF0', wf0);

  console.log('');
  console.log('Activating uploaded workflows...');
  for (const [key, id] of Object.entries(newIds)) {
    await api('PATCH', `/workflows/${id}`, { active: true });
    console.log(`  active: ${key} (${id})`);
  }

  console.log('');
  console.log('Deployment complete.');
  console.log('Only workflows with names matching this project were replaced.');
  console.log('Next: run "node n8n/test_all.js all" from the repository root.');
}

main().catch((error) => {
  console.error(`FATAL: ${error.message}`);
  process.exit(1);
});
