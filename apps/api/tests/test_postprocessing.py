"""Steps applied to the agent's answer before it reaches the customer."""

from app.agent.postprocessing.markdown import strip_markdown


def test_strip_markdown_keeps_words_lines_and_numbered_lists():
    markdown = "\n".join(
        [
            "## Black suitcases",
            "",
            "1) **Everest Hardshell** – 24 inch, Rs 5,900",
            "2) *Langtang* Softside – `HLC-04`, Rs 4,700  ",
            "* Free cover",
            "",
            "",
            "",
            "See [our store](https://example.com).",
        ]
    )

    plain_text = strip_markdown(markdown)

    assert plain_text == "\n".join(
        [
            "Black suitcases",
            "",
            "1) Everest Hardshell – 24 inch, Rs 5,900",
            "2) Langtang Softside – HLC-04, Rs 4,700",
            "- Free cover",
            "",
            "See our store (https://example.com).",
        ]
    )


def test_strip_markdown_leaves_a_lone_star_alone():
    assert strip_markdown("Rated 4.5 * by customers") == ("Rated 4.5 * by customers")
