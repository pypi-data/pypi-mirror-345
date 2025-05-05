from ignite.client import Client

def test_status():
    client = Client()
    resp = client.get("/status")
    assert resp["status"] == "ok"
