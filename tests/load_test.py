#!/usr/bin/env python3
"""
Load Testing Script untuk Todo App
Menggunakan requests dan threading untuk simulasi multiple users
"""

import requests
import threading
import time
import json
import random
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

class TodoLoadTester:
    def __init__(self, base_url="http://localhost", num_users=10, duration=60):
        self.base_url = base_url
        self.num_users = num_users
        self.duration = duration
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
        # Sample todo data
        self.sample_todos = [
            "Belajar Docker",
            "Membuat API REST",
            "Testing aplikasi",
            "Deploy ke production",
            "Monitoring sistem",
            "Backup database",
            "Update dokumentasi",
            "Code review",
            "Refactor code",
            "Optimasi performance"
        ]
    
    def make_request(self, method, endpoint, data=None):
        """Make HTTP request and record response time"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            result = {
                'method': method,
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': datetime.now(),
                'success': response.status_code < 400
            }
            
            self.results.append(result)
            return response
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            error = {
                'method': method,
                'endpoint': endpoint,
                'error': str(e),
                'response_time': response_time,
                'timestamp': datetime.now()
            }
            
            self.errors.append(error)
            return None
    
    def user_simulation(self, user_id):
        """Simulate a single user's behavior"""
        print(f"User {user_id} started")
        
        while time.time() - self.start_time < self.duration:
            # Random user behavior
            action = random.choice([
                'get_todos',
                'create_todo', 
                'get_stats',
                'health_check'
            ])
            
            if action == 'get_todos':
                self.make_request("GET", "/todos")
                
            elif action == 'create_todo':
                todo_data = {
                    "title": random.choice(self.sample_todos) + f" - User {user_id}",
                    "completed": random.choice([True, False]),
                    "description": f"Task created by user {user_id} at {datetime.now()}"
                }
                response = self.make_request("POST", "/todos", todo_data)
                
                # Sometimes update the created todo
                if response and response.status_code == 201 and random.random() < 0.3:
                    try:
                        todo_id = response.json()['data']['id']
                        update_data = {"completed": not todo_data["completed"]}
                        self.make_request("PATCH", f"/todos/{todo_id}", update_data)
                    except:
                        pass
                        
            elif action == 'get_stats':
                self.make_request("GET", "/stats")
                
            elif action == 'health_check':
                self.make_request("GET", "/health")
            
            # Random delay between requests (0.1 to 2 seconds)
            time.sleep(random.uniform(0.1, 2.0))
        
        print(f"User {user_id} finished")
    
    def run_load_test(self):
        """Run the load test with multiple users"""
        print(f"Starting load test with {self.num_users} users for {self.duration} seconds")
        print(f"Target URL: {self.base_url}")
        print("-" * 60)
        
        self.start_time = time.time()
        
        # Create thread pool for users
        with ThreadPoolExecutor(max_workers=self.num_users) as executor:
            futures = [
                executor.submit(self.user_simulation, user_id) 
                for user_id in range(1, self.num_users + 1)
            ]
            
            # Wait for all users to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"User thread error: {e}")
        
        self.end_time = time.time()
        
    def generate_report(self):
        """Generate and display test results"""
        if not self.results:
            print("No results to report!")
            return
        
        # Calculate statistics
        response_times = [r['response_time'] for r in self.results]
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        total_requests = len(self.results)
        success_rate = (len(successful_requests) / total_requests) * 100
        
        # Response time statistics
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        # Requests per second
        actual_duration = self.end_time - self.start_time
        rps = total_requests / actual_duration
        
        # Status code distribution
        status_codes = {}
        for result in self.results:
            code = result['status_code']
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Generate report
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        print(f"Test Duration: {actual_duration:.2f} seconds")
        print(f"Number of Users: {self.num_users}")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {len(successful_requests)}")
        print(f"Failed Requests: {len(failed_requests)}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Requests per Second: {rps:.2f}")
        print()
        
        print("RESPONSE TIME STATISTICS:")
        print(f"  Average: {avg_response_time:.2f} ms")
        print(f"  Minimum: {min_response_time:.2f} ms")
        print(f"  Maximum: {max_response_time:.2f} ms")
        print(f"  95th Percentile: {p95_response_time:.2f} ms")
        print()
        
        print("STATUS CODE DISTRIBUTION:")
        for code, count in sorted(status_codes.items()):
            percentage = (count / total_requests) * 100
            print(f"  {code}: {count} ({percentage:.1f}%)")
        print()
        
        if self.errors:
            print("ERRORS:")
            error_types = {}
            for error in self.errors:
                error_type = error['error']
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count}")
            print()
        
        # Endpoint performance
        endpoint_stats = {}
        for result in self.results:
            endpoint = f"{result['method']} {result['endpoint']}"
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = []
            endpoint_stats[endpoint].append(result['response_time'])
        
        print("ENDPOINT PERFORMANCE:")
        for endpoint, times in endpoint_stats.items():
            avg_time = statistics.mean(times)
            count = len(times)
            print(f"  {endpoint}: {avg_time:.2f} ms avg ({count} requests)")
        
        print("="*60)
    
    def save_results_to_file(self, filename=None):
        """Save detailed results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.json"
        
        report_data = {
            'test_config': {
                'base_url': self.base_url,
                'num_users': self.num_users,
                'duration': self.duration,
                'start_time': self.start_time,
                'end_time': self.end_time
            },
            'results': self.results,
            'errors': self.errors
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"Detailed results saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Load test for Todo App')
    parser.add_argument('--url', default='http://localhost', 
                       help='Base URL of the application (default: http://localhost)')
    parser.add_argument('--users', type=int, default=10,
                       help='Number of concurrent users (default: 10)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Test duration in seconds (default: 60)')
    parser.add_argument('--save', action='store_true',
                       help='Save detailed results to JSON file')
    
    args = parser.parse_args()
    
    # Create and run load tester
    tester = TodoLoadTester(
        base_url=args.url,
        num_users=args.users,
        duration=args.duration
    )
    
    try:
        tester.run_load_test()
        tester.generate_report()
        
        if args.save:
            tester.save_results_to_file()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        if tester.results:
            tester.generate_report()

if __name__ == "__main__":
    main()