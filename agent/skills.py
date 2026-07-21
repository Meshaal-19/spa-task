import os
import requests


def web_search(query: str) -> str:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return "Error: SERPAPI_KEY not set in environment."
    params = {"q": query, "api_key": api_key, "num": 3}
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"Search failed: {e}"
    results = data.get("organic_results", [])
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results[:3], 1):
        title = r.get("title", "No title")
        snippet = r.get("snippet", "No snippet")
        lines.append(f"{i}. {title}\n   {snippet}")
    return "\n\n".join(lines)
