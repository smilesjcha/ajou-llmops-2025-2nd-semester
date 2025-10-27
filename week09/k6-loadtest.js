
// k6 run k6-loadtest.js --vus 20 --duration 60s
import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  let payload = JSON.stringify({ userId: "k6", message: "hello from k6" });
  let headers = { 'Content-Type': 'application/json' };
  let res = http.post('http://localhost:8000/chat', payload, { headers });
  check(res, { 'status was 200': (r) => r.status === 200 });
  sleep(1);
}
