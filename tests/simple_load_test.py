#!/usr/bin/env python3
"""
Simple Load Test untuk Todo App
Script sederhana untuk testing dasar
"""

import requests
import time
import threading
from datetime import datetime

class SimpleLoadTest:
    def __init__(self, base_url="http://localhost", num_users=5, duration=30):
        self.base_url = base_url
        self.num_users = num_users
        self.duration = duration
        self.results = []
        self.lock = threading.Lock()
    
    def test_user(self, user_id):
        """Simulasi satu user"""
        print(f"User {user_id} mulai testing...")
        start_time = time.time()
        requests_made = 0
        errors = 0
        
        while time.time() - start_time < self.duration:
            try:
                # Test GET todos
                response = requests.get(f"{self.base_url}/todos", timeout=10)
                if response.status_code == 200:
                    requests_made += 1
                else:
                    errors += 1
                
                # Test POST todo
                todo_data = {
                    "title": f"Test Todo dari User {user_id}",
                    "completed": False,
                    "description": f"Dibuat pada {datetime.now()}"
                }
                response = requests.post(f"{self.base_url}/todos", json=todo_data, timeout=10)
                if response.status_code == 201:
                    requests_made += 1
                else:
                    errors += 1
                
                # Test health check
                response = requests.get(f"{self.base_url}/health", timeout=10)
                if response.status_code == 200:
                    requests_made += 1
                else:
                    errors += 1
                
                time.sleep(1)  # Delay 1 detik
                
            except Exception as e:
                errors += 1
                print(f"Error pada User {user_id}: {e}")
        
        with self.lock:
            self.results.append({
                'user_id': user_id,
                'requests_made': requests_made,
                'errors': errors,
                'duration': time.time() - start_time
            })
        
        print(f"User {user_id} selesai: {requests_made} requests, {errors} errors")
    
    def run_test(self):
        """Jalankan load test"""
        print(f"Memulai load test dengan {self.num_users} users selama {self.duration} detik")
        print(f"Target: {self.base_url}")
        print("-" * 50)
        
        # Buat thread untuk setiap user
        threads = []
        for i in range(1, self.num_users + 1):
            thread = threading.Thread(target=self.test_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Tunggu semua thread selesai
        for thread in threads:
            thread.join()
        
        # Tampilkan hasil
        self.show_results()
    
    def show_results(self):
        """Tampilkan hasil test"""
        if not self.results:
            print("Tidak ada hasil untuk ditampilkan!")
            return
        
        total_requests = sum(r['requests_made'] for r in self.results)
        total_errors = sum(r['errors'] for r in self.results)
        avg_duration = sum(r['duration'] for r in self.results) / len(self.results)
        
        print("\n" + "="*50)
        print("HASIL LOAD TEST")
        print("="*50)
        print(f"Jumlah Users: {self.num_users}")
        print(f"Durasi Test: {self.duration} detik")
        print(f"Total Requests: {total_requests}")
        print(f"Total Errors: {total_errors}")
        print(f"Success Rate: {((total_requests-total_errors)/total_requests*100):.1f}%")
        print(f"Requests per Second: {total_requests/avg_duration:.2f}")
        print()
        
        print("Detail per User:")
        for result in self.results:
            rps = result['requests_made'] / result['duration']
            print(f"  User {result['user_id']}: {result['requests_made']} requests, "
                  f"{result['errors']} errors, {rps:.2f} req/sec")
        
        print("="*50)

def main():
    print("Simple Load Test untuk Todo App")
    print("Pastikan aplikasi sudah berjalan di http://localhost")
    print()
    
    # Konfigurasi test
    num_users = int(input("Jumlah users (default 5): ") or "5")
    duration = int(input("Durasi test dalam detik (default 30): ") or "30")
    
    # Jalankan test
    tester = SimpleLoadTest(num_users=num_users, duration=duration)
    
    try:
        tester.run_test()
    except KeyboardInterrupt:
        print("\nTest dihentikan oleh user")

if __name__ == "__main__":
    main()