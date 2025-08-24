import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const evaluationDuration = new Trend('evaluation_duration');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 5 },   // Ramp up to 5 users
    { duration: '3m', target: 5 },   // Stay at 5 users
    { duration: '2m', target: 10 },  // Ramp up to 10 users
    { duration: '3m', target: 10 },  // Stay at 10 users
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    errors: ['rate<0.1'],              // Error rate must be below 10%
    evaluation_duration: ['p(95)<5000'], // 95% of evaluations must complete below 5s
  },
};

// Test data
const testTasks = [
  { episodes: 3, task_type: 'app_navigation' },
  { episodes: 2, task_type: 'text_input' },
  { episodes: 4, task_type: 'button_click' },
  { episodes: 1, task_type: 'swipe_gesture' },
];

export default function () {
  const baseUrl = __ENV.BASE_URL || 'http://your-service-url';
  
  // Random task selection
  const task = testTasks[Math.floor(Math.random() * testTasks.length)];
  
  // Test evaluation endpoint
  const startTime = Date.now();
  const response = http.post(`${baseUrl}/evaluate`, JSON.stringify(task), {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'k6-load-test/1.0',
    },
  });
  
  const duration = Date.now() - startTime;
  evaluationDuration.add(duration);
  
  // Check response
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response has results': (r) => r.json('results') !== undefined,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  errorRate.add(!success);
  
  // Test health endpoint
  const healthResponse = http.get(`${baseUrl}/health`);
  check(healthResponse, {
    'health check passed': (r) => r.status === 200,
  });
  
  // Test metrics endpoint
  const metricsResponse = http.get(`${baseUrl}/metrics`);
  check(metricsResponse, {
    'metrics endpoint accessible': (r) => r.status === 200,
  });
  
  // Random sleep between requests
  sleep(Math.random() * 2 + 1);
}

// Setup function (runs once before the test)
export function setup() {
  const baseUrl = __ENV.BASE_URL || 'http://your-service-url';
  
  // Verify system is ready
  const healthCheck = http.get(`${baseUrl}/health`);
  if (healthCheck.status !== 200) {
    throw new Error('System not ready for load testing');
  }
  
  console.log('✅ System ready for load testing');
  return { baseUrl };
}

// Teardown function (runs once after the test)
export function teardown(data) {
  console.log('🏁 Load testing completed');
  console.log(`📊 Base URL tested: ${data.baseUrl}`);
}
