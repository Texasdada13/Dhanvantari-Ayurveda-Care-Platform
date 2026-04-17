/**
 * k6 smoke test for Dhanvantari API.
 *
 * Install: https://k6.io/docs/getting-started/installation/
 * Run:     k6 run perf/k6-smoke.js
 * Against prod: API_URL=https://dhanvantari-api.onrender.com k6 run perf/k6-smoke.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },   // ramp up
    { duration: '20s', target: 10 },   // sustained
    { duration: '10s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95th percentile under 2s
    http_req_failed: ['rate<0.05'],     // <5% error rate
  },
};

const BASE = __ENV.API_URL || 'http://localhost:8747';
const headers = { 'Content-Type': 'application/json' };

export default function () {
  // Health check
  const health = http.get(`${BASE}/api/health`);
  check(health, {
    'health 200': (r) => r.status === 200,
    'health < 500ms': (r) => r.timings.duration < 500,
  });

  // Login
  const login = http.post(
    `${BASE}/api/auth/login`,
    JSON.stringify({ email: 'demo@dhanvantari.app', password: 'demo1234' }),
    { headers }
  );
  check(login, {
    'login 200': (r) => r.status === 200,
    'login < 2s': (r) => r.timings.duration < 2000,
  });

  if (login.status === 200) {
    const token = JSON.parse(login.body).access_token;
    const authHeaders = { ...headers, Authorization: `Bearer ${token}` };

    // Patient list
    const patients = http.get(`${BASE}/api/patients`, { headers: authHeaders });
    check(patients, {
      'patients 200': (r) => r.status === 200,
      'patients < 2s': (r) => r.timings.duration < 2000,
    });

    // Subscription status
    const sub = http.get(`${BASE}/api/billing/subscription`, { headers: authHeaders });
    check(sub, {
      'subscription 200': (r) => r.status === 200,
    });
  }

  sleep(1);
}
