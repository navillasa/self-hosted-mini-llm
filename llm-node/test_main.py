from dotenv import load_dotenv
load_dotenv()
import httpx
import os

def test_generate():
    user = os.environ.get("BASIC_AUTH_USER")
    passwd = os.environ.get("BASIC_AUTH_PASS")
    assert user and passwd, "Auth credentials not set"
    r = httpx.post(
        "http://localhost:8080/generate",
        json={"prompt": "Hi!"},
        auth=(user, passwd),
        timeout=60,
    )
    assert r.status_code == 200
