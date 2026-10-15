def extract_text(content: object) -> str:
    """Extract readable text from an LLM response content."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = [
            item["text"]
            for item in content
            if isinstance(item, dict)
            and item.get("type") == "text"
            and isinstance(item.get("text"), str)
        ]
        return "\n".join(text_parts)

    return str(content)