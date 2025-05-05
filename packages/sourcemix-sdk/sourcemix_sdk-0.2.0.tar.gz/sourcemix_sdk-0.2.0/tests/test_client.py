import pytest
import requests
from sourcemix_sdk.client import SourceMixClient

@pytest.fixture
def client():
    return SourceMixClient(api_base="https://api.example.com", token="fake-token")

def test_document_and_add_to_kb(requests_mock, client):
    # Mock file upload response
    task_id = "test123"
    requests_mock.post("https://api.example.com/pythondoc/test-agent", json={"task_id": task_id})

    # Mock polling
    requests_mock.get(f"https://api.example.com/task/{task_id}", json={"status": "completed", "signed_url": "https://download.example.com/file.zip"})

    response = client.document_and_add_to_kb("test-agent", "dummy.zip")
    assert response["status"] == "completed"
    assert "signed_url" in response

def test_add_to_context(requests_mock, client):
    task_id = "ctx456"
    requests_mock.post("https://api.example.com/add_to_context/test-agent", json={"task_id": task_id})
    requests_mock.get(f"https://api.example.com/task/{task_id}", json={"status": "completed"})

    result = client.add_to_context("test-agent", "dummy.zip")
    assert result["status"] == "completed"

def test_write_docs(requests_mock, client):
    task_id = "doc789"
    requests_mock.post("https://api.example.com/write_docs/test-agent", json={"task_id": task_id})
    requests_mock.get(f"https://api.example.com/task/{task_id}", json={"status": "completed"})

    output = client.write_docs("test-agent", "dummy.zip")
    assert output["status"] == "completed"
