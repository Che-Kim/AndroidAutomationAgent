#!/usr/bin/env python3
"""
AndroidWorld Locust Load Testing Script
Professional load testing using Locust framework for concurrent user simulation.
"""

from locust import HttpUser, task, between, events
import json
import random

class AndroidWorldUser(HttpUser):
    """Simulates a user interacting with AndroidWorld evaluation endpoints"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        print(f"👤 User {self.user_id} started")
    
    @task(3)
    def evaluate_app_navigation(self):
        """Test app navigation evaluation (higher weight)"""
        payload = {
            "episodes": random.randint(1, 5),
            "task_type": "app_navigation"
        }
        
        with self.client.post(
            "/evaluate",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "results" in data:
                        response.success()
                    else:
                        response.failure("Missing results in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def evaluate_text_input(self):
        """Test text input evaluation"""
        payload = {
            "episodes": random.randint(1, 3),
            "task_type": "text_input"
        }
        
        with self.client.post(
            "/evaluate",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def evaluate_button_click(self):
        """Test button click evaluation"""
        payload = {
            "episodes": random.randint(1, 4),
            "task_type": "button_click"
        }
        
        with self.client.post(
            "/evaluate",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def evaluate_swipe_gesture(self):
        """Test swipe gesture evaluation (lower weight)"""
        payload = {
            "episodes": random.randint(1, 2),
            "task_type": "swipe_gesture"
        }
        
        with self.client.post(
            "/evaluate",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def check_health(self):
        """Check system health"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: HTTP {response.status_code}")
    
    @task(1)
    def get_metrics(self):
        """Get system metrics"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics failed: HTTP {response.status_code}")

# Custom event handlers for better reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("🚀 AndroidWorld Load Test Starting...")
    print(f"🎯 Target: {environment.host}")
    print(f"👥 Users: {environment.runner.user_count}")
    print(f"⏱️  Duration: {environment.runner.duration}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("🏁 AndroidWorld Load Test Completed!")
    
    # Print summary statistics
    stats = environment.stats
    print("\n📊 TEST SUMMARY:")
    print(f"   Total Requests: {stats.total.num_requests}")
    print(f"   Failed Requests: {stats.total.num_failures}")
    print(f"   Success Rate: {((stats.total.num_requests - stats.total.num_failures) / stats.total.num_requests * 100):.1f}%")
    
    # Find the evaluation endpoint stats
    eval_stats = None
    for key in stats.entries:
        if "/evaluate" in key:
            eval_stats = stats.entries[key]
            break
    
    if eval_stats:
        print(f"\n🎯 EVALUATION ENDPOINT PERFORMANCE:")
        print(f"   Requests: {eval_stats.num_requests}")
        print(f"   Failures: {eval_stats.num_failures}")
        print(f"   Avg Response Time: {eval_stats.avg_response_time:.0f}ms")
        print(f"   Min Response Time: {eval_stats.min_response_time:.0f}ms")
        print(f"   Max Response Time: {eval_stats.max_response_time:.0f}ms")
        print(f"   Median Response Time: {eval_stats.median_response_time:.0f}ms")
        print(f"   95th Percentile: {eval_stats.get_response_time_percentile(0.95):.0f}ms")

# Configuration for running with locust command
if __name__ == "__main__":
    print("🧪 AndroidWorld Locust Load Test")
    print("Run with: locust -f locust-load-test.py --host=http://your-service-url")
    print("Or: locust -f locust-load-test.py --host=http://your-service-url --users 10 --spawn-rate 2 --run-time 5m")
