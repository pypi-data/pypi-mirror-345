import re
import io
import os
import sys
import traceback
from datetime import datetime

import anyio
import click
import urllib.parse
import mcp.types as types
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from mcp.server.lowlevel import Server
from fastmcp import FastMCP

os.environ["PYTHONIOENCODING"] = "utf-8"
# Force UTF-8 usage for stdout/stderr
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# Improved function to sanitize texts with explicit replacement of problematic characters
def sanitize_text(text):
    """
    Sanitize the input text by replacing known problematic characters with their
    ASCII equivalents and removing any other non-ASCII characters.
    Args:
        text (str): The input text to be sanitized. If None, an empty string is returned.
    Returns:
        str: The sanitized text with problematic characters replaced and non-ASCII
             characters removed.
    Replacements:
        - Right arrow (→) becomes "->"
        - Left arrow (←) becomes "<-"
        - Up arrow (↑) becomes "^"
        - Down arrow (↓) becomes "v"
        - Bullet (•) becomes "*"
        - En dash (–) becomes "-"
        - Em dash (—) becomes "--"
        - Left single quotation mark (‘) becomes "'"
        - Right single quotation mark (’) becomes "'"
        - Left double quotation mark (") becomes '"'
        - Right double quotation mark (") becomes '"'
        - Ellipsis (…) becomes "..."
        - Non-breaking space () becomes a normal space
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    try:
        # Test if the text can be encoded in the default system encoding
        text.encode(sys.getdefaultencoding())
    except UnicodeEncodeError:
        # If it can't, replace problematic characters
        # List of explicit replacements for known problematic characters
        replacements = {
            "\u2192": "->",  # Right arrow → becomes ->
            "\u2190": "<-",  # Left arrow ← becomes <-
            "\u2191": "^",   # Up arrow ↑ becomes ^
            "\u2193": "v",   # Down arrow ↓ becomes v
            "\u2022": "*",   # Bullet • becomes *
            "\u2013": "-",   # En dash – becomes -
            "\u2014": "--",  # Em dash — becomes --
            "\u2018": "'",   # Left single quotation mark ' becomes '
            "\u2019": "'",   # Right single quotation mark ' becomes '
            "\u201c": '"',   # Left double quotation mark " becomes "
            "\u201d": '"',   # Right double quotation mark " becomes "
            "\u2026": "...", # Ellipsis … becomes ...
            "\u00a0": " ",   # Non-breaking space   becomes normal space
        }

        # Apply explicit replacements
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        # Eliminate all other non-ASCII characters that might cause problems
        text = re.sub(r"[^\x00-\x7F]+", " ", text)

    return text

def generate_filename_from_url(url):
    """Generates a valid filename from a URL"""
    # Extract hostname and path
    parsed_url = urllib.parse.urlparse(url)
    hostname = parsed_url.netloc.replace(".", "_")

    # Add a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the filename
    return f"crawl_{hostname}_{timestamp}.md"


def get_results_directory():
    """Returns the path to the directory for storing results"""
    # Use a folder in the project instead of temp
    results_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "crawl_results"
    )

    # Create the folder if it doesn't exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    return results_dir

def remove_links_from_markdown(markdown_text):
    """
    Remove links and images from markdown text while preserving text and code indentation.
    
    Args:
        markdown_text (str): The markdown text to be processed
        
    Returns:
        str: Markdown text with links and images removed
    """
    # Identify and protect code blocks
    code_blocks = []
    
    # Function to replace code blocks with placeholders
    def save_code_block(match):
        code = match.group(0)
        code_blocks.append(code)
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # Identify code blocks (between ``` and ```) and replace them with placeholders
    markdown_with_placeholders = re.sub(r'```[\s\S]*?```', save_code_block, markdown_text)
    
    # Replace links in [text](url) format with just the text
    text_without_links = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', markdown_with_placeholders)
    
    # Completely remove images in ![text](url) format
    text_without_images = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text_without_links)
    
    # Remove lines containing only spaces
    text_without_empty_lines = re.sub(r'\n\s*\n', '\n\n', text_without_images)
    
    # Remove blocks of consecutive spaces (but not in code blocks)
    text_without_extra_spaces = re.sub(r' {2,}', ' ', text_without_empty_lines)
    
    # Put the code blocks back in place
    result = text_without_extra_spaces
    for i, code_block in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return result

# Instantiate the FastMCP server early
mcp = FastMCP(name="mcp-web-crawler", description="MCP server for crawling websites.")

@mcp.tool()
async def crawl(
    url: str,
    max_depth: int = 2,
    include_external: bool = False,
    verbose: bool = False,
    output_file: str = None,
) -> str:
    """
    Crawls a website and saves its content as structured markdown to a file.

    Args:
        url: URL to crawl.
        max_depth: Maximum crawling depth (default: 2).
        include_external: Whether to include external links (default: False).
        verbose: Enable verbose output (default: True).
        output_file: Path to output file (generated if not provided).

    Returns:
        A summary string indicating success or error.
    """
    # Generate a filename if not specified
    if not output_file:
        # Use the project folder instead of the temporary folder
        output_file = os.path.join(get_results_directory(), generate_filename_from_url(url))

    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=max_depth,
            include_external=include_external,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=verbose,
    )

    try:
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(url, config=config)
            print(f"Crawled {len(results)} pages in total")
            
            # Create the parent folder if necessary
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # Call results_to_markdown and get the result
            result_dict = await results_to_markdown(results, output_file)

            if result_dict["error"]:
                return f"Error: {result_dict['error']}"

            file_path = result_dict["file_path"]
            stats = result_dict["stats"]

            # Create a summary message
            summary = f"""
