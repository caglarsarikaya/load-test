from locust import HttpUser, task, between
import random
import requests

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    urls = []

    def on_start(self):
        runner = self.environment.runner

        # Only load URL list on workers
        if runner and hasattr(runner, "worker") and runner.worker:
            if not WebsiteUser.urls:
                self.load_urls()

    def load_urls(self):
        try:
            response = requests.get("http://18.223.108.69:8090/urllist.json", timeout=5)
            if response.status_code == 200:
                WebsiteUser.urls = response.json()
                print(f"[Worker] Loaded {len(WebsiteUser.urls)} URLs.")
            else:
                print(f"[Worker] Failed to load URL list. Status code: {response.status_code}")
        except Exception as e:
            print(f"[Worker] Exception while loading URLs: {e}")

    @task
    def hit_random_url(self):
        runner = self.environment.runner

        # Only workers execute load
        if runner and hasattr(runner, "worker") and runner.worker:
            if WebsiteUser.urls:
                url = random.choice(WebsiteUser.urls)
                full_url = f"{self.environment.host}{url}"
                print(f"Hitting URL: {full_url}")
                self.client.get(url)
