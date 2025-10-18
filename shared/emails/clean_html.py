import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup


def clean_html(html_string: str, options: Optional[Dict[str, Any]] = None) -> str:
    """
    Clean HTML string by removing unnecessary attributes, styles, and optionally extracting text only.

    Args:
        html_string: The HTML string to clean
        options: Dictionary with options:
            - remove_comments (bool): Remove HTML comments (default: True)
            - remove_empty_elements (bool): Remove empty HTML elements (default: True)
            - preserve_structure (bool): Preserve ID attributes (default: False)
            - extract_text_only (bool): Extract only text content (default: False)

    Returns:
        Cleaned HTML string or text content
    """
    if options is None:
        options = {}

    remove_comments = options.get("remove_comments", True)
    remove_empty_elements = options.get("remove_empty_elements", True)
    preserve_structure = options.get("preserve_structure", False)
    extract_text_only = options.get("extract_text_only", False)

    # Remove new lines
    html_string = re.sub(r"\r?\n|\r", "", html_string)

    if extract_text_only:
        return extract_text_content(html_string)

    return clean_html_content(
        html_string,
        {
            "remove_comments": remove_comments,
            "remove_empty_elements": remove_empty_elements,
            "preserve_structure": preserve_structure,
        },
    )


def extract_text_content(html: str) -> str:
    """
    Extract text content from HTML, removing scripts, styles, and hidden elements.

    Args:
        html: The HTML string to extract text from

    Returns:
        Extracted and cleaned text content
    """
    soup = BeautifulSoup(html, "html.parser")
    return extract_text_from_element(soup)


def extract_text_from_element(soup: BeautifulSoup) -> str:
    """
    Extract text from a BeautifulSoup element, removing scripts, styles, and hidden elements.

    Args:
        soup: BeautifulSoup object representing the HTML

    Returns:
        Cleaned text content
    """
    # Remove script and style elements
    for element in soup.find_all(["script", "style"]):
        element.decompose()

    # Remove hidden elements
    for element in soup.find_all(
        style=re.compile(r"display:\s*none|visibility:\s*hidden", re.I)
    ):
        element.decompose()

    # Get text content
    text_content = soup.get_text()

    # Clean up whitespace and formatting
    text_content = re.sub(
        r"\s+", " ", text_content
    )  # Replace multiple whitespace with single space
    text_content = re.sub(r"\n\s*\n", "\n\n", text_content)  # Preserve paragraph breaks
    text_content = re.sub(
        r"^\s+|\s+$", "", text_content, flags=re.MULTILINE
    )  # Remove leading/trailing spaces from lines
    text_content = text_content.strip()

    return text_content


def clean_html_content(html: str, options: Dict[str, Any]) -> str:
    """
    Clean HTML content by removing various attributes and unwanted elements.

    Args:
        html: The HTML string to clean
        options: Dictionary with cleaning options

    Returns:
        Cleaned HTML string
    """
    cleaned = html

    # Remove all style attributes
    cleaned = re.sub(
        r'\s*style\s*=\s*["\'][^"\']*["\']', "", cleaned, flags=re.IGNORECASE
    )

    # Remove all class attributes
    cleaned = re.sub(
        r'\s*class\s*=\s*["\'][^"\']*["\']', "", cleaned, flags=re.IGNORECASE
    )

    # Remove all id attributes (except if preserving structure)
    if not options.get("preserve_structure"):
        cleaned = re.sub(
            r'\s*id\s*=\s*["\'][^"\']*["\']', "", cleaned, flags=re.IGNORECASE
        )

    # Remove inline CSS and style tags
    cleaned = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", cleaned, flags=re.IGNORECASE)

    # Remove script tags
    cleaned = re.sub(
        r"<script[^>]*>[\s\S]*?</script>", "", cleaned, flags=re.IGNORECASE
    )

    # Remove comments
    if options.get("remove_comments"):
        cleaned = re.sub(r"<!--[\s\S]*?-->", "", cleaned)

    # Remove tracking and analytics attributes
    cleaned = re.sub(
        r'\s*(onclick|onload|onmouseover|onmouseout|data-[^=]*)\s*=\s*["\'][^"\']*["\']',
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove table presentation attributes
    cleaned = re.sub(
        r'\s*(cellpadding|cellspacing|border|align|valign|width|height|bgcolor)\s*=\s*["\'][^"\']*["\']',
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove font and color attributes
    cleaned = re.sub(
        r'\s*(color|face|size)\s*=\s*["\'][^"\']*["\']',
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove target="_blank" and tracking attributes from links
    cleaned = re.sub(
        r'\s*(target|rel)\s*=\s*["\'][^"\']*["\']', "", cleaned, flags=re.IGNORECASE
    )

    # Remove image tracking pixels
    cleaned = re.sub(r"<img[^>]*tracking[^>]*>", "", cleaned, flags=re.IGNORECASE)

    # Remove empty attributes
    cleaned = re.sub(r'\s*=\s*["\']["\']', "", cleaned)

    # Clean up multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned)

    if options.get("remove_empty_elements"):
        # Remove empty elements (preserve self-closing tags)
        # List of self-closing tags to preserve
        self_closing = "br|hr|img|input|meta|link|area|base|col|embed|source|track|wbr"
        pattern = f"<(?!{self_closing})([a-zA-Z][a-zA-Z0-9]*)[^>]*>\\s*</\\1>"
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Format the output
    cleaned = format_html(cleaned)

    return cleaned


def format_html(html: str) -> str:
    """
    Format HTML for readability.

    Args:
        html: The HTML string to format

    Returns:
        Formatted HTML string
    """
    # Basic HTML formatting for readability
    html = re.sub(r"><", ">\n<", html)
    html = re.sub(r"^\s+|\s+$", "", html, flags=re.MULTILINE)
    lines = [line for line in html.split("\n") if line.strip()]
    return "\n".join(lines)
