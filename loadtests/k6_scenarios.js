import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const API_KEY = __ENV.API_KEY || '';
const SMOKE_RPS = Number(__ENV.SMOKE_RPS || 50);
const STEADY_RPS = Number(__ENV.STEADY_RPS || 200);
const STRESS_RPS = Number(__ENV.STRESS_RPS || 1000);

const tickets = [
  'VPN keeps dropping every hour, please help',
  'Please refund the duplicate charge on the last invoice',
  'My login keeps saying the password is invalid even after reset',
  'Can you add dark mode to the analytics dashboard?',
  'This slack channel is getting spam links about crypto',
  'Order #19871 has not shipped, need assistance',
];

const classifyTrend = new Trend('classify_latency_ms');
const classifyErrors = new Counter('classify_errors_total');

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-arrival-rate',
      rate: SMOKE_RPS,
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: SMOKE_RPS,
      gracefulStop: '15s',
      exec: 'classifySmoke',
    },
    steady: {
      executor: 'constant-arrival-rate',
      startTime: '3m',
      rate: STEADY_RPS,
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: STEADY_RPS,
      gracefulStop: '30s',
      exec: 'classifySteady',
    },
    stress: {
      executor: 'ramping-arrival-rate',
      startTime: '9m',
      stages: [
        { duration: '2m', target: STRESS_RPS / 10 },
        { duration: '4m', target: STRESS_RPS / 2 },
        { duration: '4m', target: STRESS_RPS },
        { duration: '2m', target: 0 },
      ],
      timeUnit: '1s',
      preAllocatedVUs: STRESS_RPS,
      gracefulStop: '45s',
      exec: 'classifyStress',
    },
  },
  thresholds: {
    classify_latency_ms: ['p(95)<750', 'p(99)<1500'],
    http_req_failed: ['rate<0.02'],
    classify_errors_total: ['count==0'],
  },
};

export function setup() {
  if (!API_KEY) {
    throw new Error('API_KEY env variable must be set for load testing');
  }
}

function pickTicket() {
  return tickets[Math.floor(Math.random() * tickets.length)];
}

function classifyRequest() {
  const payload = JSON.stringify({ ticket: pickTicket() });
  const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
    'X-Forwarded-Proto': 'https',
  };
  const response = http.post(`${BASE_URL}/api/v1/classify`, payload, { headers });

  classifyTrend.add(response.timings.duration);

  const ok = check(response, {
    'status is 200': (res) => res.status === 200,
    'has category': (res) => !!(res.json('category')),
  });

  if (!ok) {
    classifyErrors.add(1);
  }

  sleep(0.2);
}

export function classifySmoke() {
  classifyRequest();
}

export function classifySteady() {
  classifyRequest();
}

export function classifyStress() {
  classifyRequest();
}

