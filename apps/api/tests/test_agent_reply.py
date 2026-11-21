"""The webhook runs the agent and sends its answer to the customer."""

from tests.test_replies import conversation_id_of
from tests.test_webhooks import KEY, webhook_body


def post_customer_message(client, text: str):
    body = webhook_body(customer_id="sujan", name="Sujan Maharjan", text=text)
    return client.post("/webhooks/rahulcoolgram", json=body, headers=KEY)


def test_customer_message_gets_an_ai_reply(client, llm, rahulcoolgram):
    llm.answer = "Yes, we have black suitcases."

    post_customer_message(client, "Black suitcase?")

    conversation_id = conversation_id_of(client, "Sujan Maharjan")
    last_message = client.get(f"/conversations/{conversation_id}/messages").json()[-1]
    assert last_message["sender_type"] == "ai"
    assert last_message["text"] == "Yes, we have black suitcases."
    assert rahulcoolgram.sent == [("sujan", "Yes, we have black suitcases.")]


def test_agent_sees_the_whole_conversation_ending_with_the_new_message(client, llm):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")
    history_length = len(client.get(f"/conversations/{conversation_id}/messages").json())

    post_customer_message(client, "Black suitcase?")

    [sent_to_model] = llm.calls
    assert sent_to_model[0]["role"] == "system"
    assert len(sent_to_model) == 1 + history_length + 1
    assert sent_to_model[-1] == {"role": "user", "content": "Black suitcase?"}


def test_model_outage_keeps_the_customer_message_and_sends_nothing(client, llm, rahulcoolgram):
    llm.down = True

    response = post_customer_message(client, "Black suitcase?")

    assert response.json() == {"status": "saved"}
    conversation_id = conversation_id_of(client, "Sujan Maharjan")
    last_message = client.get(f"/conversations/{conversation_id}/messages").json()[-1]
    assert last_message["text"] == "Black suitcase?"
    assert rahulcoolgram.sent == []


def test_empty_answer_is_not_sent(client, llm, rahulcoolgram):
    llm.answer = "  "

    post_customer_message(client, "Black suitcase?")

    assert rahulcoolgram.sent == []


def test_markdown_is_removed_before_the_reply_is_sent(client, llm, rahulcoolgram):
    llm.answer = "**Langtang Softside Trolley**  \nPrice: Rs 4,700"

    post_customer_message(client, "2")

    assert rahulcoolgram.sent == [("sujan", "Langtang Softside Trolley\nPrice: Rs 4,700")]
