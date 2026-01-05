#!/usr/bin/env python3
import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import json

class LoadTester:
    def __init__(self, base_url="http://localhost", port=80):
        self.base_url = f"{base_url}:{port}"
        self.results = defaultdict(list)
        self.lock = threading.Lock()
        
    def health_check(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return {
                "status": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:100]
            }
        except Exception as e:
            return {"error": str(e), "status": 0}
    
    def get_todos(self):
        """Get all todos"""
        try:
            response = requests.get(f"{self.base_url}/todos", timeout=5)
            return {
                "status": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "todos_count": len(response.json()) if response.headers.get('content-type', '').startswith('application/json') else 0
            }
        except Exception as e:
            return {"error": str(e), "status": 0}
    
    def create_todo(self):
        """Create a new todo"""
        try:
            todo_data = {
                "title": f"Test Todo {random.randint(1000, 9999)}",
                "description": f"Load test todo at {time.time()}",
                "completed": False
            }
            response = requests.post(
                f"{self.base_url}/todos", 
                json=todo_data, 
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            return {
                "status": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "created": response.status_code == 201
            }
        except Exception as e:
            return {"error": str(e), "status": 0}
    
    def worker_thread(self, test_type, thread_id, duration=60):
        """Worker thread for load testing"""
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time:
            if test_type == "health":
                result = self.health_check()
            elif test_type == "get":
                result = self.get_todos()
            elif test_type == "create":
                result = self.create_todo()
            else:
                result = {"error": "Unknown test type", "status": 0}
            
            result["thread_id"] = thread_id
            result["timestamp"] = time.time()
            
            with self.lock:
                self.results[test_type].append(result)
            
            # Random delay between requests (100-500ms)
            time.sleep(random.uniform(0.1, 0.5))
    
    def run_load_test(self, test_type="health", threads=10, duration=60):
        """Run load test with specified parameters"""
        print(f"🚀 Starting {test_type} load test...")
        print(f"   Threads: {threads}")
        print(f"   Duration: {duration} seconds")
        print(f"   Target: {self.base_url}")
        print("-" * 50)
        
        # Clear previous results
        self.results[test_type] = []
        
        # Start worker threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for i in range(threads):
                future = executor.submit(self.worker_thread, test_type, i, duration)
                futures.append(future)
            
            # Wait for all threads to complete
            for future in futures:
                future.result()
        
        # Analyze results
        self.analyze_results(test_type)
    
    def analyze_results(self, test_type):
        """Analyze test results"""
        results = self.results[test_type]
        if not results:
            print("❌ No results to analyze")
            return
        
        # Calculate statistics
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.get("status", 0) in [200, 201])
        failed_requests = total_requests - successful_requests
        
        response_times = [r.get("response_time", 0) for r in results if r.get("response_time", 0) > 0]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        # Calculate requests per second
        if results:
            time_span = max(r["timestamp"] for r in results) - min(r["timestamp"] for r in results)
            rps = total_requests / time_span if time_span > 0 else 0
        else:
            rps = 0
        
        # Print results
        print(f"📊 {test_type.upper()} TEST RESULTS:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        print(f"   Failed: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        print(f"   Requests/Second: {rps:.2f}")
        print(f"   Response Time - Avg: {avg_response_time:.3f}s")
        print(f"   Response Time - Min: {min_response_time:.3f}s")
        print(f"   Response Time - Max: {max_response_time:.3f}s")
        
        # Show error distribution
        errors = defaultdict(int)
        for result in results:
            if result.get("error"):
                errors[result["error"]] += 1
            elif result.get("status", 0) not in [200, 201]:
                errors[f"HTTP {result.get('status', 0)}"] += 1
        
        if errors:
            print(f"   Errors:")
            for error, count in errors.items():
                print(f"     {error}: {count}")
        
        print("-" * 50)
    
    def test_scaling(self, max_threads=50, step=10, duration=30):
        """Test scaling by gradually increasing load"""
        print(f"🔥 SCALING TEST - Gradually increasing load")
        print(f"   Starting with {step} threads, max {max_threads}")
        print("-" * 50)
        
        for threads in range(step, max_threads + 1, step):
            print(f"\n📈 Testing with {threads} threads:")
            self.run_load_test("health", threads=threads, duration=duration)
            time.sleep(2)  # Brief pause between tests
    
    def test_mixed_workload(self, threads=20, duration=60):
        """Test mixed workload (health, get, create)"""
        print(f"🔄 MIXED WORKLOAD TEST")
        print(f"   Threads: {threads}")
        print(f"   Duration: {duration} seconds")
        print("-" * 50)
        
        # Clear all results
        self.results = defaultdict(list)
        
        # Start different types of workers
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            
            # Distribute threads across different test types
            health_threads = threads // 3
            get_threads = threads // 3
            create_threads = threads - health_threads - get_threads
            
            # Start health check workers
            for i in range(health_threads):
                future = executor.submit(self.worker_thread, "health", f"health_{i}", duration)
                futures.append(future)
            
            # Start get todos workers
            for i in range(get_threads):
                future = executor.submit(self.worker_thread, "get", f"get_{i}", duration)
                futures.append(future)
            
            # Start create todo workers
            for i in range(create_threads):
                future = executor.submit(self.worker_thread, "create", f"create_{i}", duration)
                futures.append(future)
            
            # Wait for all threads to complete
            for future in futures:
                future.result()
        
        # Analyze all results
        for test_type in ["health", "get", "create"]:
            if self.results[test_type]:
                self.analyze_results(test_type)

def main():
    tester = LoadTester()
    
    print("🐳 DOCKER SWARM LOAD TESTING TOOL")
    print("=" * 50)
    print("1. Basic Health Check Test")
    print("2. Get Todos Test") 
    print("3. Create Todo Test")
    print("4. Scaling Test (Gradual Load Increase)")
    print("5. Mixed Workload Test")
    print("6. Custom Test")
    print("=" * 50)
    
    try:
        choice = input("Select test (1-6): ").strip()
        
        if choice == "1":
            threads = int(input("Number of threads (default 10): ") or "10")
            duration = int(input("Duration in seconds (default 30): ") or "30")
            tester.run_load_test("health", threads, duration)
            
        elif choice == "2":
            threads = int(input("Number of threads (default 10): ") or "10")
            duration = int(input("Duration in seconds (default 30): ") or "30")
            tester.run_load_test("get", threads, duration)
            
        elif choice == "3":
            threads = int(input("Number of threads (default 5): ") or "5")
            duration = int(input("Duration in seconds (default 30): ") or "30")
            tester.run_load_test("create", threads, duration)
            
        elif choice == "4":
            max_threads = int(input("Maximum threads (default 50): ") or "50")
            step = int(input("Thread increment (default 10): ") or "10")
            duration = int(input("Duration per test (default 30): ") or "30")
            tester.test_scaling(max_threads, step, duration)
            
        elif choice == "5":
            threads = int(input("Number of threads (default 20): ") or "20")
            duration = int(input("Duration in seconds (default 60): ") or "60")
            tester.test_mixed_workload(threads, duration)
            
        elif choice == "6":
            test_type = input("Test type (health/get/create): ").strip().lower()
            threads = int(input("Number of threads: "))
            duration = int(input("Duration in seconds: "))
            tester.run_load_test(test_type, threads, duration)
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
