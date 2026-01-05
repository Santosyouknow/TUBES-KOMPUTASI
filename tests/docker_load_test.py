#!/usr/bin/env python3
"""
Docker Container Load Test
Script khusus untuk testing aplikasi yang berjalan di Docker container
Termasuk monitoring resource usage container
"""

import requests
import threading
import time
import json
import docker
import psutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import argparse

class DockerLoadTester:
    def __init__(self, base_url="http://localhost", num_users=10, duration=60):
        self.base_url = base_url
        self.num_users = num_users
        self.duration = duration
        self.results = []
        self.container_stats = []
        self.docker_client = None
        self.lock = threading.Lock()
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            print("✅ Docker client connected")
        except Exception as e:
            print(f"⚠️  Docker client connection failed: {e}")
            print("   Container monitoring will be disabled")
    
    def get_container_stats(self):
        """Get Docker container resource usage"""
        if not self.docker_client:
            return None
        
        try:
            containers = self.docker_client.containers.list()
            todo_containers = [c for c in containers if 'todo' in c.name.lower() or 'api' in c.name.lower()]
            
            stats = {}
            for container in todo_containers:
                try:
                    # Get container stats (non-blocking)
                    container_stats = container.stats(stream=False)
                    
                    # Calculate CPU percentage
                    cpu_delta = container_stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               container_stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = container_stats['cpu_stats']['system_cpu_usage'] - \
                                  container_stats['precpu_stats']['system_cpu_usage']
                    
                    cpu_percent = 0
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100
                    
                    # Calculate memory usage
                    memory_usage = container_stats['memory_stats']['usage']
                    memory_limit = container_stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100
                    
                    stats[container.name] = {
                        'cpu_percent': cpu_percent,
                        'memory_usage_mb': memory_usage / (1024 * 1024),
                        'memory_percent': memory_percent,
                        'memory_limit_mb': memory_limit / (1024 * 1024),
                        'timestamp': datetime.now()
                    }
                except Exception as e:
                    print(f"Error getting stats for {container.name}: {e}")
            
            return stats
            
        except Exception as e:
            print(f"Error getting container stats: {e}")
            return None
    
    def monitor_containers(self):
        """Monitor container resources during test"""
        print("Starting container monitoring...")
        
        while hasattr(self, 'test_running') and self.test_running:
            stats = self.get_container_stats()
            if stats:
                with self.lock:
                    self.container_stats.append({
                        'timestamp': datetime.now(),
                        'containers': stats
                    })
                
                # Print real-time stats
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Container Stats:")
                for container_name, container_stats in stats.items():
                    print(f"  {container_name}: "
                          f"CPU: {container_stats['cpu_percent']:.1f}% | "
                          f"Memory: {container_stats['memory_usage_mb']:.1f}MB "
                          f"({container_stats['memory_percent']:.1f}%)")
            
            time.sleep(5)  # Monitor every 5 seconds
    
    def make_request(self, method, endpoint, data=None):
        """Make HTTP request with timing"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            with self.lock:
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
            
            with self.lock:
                error = {
                    'method': method,
                    'endpoint': endpoint,
                    'error': str(e),
                    'response_time': response_time,
                    'timestamp': datetime.now(),
                    'success': False
                }
                self.results.append(error)
            
            return None
    
    def user_simulation(self, user_id):
        """Simulate user behavior"""
        while hasattr(self, 'test_running') and self.test_running:
            # Test different endpoints
            self.make_request("GET", "/todos")
            time.sleep(0.5)
            
            self.make_request("POST", "/todos", {
                "title": f"Docker Test Todo {user_id}-{int(time.time())}",
                "completed": False,
                "description": f"Created by Docker load test user {user_id}"
            })
            time.sleep(0.5)
            
            self.make_request("GET", "/health")
            time.sleep(1)
    
    def run_test(self):
        """Run the Docker load test"""
        print(f"Starting Docker Load Test")
        print(f"Users: {self.num_users} | Duration: {self.duration}s | URL: {self.base_url}")
        print("-" * 60)
        
        self.test_running = True
        
        # Start container monitoring
        if self.docker_client:
            monitor_thread = threading.Thread(target=self.monitor_containers)
            monitor_thread.daemon = True
            monitor_thread.start()
        
        # Start user simulation
        with ThreadPoolExecutor(max_workers=self.num_users) as executor:
            futures = [
                executor.submit(self.user_simulation, user_id)
                for user_id in range(1, self.num_users + 1)
            ]
            
            # Let test run for specified duration
            time.sleep(self.duration)
            
            # Stop test
            self.test_running = False
            
            # Wait for threads to finish
            for future in futures:
                try:
                    future.result(timeout=10)
                except:
                    pass
    
    def analyze_container_performance(self):
        """Analyze container performance during test"""
        if not self.container_stats:
            print("No container stats available")
            return
        
        print("\nCONTAINER PERFORMANCE ANALYSIS:")
        print("-" * 60)
        
        # Group stats by container
        container_data = {}
        for stat_entry in self.container_stats:
            for container_name, stats in stat_entry['containers'].items():
                if container_name not in container_data:
                    container_data[container_name] = {
                        'cpu_usage': [],
                        'memory_usage': [],
                        'memory_percent': []
                    }
                
                container_data[container_name]['cpu_usage'].append(stats['cpu_percent'])
                container_data[container_name]['memory_usage'].append(stats['memory_usage_mb'])
                container_data[container_name]['memory_percent'].append(stats['memory_percent'])
        
        # Calculate averages and peaks
        for container_name, data in container_data.items():
            avg_cpu = sum(data['cpu_usage']) / len(data['cpu_usage'])
            max_cpu = max(data['cpu_usage'])
            avg_memory = sum(data['memory_usage']) / len(data['memory_usage'])
            max_memory = max(data['memory_usage'])
            avg_memory_percent = sum(data['memory_percent']) / len(data['memory_percent'])
            max_memory_percent = max(data['memory_percent'])
            
            print(f"\n{container_name}:")
            print(f"  CPU Usage    - Avg: {avg_cpu:.1f}% | Peak: {max_cpu:.1f}%")
            print(f"  Memory Usage - Avg: {avg_memory:.1f}MB | Peak: {max_memory:.1f}MB")
            print(f"  Memory %     - Avg: {avg_memory_percent:.1f}% | Peak: {max_memory_percent:.1f}%")
            
            # Performance warnings
            if max_cpu > 80:
                print(f"  ⚠️  High CPU usage detected!")
            if max_memory_percent > 80:
                print(f"  ⚠️  High memory usage detected!")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        if not self.results:
            print("No results to report!")
            return
        
        # Basic statistics
        total_requests = len(self.results)
        successful_requests = [r for r in self.results if r.get('success', False)]
        failed_requests = [r for r in self.results if not r.get('success', False)]
        
        success_rate = (len(successful_requests) / total_requests) * 100
        
        # Response time analysis
        response_times = [r['response_time'] for r in self.results if 'response_time' in r]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        # Calculate RPS
        rps = total_requests / self.duration
        
        print("\n" + "="*60)
        print("DOCKER LOAD TEST RESULTS")
        print("="*60)
        print(f"Test Duration: {self.duration} seconds")
        print(f"Concurrent Users: {self.num_users}")
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
        
        # Container performance analysis
        self.analyze_container_performance()
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        if success_rate < 95:
            print("  - Success rate is low, check application logs")
            print("  - Consider scaling up containers")
        
        if avg_response_time > 1000:
            print("  - High response times detected")
            print("  - Check database performance")
            print("  - Consider adding more API replicas")
        
        if self.container_stats:
            # Check if any container had high resource usage
            high_cpu_detected = False
            high_memory_detected = False
            
            for stat_entry in self.container_stats:
                for container_name, stats in stat_entry['containers'].items():
                    if stats['cpu_percent'] > 80:
                        high_cpu_detected = True
                    if stats['memory_percent'] > 80:
                        high_memory_detected = True
            
            if high_cpu_detected:
                print("  - High CPU usage detected in containers")
                print("  - Consider horizontal scaling")
            
            if high_memory_detected:
                print("  - High memory usage detected")
                print("  - Check for memory leaks")
                print("  - Increase container memory limits")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Docker Load Test for Todo App')
    parser.add_argument('--url', default='http://localhost',
                       help='Base URL of the application')
    parser.add_argument('--users', type=int, default=10,
                       help='Number of concurrent users')
    parser.add_argument('--duration', type=int, default=60,
                       help='Test duration in seconds')
    
    args = parser.parse_args()
    
    # Check if application is running
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Application health check failed: {response.status_code}")
            return
        print("✅ Application is running and healthy")
    except Exception as e:
        print(f"❌ Cannot connect to application: {e}")
        print("   Make sure the application is running with: docker-compose up -d")
        return
    
    # Run test
    tester = DockerLoadTester(
        base_url=args.url,
        num_users=args.users,
        duration=args.duration
    )
    
    try:
        tester.run_test()
        tester.generate_report()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        tester.test_running = False
        if tester.results:
            tester.generate_report()

if __name__ == "__main__":
    main()