from bs4 import BeautifulSoup
from langchain.tools import tool
import requests
from tavily import TavilyClient
import os
import time
from dotenv import load_dotenv
from rich import print

load_dotenv()


# ============================================================
# TAVILY CLIENT
# ============================================================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing from .env")

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)


# ============================================================
# WEB SEARCH TOOL
# ============================================================

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information.
    Returns titles, URLs and snippets.
    """

    max_retries = 3

    for attempt in range(max_retries):

        try:
            results = tavily.search(
                query=query,
                max_results=5,
                timeout=30
            )

            out = []

            for r in results.get("results", []):
                out.append(
                    f"Title: {r.get('title', 'N/A')}\n"
                    f"URL: {r.get('url', 'N/A')}\n"
                    f"Snippet: {r.get('content', '')[:300]}\n"
                )

            if not out:
                return "No search results were found."

            return "\n----\n".join(out)

        except requests.exceptions.ConnectionError as e:

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue

            return (
                "Tavily connection failed after multiple attempts. "
                "Please check your internet connection, VPN/firewall, "
                "or Tavily service availability."
            )

        except requests.exceptions.Timeout:

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue

            return "Tavily request timed out after multiple attempts."

        except Exception as e:

            return f"Tavily search failed: {str(e)}"


# ============================================================
# WEB SCRAPER TOOL
# ============================================================

@tool
def scrape_url(url: str) -> str:
    """
    Scrape and return clean text content from a given URL.
    """

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "Chrome/139.0 Safari/537.36"
                )
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for tag in soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return text[:5000]

    except requests.exceptions.Timeout:
        return "Could not scrape URL: request timed out."

    except requests.exceptions.ConnectionError:
        return "Could not scrape URL: connection failed."

    except requests.exceptions.HTTPError as e:
        return f"Could not scrape URL: HTTP error {e}"

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"