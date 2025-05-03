import time
import requests

class SourceMixClient:
    def __init__(self, api_base: str, token: str):
        self.api_base = api_base.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"}

    def _upload(self, endpoint, context, zip_path):
        with open(zip_path, "rb") as f:
            files = {"zip_file": f}
            r = requests.post(f"{self.api_base}/{endpoint}/{context}", headers=self.headers, files=files)
        r.raise_for_status()
        return r.json()["task_id"]

    def _poll(self, task_id):
        while True:
            poll = requests.get(f"{self.api_base}/task/{task_id}", headers=self.headers)
            poll.raise_for_status()
            data = poll.json()
            if data["status"] == "completed":
                return data.get("signed_url")
            if data["status"] == "failed":
                raise RuntimeError(f"Task failed: {data.get('error')}")
            time.sleep(5)

    def add_to_context(self, context, zip_path):
        task_id = self._upload("add_to_context", context, zip_path)
        return self._poll(task_id)

    def write_docs(self, context, zip_path):
        task_id = self._upload("write_docs", context, zip_path)
        return self._poll(task_id)

    def document_and_add_to_kb(self, context, zip_path):
        task_id = self._upload("pythondoc", context, zip_path)
        return self._poll(task_id)
