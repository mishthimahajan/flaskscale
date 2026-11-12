
import concurrent.futures
import time
import urllib.request

URL = "http://127.0.0.1:5001/stress?iterations=2000000"
DURATION_SECONDS = 120
WORKERS = 12

stop_at = time.time() + DURATION_SECONDS


def send_requests():
    success = 0
    failed = 0

    while time.time() < stop_at:
        try:
            with urllib.request.urlopen(URL, timeout=30) as response:
                response.read()
                if response.status == 200:
                    success += 1
                else:
                    failed += 1
        except Exception as exc:
            failed += 1
            print(f"Request failed: {exc}")

    return success, failed


with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
    results = list(pool.map(lambda _: send_requests(), range(WORKERS)))

print("Successful requests:", sum(result[0] for result in results))
print("Failed requests:", sum(result[1] for result in results))
