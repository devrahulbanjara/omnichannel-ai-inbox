from tests.test_webhooks import KEY, webhook_body


def test_dashboard_hears_about_a_new_customer_message(client):
    with client.websocket_connect("/live") as live:
        client.post("/webhooks/rahulcoolgram", json=webhook_body(), headers=KEY)

        event = live.receive_json()

    newest_id = client.get("/conversations").json()[0]["id"]
    assert event == {"type": "message.created", "conversation_id": newest_id}


def test_dashboard_hears_about_a_reply_and_its_delivery(client):
    conversation_id = client.get("/conversations").json()[0]["id"]

    with client.websocket_connect("/live") as live:
        client.post(f"/conversations/{conversation_id}/messages", json={"text": "Hi"})

        created = live.receive_json()
        updated = live.receive_json()

    assert created == {"type": "message.created", "conversation_id": conversation_id}
    assert updated == {"type": "message.updated", "conversation_id": conversation_id}
