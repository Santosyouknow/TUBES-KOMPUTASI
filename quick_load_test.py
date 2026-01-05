#!/usr/bin/env python3
"""
Quick Load Test for Docker Swarm Scaling
Simple script to test load balancing across API replicas
"""
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import random

def quick_health_test(thread_id, results, base_url="http://localhost"):
    """Single health check request"""
    try:
        start = time.time()
        response = requests.get(f"{base_url}/health", timeout=3)
        end = time.time()
        
        results.append({
            "thread": thread_id,
            "status": response.status_code,
            "response_time": end - start,
            "server": response.headers.get('Server', 'Unknown')
        })
    except Exception as e:
        results.append({
            "thread": thread_id, 
            "status": 0,
            "error": str(e)
        })

def run_quick_test(concurrent_requests=20, base_url="http://localhost"):
    """Run quick load test"""
    print(f"🚀 Quick Load Test - {concurrent_requests} concurrent requests")
    print(f"   Target: {base_url}/health")
    print("-" * 40)
    
    results = []
    
    # Execute concurrent requests
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = []
        for i in range(concurrent_requests):
            future = executor.submit(quick_health_test, i, results, base_url)
            futures.append(future)
        
        # Wait for completion
        for future in futures:
            future.result()
    
    # Analyze results
    successful = sum(1 for r in results if r.get("status") == 200)
    failed = len(results) - successful
    
    response_times = [r["response_time"] for r in results if r.get("response_time")]
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
    else:
        avg_time = min_time = max_time = 0
    
    print(f"📊 Results:")
    print(f"   Total Requests: {len(results)}")
    print(f"   Successful: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"   Failed: {failed} ({failed/len(results)*100:.1f}%)")
    print(f"   Response Time - Avg: {avg_time:.3f}s")
    print(f"   Response Time - Min: {min_time:.3f}s") 
    print(f"   Response Time - Max: {max_time:.3f}s")
    
    # Show server distribution (if different servers respond)
    servers = {}
    for r in results:
        server = r.get("server", "Unknown")
        servers[server] = servers.get(server, 0) + 1
    
    if len(servers) > 1:
        print(f"   Server Distribution:")
        for server, count in servers.items():
            print(f"     {server}: {count} requests")
    
    print("-" * 40)
    return results

def test_scaling_levels():
    """Test different scaling levels"""
    base_url = "http://localhost"
    
    # Test with different concurrent levels
    levels = [5, 10, 20, 30, 50]
    
    print("🔥 SCALING TEST - Different Load Levels")
    print("=" * 50)
    
    for level in levels:
        print(f"\n📈 Testing {level} concurrent requests:")
        run_quick_test(level, base_url)
        time.sleep(1)  # Brief pause between tests

if __name__ == "__main__":
    print("🐳 Docker Swarm Quick Load Test")
    print("=" * 50)
    print("1. Quick Test (20 requests)")
    print("2. Custom Test")
    print("3. Scaling Test (5, 10, 20, 30, 50 requests)")
    print("=" * 50)
    
    try:
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            run_quick_test()
            
        elif choice == "2":
            requests_num = int(input("Number of concurrent requests: "))
            url = input("Base URL (default http://localhost): ") or "http://localhost"
            run_quick_test(requests_num, url)
            
        elif choice == "3":
            test_scaling_levels()
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
