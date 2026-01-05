#!/usr/bin/env python3
"""
Direct API Load Test - Test individual API replicas
"""
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import random

def test_api_direct(thread_id, results, port=3000):
    """Test API directly on port"""
    try:
        start = time.time()
        response = requests.get(f"http://localhost:{port}/health", timeout=3)
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

def run_direct_test(concurrent_requests=20, port=3000):
    """Run direct API test"""
    print(f"🚀 Direct API Test - {concurrent_requests} requests")
    print(f"   Target: http://localhost:{port}/health")
    print("-" * 40)
    
    results = []
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = []
        for i in range(concurrent_requests):
            future = executor.submit(test_api_direct, i, results, port)
            futures.append(future)
        
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
    print("-" * 40)
    
    return results

if __name__ == "__main__":
    print("🐳 Direct API Load Test")
    print("=" * 40)
    
    try:
        requests_num = int(input("Number of concurrent requests (default 20): ") or "20")
        run_direct_test(requests_num)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
