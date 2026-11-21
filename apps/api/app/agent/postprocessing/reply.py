from app.agent.postprocessing.markdown import strip_markdown


def postprocess_reply(answer: str) -> str:
    """The agent's answer as it is saved and sent to the customer. Each step takes the text
    from the step before; checks on the answer, such as guardrails, are added here as steps."""
    # Chat apps show markdown symbols as they are. The prompt asks for plain text, but the
    # model does not always follow it.
    text = strip_markdown(answer)
    return text
