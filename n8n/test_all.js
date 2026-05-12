const BASE_URL = "http://localhost:5678/webhook/ai-sales/intake";

const tests = {
  lead: {
    name: "Alex Tester",
    email: "alex@example.com",
    phone: "555-999-8888",
    message: "Hi, I'm really interested in your SEO services and would like to know the pricing.",
    service: "SEO",
    source: "website test"
  },
  book: {
    name: "Sarah Booker",
    email: "sarah@example.com",
    phone: "555-111-2222",
    message: "I'd like to book an appointment for a consultation about web design please.",
    service: "Web Design",
    source: "website test",
    preferred_date: "2026-06-01",
    preferred_time: "14:00"
  },
  reactivate: {
    name: "Old Client",
    email: "oldclient@example.com",
    phone: "555-333-4444",
    message: "Hey, it's been a while. I used your SEO service last year and I'm thinking of coming back. What's new?",
    service: "SEO",
    source: "website test"
  },
  bad_input: {
    name: "Bad Lead",
    message: "",
    source: "website test"
  }
};

async function runTest(testName) {
  const payload = tests[testName];
  if (!payload) return;

  console.log(`\n==================================================`);
  console.log(`  TEST: ${testName.toUpperCase()}`);
  console.log(`==================================================`);
  console.log(`Payload:`, JSON.stringify(payload, null, 2));

  try {
    const response = await fetch(BASE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch { data = text; }

    if (response.ok) {
      console.log(`✅ HTTP ${response.status} — SUCCESS`);
      console.log('Response:', typeof data === 'object' ? JSON.stringify(data, null, 2) : data);
    } else {
      console.log(`⚠️  HTTP ${response.status}`);
      console.log('Response:', typeof data === 'object' ? JSON.stringify(data, null, 2) : data);
    }
  } catch (error) {
    console.error(`❌ ERROR:`, error.message);
  }
}

async function main() {
  const arg = process.argv[2] || 'all';
  if (arg === 'all') {
    for (const name of Object.keys(tests)) {
      await runTest(name);
      console.log('\nWaiting 3s before next test...\n');
      await new Promise(r => setTimeout(r, 3000));
    }
  } else {
    await runTest(arg);
  }
}

main();
