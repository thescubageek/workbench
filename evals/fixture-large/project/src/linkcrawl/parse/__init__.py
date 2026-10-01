"""Link extraction from HTML, Markdown and CSS documents."""

from linkcrawl.parse.base import ExtractedLink
from linkcrawl.parse.dispatch import extract_links

__all__ = ["ExtractedLink", "extract_links"]
