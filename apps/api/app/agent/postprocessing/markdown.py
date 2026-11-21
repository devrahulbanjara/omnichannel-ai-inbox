import re


def strip_markdown(text: str) -> str:
    """Remove markdown formatting, keeping the words, line breaks and list markers."""
    lines = []
    for line in text.splitlines():
        line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)  # "## Heading" -> "Heading"
        line = re.sub(r"^(\s*)[*+]\s+", r"\1- ", line)  # "* item" -> "- item"
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)  # **bold**
        line = re.sub(r"__(.+?)__", r"\1", line)  # __bold__
        line = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", line)  # *italic*
        line = re.sub(r"`([^`]+)`", r"\1", line)  # `code`
        line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", line)  # [text](url)
        lines.append(line.rstrip())  # trailing spaces are markdown line breaks
    plain_text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", plain_text).strip()