## Crawl completed successfully
- URL: {url}
- Result file: {file_path}
- Duration: {stats["duration_seconds"]:.2f} seconds
- Pages processed: {stats["successful_pages"]} successful, {stats.get("failed_pages", 0)} failed, {stats.get("not_found_pages", 0)} not found (404), {stats.get("forbidden_pages", 0)} access forbidden (403)

You can view the results in the file: {file_path}
(Results are now stored in the 'crawl_results' folder of your project)
            """
            return summary
    except Exception as e:
        print(f"Error during crawling: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return f"Error: {sanitize_text(str(e))}"

async def results_to_markdown(results: list, output_path: str) -> dict:
    """
    Convert crawl results to a markdown file
    
    Args:
        results: List of crawl results
        output_path: Output file path
        
    Returns:
        A dictionary containing statistics and operation status
    """
    stats = {
        "successful_pages": 0,
        "failed_pages": 0,
        "not_found_pages": 0,
        "forbidden_pages": 0,
        "start_time": datetime.now()
    }
    
    try:
        with open(output_path, "w", encoding="utf-8") as md_file:
            for result in results:
                # Safe retrieval of content as in crawl copy.py
                text_for_output = getattr(result, "markdown", None) or getattr(
                    result, "text", None
                )

                if not text_for_output:
                    print(f"No content found for {result.url} - Skipped")
                    stats["failed_pages"] += 1
                    continue
                    
                # Check if it's an error page (404 or 403)
                if ("404 Not Found" in text_for_output or "403 Forbidden" in text_for_output) and "nginx" in text_for_output:
                    error_type = "404" if "404 Not Found" in text_for_output else "403"
                    print(f"{error_type} page detected and skipped: {result.url}")
                    if error_type == "404":
                        stats["not_found_pages"] += 1
                    else:
                        stats["forbidden_pages"] += 1
                    continue

                # Remove links from Markdown text
                text_for_output = remove_links_from_markdown(text_for_output)

                # Structuring metadata
                metadata = {
                    "depth": result.metadata.get("depth", "N/A"),
                    "timestamp": datetime.now().isoformat(),
                    "title": result.metadata.get("title", "Untitled page"),
                }
                
                # Check if title contains error indicators
                error_indicators = ["404", "403", "Not Found", "Forbidden"]
                if any(indicator in metadata["title"] for indicator in error_indicators):
                    print(f"Page with error title detected and skipped: {result.url}")
                    if "404" in metadata["title"] or "Not Found" in metadata["title"]:
                        stats["not_found_pages"] += 1
                    else:
                        stats["forbidden_pages"] += 1
                    continue

                # Formatted writing with literal template
                md_content = f"""
# {metadata["title"]}

## URL
{result.url}

## Metadata
- Depth: {metadata["depth"]}
- Timestamp: {metadata["timestamp"]}

## Content
{text_for_output}

---
"""
                md_file.write(md_content)
                stats["successful_pages"] += 1
            
            # Display a summary at the end
            print(f"Valid pages processed: {stats['successful_pages']}")
            print(f"Error pages (403/404) skipped: {stats['not_found_pages'] + stats['forbidden_pages']}")
        
        # Finalize statistics
        stats["end_time"] = datetime.now()
        stats["duration_seconds"] = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        return {
            "file_path": output_path,
            "stats": stats,
            "error": None
        }
    
    except Exception as e:
        print(f"Error writing markdown file: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return {
            "error": f"Writing error: {str(e)}",
            "file_path": None,
            "stats": stats
        }

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    try:
        mcp.run()
    except Exception as e:
        print(f"Error running stdio server: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    try:
        # Click decorator handles argument parsing and calls main
        main()
    except Exception as e:
        print(f"Main error: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)