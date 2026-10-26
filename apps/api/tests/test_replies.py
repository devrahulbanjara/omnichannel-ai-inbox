def conversation_id_of(client, name: str) -> str:
    return next(c["id"] for c in client.get("/conversations").json() if c["contact_name"] == name)


def test_staff_reply_is_delivered_to_rahulcoolgram(client, rahulcoolgram):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    response = client.post(f"/conversations/{conversation_id}/messages", json={"text": "Yes!"})

    assert response.status_code == 201
    assert response.json()["delivery_status"] == "sent"
    assert rahulcoolgram.sent == [("sujan", "Yes!")]


def test_reply_is_marked_failed_when_rahulcoolgram_is_down(client, rahulcoolgram):
    rahulcoolgram.down = True
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    response = client.post(f"/conversations/{conversation_id}/messages", json={"text": "Yes!"})

    assert response.status_code == 201
    message = response.json()
    assert message["delivery_status"] == "failed"
    assert message["error"] == "Could not reach RahulCoolGram"


def test_same_idempotency_key_creates_one_message(client, rahulcoolgram):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")
    url = f"/conversations/{conversation_id}/messages"
    headers = {"Idempotency-Key": "reply-1"}

    first = client.post(url, json={"text": "Rs 5,900"}, headers=headers)
    second = client.post(url, json={"text": "Rs 5,900"}, headers=headers)

    assert first.json()["id"] == second.json()["id"]
    texts = [m["text"] for m in client.get(url).json()]
    assert texts.count("Rs 5,900") == 1
    assert len(rahulcoolgram.sent) == 1


def test_different_idempotency_keys_create_two_messages(client):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")
    url = f"/conversations/{conversation_id}/messages"

    client.post(url, json={"text": "Ok"}, headers={"Idempotency-Key": "reply-1"})
    client.post(url, json={"text": "Ok"}, headers={"Idempotency-Key": "reply-2"})

    texts = [m["text"] for m in client.get(url).json()]
    assert texts.count("Ok") == 2
