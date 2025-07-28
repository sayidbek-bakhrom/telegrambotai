import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}


@pytest.mark.asyncio
async def test_process_message_valid(monkeypatch):
    # Mock the OpenAI client and response
    class MockCompletion:
        class Choice:
            class Message:
                content = "Mock response"
            message = Message()
        choices = [Choice()]

    class MockClient:
        class Chat:
            class Completions:
                @staticmethod
                def create(*args, **kwargs):
                    return MockCompletion()
            completions = Completions()
        chat = Chat()

    monkeypatch.setattr("app.main.get_client", lambda: MockClient())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/process_message", json={
            "user_id": 123,
            "message": "Hello!"
        })

    assert response.status_code == 200
    assert response.json()["response"] == "Mock response"


@pytest.mark.asyncio
async def test_summarize(monkeypatch):
    # Mock the Hugging Face response
    class MockResponse:
        status_code = 200
        def json(self):
            return [{"summary_text": "Mock summary"}]

    class MockClient:
        async def post(self, *args, **kwargs):
            return MockResponse()
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr("app.main.httpx.AsyncClient", lambda: MockClient())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/summarize", json={"text": "This is a long article."})

    assert response.status_code == 200
    assert response.json()["summary"] == "Mock summary"