const BASE_URL = process.env.CRM_INTAKE_URL || 'http://localhost:5678/webhook/ai-sales/intake';

function isoDateDaysFromNow(days) {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

const tests = {
  lead: {
    expectedStatus: 200,
    payload: {
      name: 'Alex Tester',
      email: 'alex@example.com',
      phone: '555-999-8888',
      message: "Hi, I'm really interested in your SEO services and would like to know the pricing.",
      service: 'SEO',
      source: 'website test',
    },
  },
  book: {
    expectedStatus: 200,
    payload: {
      name: 'Sarah Booker',
      email: 'sarah@example.com',
      phone: '555-111-2222',
      message: "I'd like to book an appointment for a consultation about web design please.",
      service: 'Web Design',
      source: 'website test',
      preferred_date: isoDateDaysFromNow(7),
      preferred_time: '14:00',
    },
  },
  reactivate: {
    expectedStatus: 200,
    payload: {
      name: 'Old Client',
      email: 'oldclient@example.com',
      phone: '555-333-4444',
      message: "Hey, it's been a while. I used your SEO service last year and I'm thinking of coming back. What's new?",
      service: 'SEO',
      source: 'website test',
    },
  },
  bad_input: {
    expectedStatus: 400,
    payload: {
      name: 'Bad Lead',
      message: '',
      source: 'website test',
    },
  },
};

async function runTest(testName) {
  const test = tests[testName];
  if (!test) {
    console.error(`Unknown test: ${testName}`);
    return false;
  }

  console.log('\n==================================================');
  console.log(`  TEST: ${testName.toUpperCase()}`);
  console.log('==================================================');
  console.log(`Expected HTTP: ${test.expectedStatus}`);
  console.log('Payload:', JSON.stringify(test.payload, null, 2));

  try {
    const response = await fetch(BASE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(test.payload),
    });

    const text = await response.text();
    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text;
    }

    const passed = response.status === test.expectedStatus;
    console.log(`${passed ? '✅ PASS' : '❌ FAIL'} — HTTP ${response.status}`);
    console.log(
      'Response:',
      typeof data === 'object' && data !== null ? JSON.stringify(data, null, 2) : data
    );

    return passed;
  } catch (error) {
    console.error(`❌ ERROR: ${error.message}`);
    return false;
  }
}

async function main() {
  if (typeof fetch !== 'function') {
    console.error('ERROR: This smoke harness requires Node.js 18+ (global fetch is unavailable).');
    process.exit(1);
  }

  const arg = process.argv[2] || 'all';
  const names = arg === 'all' ? Object.keys(tests) : [arg];
  let passed = 0;

  for (const name of names) {
    if (await runTest(name)) passed += 1;
  }

  console.log('\n==================================================');
  console.log(`RESULT: ${passed}/${names.length} smoke cases passed`);
  console.log('==================================================');

  if (passed !== names.length) {
    process.exitCode = 1;
  }
}

main();
