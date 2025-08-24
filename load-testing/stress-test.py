#!/usr/bin/env python3
"""
AndroidWorld Stress Testing Script
Tests system resilience under concurrent load using threading and concurrent requests.
"""

import asyncio
import aiohttp
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any
import statistics
import argparse
import sys

@dataclass
class TestResult:
    """Individual test result data"""
    thread_id: int
    start_time: float
    end_time: float
    duration: float
    status_code: int
    success: bool
    error: str = None
    response_size: int = 0

@dataclass
class StressTestReport:
    """Aggregated stress test results"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_concurrency_reached: int
    total_duration: float
    requests_per_second: float
    cpu_usage_estimate: float
    memory_usage_estimate: float

class AndroidWorldStressTester:
    """Stress tester for AndroidWorld evaluation endpoints"""
    
    def __init__(self, base_url: str, max_workers: int = 10):
        self.base_url = base_url.rstrip('/')
        self.max_workers = max_workers
        self.results: List[TestResult] = []
        self.results_lock = threading.Lock()
        
        # Test scenarios
        self.test_scenarios = [
            {"episodes": 1, "task_type": "app_navigation"},
            {"episodes": 2, "task_type": "text_input"},
            {"episodes": 3, "task_type": "button_click"},
            {"episodes": 1, "task_type": "swipe_gesture"},
            {"episodes": 4, "task_type": "form_filling"},
        ]
    
    async def single_request(self, session: aiohttp.ClientSession, thread_id: int) -> TestResult:
        """Execute a single evaluation request"""
        start_time = time.time()
        
        try:
            # Random scenario selection
            import random
            scenario = random.choice(self.test_scenarios)
            
            async with session.post(
                f"{self.base_url}/evaluate",
                json=scenario,
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                duration = end_time - start_time
                
                response_text = await response.text()
                
                return TestResult(
                    thread_id=thread_id,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    status_code=response.status,
                    success=response.status == 200,
                    response_size=len(response_text)
                )
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            return TestResult(
                thread_id=thread_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                status_code=0,
                success=False,
                error=str(e)
            )
    
    async def run_concurrent_requests(self, num_requests: int, concurrency: int) -> List[TestResult]:
        """Run multiple concurrent requests"""
        print(f"🚀 Starting stress test: {num_requests} requests with {concurrency} concurrent workers")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                task = self.single_request(session, i)
                tasks.append(task)
            
            # Execute with concurrency limit
            semaphore = asyncio.Semaphore(concurrency)
            
            async def limited_request(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(*[limited_request(task) for task in tasks])
            return results
    
    def run_threaded_stress_test(self, num_requests: int, concurrency: int) -> List[TestResult]:
        """Run stress test using threading for better concurrency control"""
        print(f"🧵 Starting threaded stress test: {num_requests} requests with {concurrency} concurrent workers")
        
        def worker(thread_id: int):
            """Worker function for each thread"""
            import requests
            
            start_time = time.time()
            try:
                # Random scenario selection
                import random
                scenario = random.choice(self.test_scenarios)
                
                response = requests.post(
                    f"{self.base_url}/evaluate",
                    json=scenario,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                result = TestResult(
                    thread_id=thread_id,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    status_code=response.status_code,
                    success=response.status_code == 200,
                    response_size=len(response.content)
                )
                
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                
                result = TestResult(
                    thread_id=thread_id,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    status_code=0,
                    success=False,
                    error=str(e)
                )
            
            with self.results_lock:
                self.results.append(result)
        
        # Create and start threads
        threads = []
        for i in range(num_requests):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
            
            # Control concurrency
            if len(threads) >= concurrency:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for t in threads:
            t.join()
        
        return self.results
    
    def generate_report(self, results: List[TestResult], test_duration: float) -> StressTestReport:
        """Generate comprehensive stress test report"""
        if not results:
            raise ValueError("No results to analyze")
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        durations = [r.duration for r in results if r.success]
        
        # Calculate percentiles
        p95 = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else (max(durations) if durations else 0)
        p99 = statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else (max(durations) if durations else 0)
        
        # Estimate resource usage (rough calculations)
        avg_cpu_per_request = 0.15  # Estimated CPU seconds per request
        avg_memory_per_request = 50  # Estimated MB per request
        
        return StressTestReport(
            total_requests=len(results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            success_rate=len(successful) / len(results) * 100,
            avg_response_time=statistics.mean(durations) if durations else 0,
            min_response_time=min(durations) if durations else 0,
            max_response_time=max(durations) if durations else 0,
            p95_response_time=p95,
            p99_response_time=p99,
            max_concurrency_reached=min(len(results), self.max_workers),
            total_duration=test_duration,
            requests_per_second=len(results) / test_duration if test_duration > 0 else 0,
            cpu_usage_estimate=len(results) * avg_cpu_per_request,
            memory_usage_estimate=len(results) * avg_memory_per_request
        )
    
    def save_report(self, report: StressTestReport, filename: str = "stress_test_report.json"):
        """Save stress test report to file"""
        report_dict = {
            "timestamp": time.time(),
            "base_url": self.base_url,
            "max_workers": self.max_workers,
            "results": {
                "total_requests": report.total_requests,
                "successful_requests": report.successful_requests,
                "failed_requests": report.failed_requests,
                "success_rate": report.success_rate,
                "avg_response_time": report.avg_response_time,
                "min_response_time": report.min_response_time,
                "max_response_time": report.max_response_time,
                "p95_response_time": report.p95_response_time,
                "p99_response_time": report.p99_response_time,
                "max_concurrency_reached": report.max_concurrency_reached,
                "total_duration": report.total_duration,
                "requests_per_second": report.requests_per_second,
                "cpu_usage_estimate": report.cpu_usage_estimate,
                "memory_usage_estimate": report.memory_usage_estimate
            },
            "recommendations": self._generate_recommendations(report)
        }
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"📊 Report saved to {filename}")
    
    def _generate_recommendations(self, report: StressTestReport) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if report.success_rate < 95:
            recommendations.append("Success rate below 95% - investigate error handling and system stability")
        
        if report.p95_response_time > 5.0:
            recommendations.append("95th percentile response time > 5s - optimize performance or increase resources")
        
        if report.requests_per_second < 10:
            recommendations.append("Throughput below 10 req/s - consider horizontal scaling or performance optimization")
        
        if report.cpu_usage_estimate > 100:
            recommendations.append("High CPU usage estimated - consider vertical scaling or code optimization")
        
        if report.memory_usage_estimate > 1000:
            recommendations.append("High memory usage estimated - investigate memory leaks or increase memory limits")
        
        if not recommendations:
            recommendations.append("System performing well under stress - current configuration appears adequate")
        
        return recommendations
    
    def print_report(self, report: StressTestReport):
        """Print formatted stress test report"""
        print("\n" + "="*60)
        print("🧪 ANDROIDWORLD STRESS TEST REPORT")
        print("="*60)
        print(f"📊 Total Requests: {report.total_requests}")
        print(f"✅ Successful: {report.successful_requests}")
        print(f"❌ Failed: {report.failed_requests}")
        print(f"📈 Success Rate: {report.success_rate:.1f}%")
        print(f"⏱️  Total Duration: {report.total_duration:.2f}s")
        print(f"🚀 Requests/Second: {report.requests_per_second:.2f}")
        print(f"👥 Max Concurrency: {report.max_concurrency_reached}")
        print()
        print("📊 RESPONSE TIME STATISTICS:")
        print(f"   Average: {report.avg_response_time:.3f}s")
        print(f"   Min: {report.min_response_time:.3f}s")
        print(f"   Max: {report.max_response_time:.3f}s")
        print(f"   95th Percentile: {report.p95_response_time:.3f}s")
        print(f"   99th Percentile: {report.p99_response_time:.3f}s")
        print()
        print("💻 RESOURCE ESTIMATES:")
        print(f"   CPU Usage: {report.cpu_usage_estimate:.1f} CPU-seconds")
        print(f"   Memory Usage: {report.memory_usage_estimate:.0f} MB")
        print()
        print("💡 RECOMMENDATIONS:")
        for rec in self._generate_recommendations(report):
            print(f"   • {rec}")
        print("="*60)

def main():
    """Main function for command-line execution"""
    parser = argparse.ArgumentParser(description="AndroidWorld Stress Testing Tool")
    parser.add_argument("--url", default="", help="Base URL to test (required)")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests")
    parser.add_argument("--concurrency", type=int, default=10, help="Maximum concurrent requests")
    parser.add_argument("--output", default="stress_test_report.json", help="Output report filename")
    
    args = parser.parse_args()
    
    if not args.url:
        print("❌ Error: --url parameter is required")
        print("Example: python stress-test.py --url http://your-service-url --requests 100")
        sys.exit(1)
    
    print("🧪 AndroidWorld Stress Testing Tool")
    print(f"🎯 Target: {args.url}")
    print(f"📊 Configuration: {args.requests} requests, {args.concurrency} concurrent")
    
    # Create tester
    tester = AndroidWorldStressTester(args.url, args.concurrency)
    
    # Run test
    start_time = time.time()
    results = tester.run_threaded_stress_test(args.requests, args.concurrency)
    end_time = time.time()
    
    test_duration = end_time - start_time
    
    # Generate and display report
    report = tester.generate_report(results, test_duration)
    tester.print_report(report)
    
    # Save report
    tester.save_report(report, args.output)
    
    # Exit with error code if success rate is too low
    if report.success_rate < 90:
        print(f"\n⚠️  Warning: Low success rate ({report.success_rate:.1f}%) - system may be unstable")
        sys.exit(1)
    else:
        print(f"\n✅ Stress test completed successfully with {report.success_rate:.1f}% success rate")
        sys.exit(0)

if __name__ == "__main__":
    main()
