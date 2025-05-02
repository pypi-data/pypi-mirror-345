#!/usr/bin/env python3

import argparse
import sys
from typing import Optional
from md2htmlify import MarkdownConverter  # Import the updated class-based converter

def main():
    """
    CLI script to convert Markdown text (provided as an argument or via stdin) to HTML.
    Libraries are stored in ~/.lib by default, but can be overridden with --lib-dir.
    """
    parser = argparse.ArgumentParser(description="Convert Markdown text to HTML.")
    parser.add_argument(
        "--markdown-text",
        type=str,
        default=None,
        help="The Markdown text to convert. If not provided, the converter will read Markdown from stdin."
    )
    parser.add_argument(
        "--lib-dir",
        type=str,
        default="",
        help="Path to the library directory. Defaults to ~/.lib if not specified."
    )
    parser.add_argument(
        "--use-cdn",
        action="store_true",
        default=False,
        help="Use CDN for dependencies (MathJax, Tailwind) instead of local libs."
    )
    args = parser.parse_args()

    markdown_text: Optional[str] = args.markdown_text
    if not markdown_text:
        # If no text is provided, read from stdin
        markdown_text = sys.stdin.read()

    # Create converter instance
    converter = MarkdownConverter(lib_dir=args.lib_dir)
    
    # Convert the Markdown text to HTML
    html_output = converter.convert_markdown_to_html(markdown_text, use_cdn=args.use_cdn)
    
    # Print the resulting HTML to stdout
    print(html_output)


if __name__ == "__main__":
    main()