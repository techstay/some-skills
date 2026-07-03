# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx>=0.28.1",
#     "python-dotenv>=1.0.0",
#     "cyclopts>=4.10.1",
#     "tavily-python>=0.7.0",
#     "exa-py>=2.10.0",
#     "ollama>=0.6.0",
#     "firecrawl-py>=2.0.0",
# ]
# ///

import os
import sys
from typing import Annotated

import dotenv
import httpx
import ollama
from cyclopts import App, Parameter
from exa_py import Exa
from firecrawl import Firecrawl
from tavily import TavilyClient

dotenv.load_dotenv()


def _is_disabled(service: str) -> bool:
    """Return True if the service is disabled via DISABLE_<SERVICE>=1/true."""
    val = os.getenv(f"DISABLE_{service.upper()}", "").strip().lower()
    return val in ("1", "true")


def _jina_headers() -> dict[str, str]:
    """Build headers for Jina AI requests; Authorization is optional."""
    headers: dict[str, str] = {"Accept": "application/json"}
    key = os.getenv("JINA_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _guard(service: str, env_var: str) -> str | None:
    """Return an error string if the service is disabled or its key is missing, else None."""
    if _is_disabled(service):
        return f"[{service}] disabled by env"
    if not os.getenv(env_var):
        return f"[{service}] {env_var} not set"
    return None


def _tavily_client() -> TavilyClient | str:
    """Return a Tavily client, or an error string if unavailable."""
    if err := _guard("tavily", "TAVILY_API_KEY"):
        return err
    return TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))


def _exa_client() -> Exa | str:
    """Return an Exa client, or an error string if unavailable."""
    if err := _guard("exa", "EXA_API_KEY"):
        return err
    return Exa(api_key=os.getenv("EXA_API_KEY", ""))


def tavily_search(query: str, max_results: int = 10) -> str:
    """Search the web using Tavily."""
    client = _tavily_client()
    if isinstance(client, str):
        return client
    try:
        resp = client.search(
            query,
            max_results=max_results,
            include_answer="basic",
        )
        parts: list[str] = []
        answer = resp.get("answer")
        if answer:
            parts.append(f"Answer: {answer}")
        for item in resp.get("results", []):
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")
            parts.append(f"## {title}\nURL: {url}\n{content}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[tavily] search failed: {exc}"


def tavily_extract(url: str) -> str:
    """Extract content from a URL using Tavily."""
    client = _tavily_client()
    if isinstance(client, str):
        return client
    try:
        resp = client.extract(
            urls=[url],
            format="markdown",
        )
        parts: list[str] = []
        for item in resp.get("results", []):
            item_url = item.get("url", "")
            raw = item.get("raw_content", "")
            parts.append(f"## {item_url}\n{raw}")
        for item in resp.get("failed_results", []):
            item_url = item.get("url", "")
            error = item.get("error", "unknown error")
            parts.append(f"[failed] {item_url}: {error}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[tavily] extract failed: {exc}"


def exa_search(query: str, max_results: int = 10) -> str:
    """Search the web using Exa."""
    client = _exa_client()
    if isinstance(client, str):
        return client
    try:
        result = client.search(
            query,
            num_results=max_results,
            type="auto",
            contents={"highlights": True},
        )
        parts: list[str] = []
        for item in getattr(result, "results", []):
            title = getattr(item, "title", "")
            url = getattr(item, "url", "")
            highlights = getattr(item, "highlights", None) or []
            highlights_text = "\n".join(str(h) for h in highlights)
            parts.append(f"## {title}\nURL: {url}\n{highlights_text}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[exa] search failed: {exc}"


def exa_extract(url: str) -> str:
    """Extract content from a URL using Exa."""
    client = _exa_client()
    if isinstance(client, str):
        return client
    try:
        result = client.get_contents(url, text=True)
        results = getattr(result, "results", [])
        if not results:
            return f"[exa] extract failed: no content for {url}"
        item = results[0]
        title = getattr(item, "title", "")
        text = getattr(item, "text", "")
        return f"## {url}\n{title}\n{text}"
    except Exception as exc:  # noqa: BLE001
        return f"[exa] extract failed: {exc}"


def ollama_search(query: str, max_results: int = 10) -> str:
    """Search the web using Ollama Cloud."""
    if err := _guard("ollama", "OLLAMA_API_KEY"):
        return err
    try:
        response = ollama.web_search(query, max_results=max_results)
        parts: list[str] = []
        for item in getattr(response, "results", []):
            title = getattr(item, "title", "")
            url = getattr(item, "url", "")
            content = getattr(item, "content", "")
            parts.append(f"## {title}\nURL: {url}\n{content}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[ollama] search failed: {exc}"


def ollama_extract(url: str) -> str:
    """Extract content from a URL using Ollama Cloud."""
    if err := _guard("ollama", "OLLAMA_API_KEY"):
        return err
    try:
        response = ollama.web_fetch(url=url)
        title = getattr(response, "title", "")
        content = getattr(response, "content", "")
        return f"## {url}\n{title}\n{content}"
    except Exception as exc:  # noqa: BLE001
        return f"[ollama] extract failed: {exc}"


def jina_search(query: str, max_results: int = 10) -> str:
    """Search the web using Jina AI."""
    if _is_disabled("jina"):
        return "[jina] disabled by env"
    try:
        resp = httpx.post(
            "https://s.jina.ai/",
            json={"q": query, "num": max_results},
            headers=_jina_headers(),
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        parts: list[str] = []
        for item in data:
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "") or item.get("description", "")
            parts.append(f"## {title}\nURL: {url}\n{content}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[jina] search failed: {exc}"


def jina_extract(url: str) -> str:
    """Extract content from a URL using Jina AI."""
    if _is_disabled("jina"):
        return "[jina] disabled by env"
    try:
        resp = httpx.get(
            f"https://r.jina.ai/{url}",
            headers=_jina_headers(),
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        title = data.get("title", "")
        content = data.get("content", "")
        return f"## {url}\n{title}\n{content}"
    except Exception as exc:  # noqa: BLE001
        return f"[jina] extract failed: {exc}"


def searxng_search(query: str, max_results: int = 10) -> str:
    """Search the web using a local SearXNG instance."""
    if _is_disabled("searxng"):
        return "[searxng] disabled by env"
    base = os.getenv("SEARXNG_URL", "http://localhost:8888").rstrip("/")
    try:
        resp = httpx.get(
            f"{base}/search",
            params={"q": query, "format": "json"},
            headers={"User-Agent": "search-extract/1.0"},
            timeout=60.0,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])[:max_results]
        parts: list[str] = []
        for item in results:
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")
            parts.append(f"## {title}\nURL: {url}\n{content}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[searxng] search failed: {exc}"


def firecrawl_search(query: str, max_results: int = 10) -> str:
    """Search the web using Firecrawl."""
    if _is_disabled("firecrawl"):
        return "[firecrawl] disabled by env"
    try:
        key = os.getenv("FIRECRAWL_API_KEY", "")
        app = Firecrawl(api_key=key) if key else Firecrawl()
        result = app.search(query, limit=max_results)
        parts: list[str] = []
        for item in getattr(result, "web", None) or []:
            title = getattr(item, "title", "")
            url = getattr(item, "url", "")
            content = getattr(item, "description", "")
            parts.append(f"## {title}\nURL: {url}\n{content}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[firecrawl] search failed: {exc}"


def firecrawl_extract(url: str) -> str:
    """Extract content from a URL using Firecrawl."""
    if _is_disabled("firecrawl"):
        return "[firecrawl] disabled by env"
    try:
        key = os.getenv("FIRECRAWL_API_KEY", "")
        app = Firecrawl(api_key=key) if key else Firecrawl()
        doc = app.scrape(url, formats=["markdown"])
        metadata = getattr(doc, "metadata", None)
        title = getattr(metadata, "title", "") if metadata else ""
        content = getattr(doc, "markdown", "") or ""
        return f"## {url}\n{title}\n{content}"
    except Exception as exc:  # noqa: BLE001
        return f"[firecrawl] extract failed: {exc}"


def parallel_search(query: str, max_results: int = 10) -> str:
    """Search the web using Parallel Web Systems."""
    if err := _guard("parallel", "PARALLEL_API_KEY"):
        return err
    key = os.getenv("PARALLEL_API_KEY", "")
    try:
        resp = httpx.post(
            "https://api.parallel.ai/v1/search",
            headers={"Content-Type": "application/json", "x-api-key": key},
            json={"search_queries": [query], "mode": "advanced"},
            timeout=60.0,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])[:max_results]
        parts: list[str] = []
        for item in results:
            title = item.get("title", "")
            url = item.get("url", "")
            excerpts = item.get("excerpts", None) or []
            excerpts_text = "\n".join(str(e) for e in excerpts)
            parts.append(f"## {title}\nURL: {url}\n{excerpts_text}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[parallel] search failed: {exc}"


def parallel_extract(url: str) -> str:
    """Extract content from a URL using Parallel Web Systems."""
    if err := _guard("parallel", "PARALLEL_API_KEY"):
        return err
    key = os.getenv("PARALLEL_API_KEY", "")
    try:
        resp = httpx.post(
            "https://api.parallel.ai/v1/extract",
            headers={"Content-Type": "application/json", "x-api-key": key},
            json={"urls": [url], "advanced_settings": {"full_content": True}},
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        parts: list[str] = []
        for item in data.get("results", []):
            item_url = item.get("url", "")
            title = item.get("title", "")
            full_content = item.get("full_content", "")
            excerpts = item.get("excerpts", None) or []
            body = full_content or "\n".join(str(e) for e in excerpts)
            parts.append(f"## {item_url}\n{title}\n{body}")
        for item in data.get("errors", []):
            item_url = item.get("url", "")
            error_type = item.get("error_type", "unknown error")
            parts.append(f"[failed] {item_url}: {error_type}")
        return "\n---\n".join(parts)
    except Exception as exc:  # noqa: BLE001
        return f"[parallel] extract failed: {exc}"


# --- Service registry & default selection -----------------------------------

# Services in priority order for default selection.
SEARCH_SERVICES = (
    "tavily",
    "exa",
    "ollama",
    "jina",
    "searxng",
    "parallel",
    "firecrawl",
)
EXTRACT_SERVICES = ("tavily", "exa", "ollama", "jina", "parallel", "firecrawl")

# Services that require an API key to be considered "available".
REQUIRED_KEYS: dict[str, str] = {
    "tavily": "TAVILY_API_KEY",
    "exa": "EXA_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "parallel": "PARALLEL_API_KEY",
}


def _service_available(service: str) -> bool:
    """Return True if a service is enabled and has its required key (if any)."""
    if _is_disabled(service):
        return False
    key = REQUIRED_KEYS.get(service)
    if key and not os.getenv(key):
        return False
    return True


def _default_service(services: tuple[str, ...]) -> str | None:
    """Return the first available service, or None if none are available."""
    for service in services:
        if _service_available(service):
            return service
    return None


def _resolve_service(
    services: tuple[str, ...], flags: list[tuple[str, bool]]
) -> str | None:
    """Resolve the service to use from explicit flags, else default to first available.

    ``flags`` is an ordered list of ``(service_name, is_set)``. Diagnostics go to
    stderr so stdout stays clean for LLM consumption.
    """
    chosen = [name for name, on in flags if on]
    if len(chosen) > 1:
        print(
            f"[error] multiple services selected: {', '.join(chosen)}; "
            "specify only one --<service> flag",
            file=sys.stderr,
        )
        return None
    if chosen:
        return chosen[0]
    service = _default_service(services)
    if not service:
        print(
            "[error] no available service. Set an API key (e.g. TAVILY_API_KEY) "
            "or enable a service.",
            file=sys.stderr,
        )
        return None
    print(
        f"[info] no service specified; using first available: {service}",
        file=sys.stderr,
    )
    return service


# --- App --------------------------------------------------------------------

app = App(
    name="search-extract",
    help="Web search and content extraction across multiple services.",
    help_epilogue=(
        "## Services\n\n"
        "| Command  | --<service> flags                                                |\n"
        "|----------|------------------------------------------------------------------|\n"
        "| search   | --tavily --exa --ollama --jina --searxng --parallel --firecrawl  |\n"
        "| extract  | --tavily --exa --ollama --jina --parallel --firecrawl            |\n\n"
        "Pick a backend with a --<service> flag. If none is given, the first\n"
        "available service (enabled + has its API key) is used automatically.\n"
        "Search defaults to 10 results; extract takes a single URL.\n\n"
        "## Examples\n\n"
        "```bash\n"
        'search --tavily "latest AI news"\n'
        'search --exa "quantum computing"\n'
        'search "open source LLMs"          # default to first available\n'
        "extract --jina https://example.com\n"
        "extract --tavily https://example.com\n"
        "extract https://example.com         # default to first available\n"
        "```"
    ),
)


@app.command
def search(
    query: Annotated[str, Parameter(help="Search query")],
    tavily: Annotated[bool, Parameter(name="--tavily", help="Use Tavily")] = False,
    exa: Annotated[bool, Parameter(name="--exa", help="Use Exa")] = False,
    ollama: Annotated[
        bool, Parameter(name="--ollama", help="Use Ollama Cloud")
    ] = False,
    jina: Annotated[bool, Parameter(name="--jina", help="Use Jina AI")] = False,
    searxng: Annotated[
        bool, Parameter(name="--searxng", help="Use local SearXNG")
    ] = False,
    parallel: Annotated[
        bool, Parameter(name="--parallel", help="Use Parallel Web Systems")
    ] = False,
    firecrawl: Annotated[
        bool, Parameter(name="--firecrawl", help="Use Firecrawl")
    ] = False,
    max_results: Annotated[
        int, Parameter(name="--max-results", help="Max results (default 10)")
    ] = 10,
) -> None:
    """Search the web. Pick a backend with a --<service> flag; defaults to first available."""
    flags = [
        ("tavily", tavily),
        ("exa", exa),
        ("ollama", ollama),
        ("jina", jina),
        ("searxng", searxng),
        ("parallel", parallel),
        ("firecrawl", firecrawl),
    ]
    service = _resolve_service(SEARCH_SERVICES, flags)
    if not service:
        return
    if service == "tavily":
        print(tavily_search(query, max_results))
    elif service == "exa":
        print(exa_search(query, max_results))
    elif service == "ollama":
        print(ollama_search(query, max_results))
    elif service == "jina":
        print(jina_search(query, max_results))
    elif service == "searxng":
        print(searxng_search(query, max_results))
    elif service == "parallel":
        print(parallel_search(query, max_results))
    elif service == "firecrawl":
        print(firecrawl_search(query, max_results))


@app.command
def extract(
    url: Annotated[str, Parameter(help="URL to extract")],
    tavily: Annotated[bool, Parameter(name="--tavily", help="Use Tavily")] = False,
    exa: Annotated[bool, Parameter(name="--exa", help="Use Exa")] = False,
    ollama: Annotated[
        bool, Parameter(name="--ollama", help="Use Ollama Cloud")
    ] = False,
    jina: Annotated[bool, Parameter(name="--jina", help="Use Jina AI")] = False,
    parallel: Annotated[
        bool, Parameter(name="--parallel", help="Use Parallel Web Systems")
    ] = False,
    firecrawl: Annotated[
        bool, Parameter(name="--firecrawl", help="Use Firecrawl")
    ] = False,
) -> None:
    """Extract content from a URL. Pick a backend with a --<service> flag; defaults to first available."""
    flags = [
        ("tavily", tavily),
        ("exa", exa),
        ("ollama", ollama),
        ("jina", jina),
        ("parallel", parallel),
        ("firecrawl", firecrawl),
    ]
    service = _resolve_service(EXTRACT_SERVICES, flags)
    if not service:
        return
    if service == "tavily":
        print(tavily_extract(url))
    elif service == "exa":
        print(exa_extract(url))
    elif service == "ollama":
        print(ollama_extract(url))
    elif service == "jina":
        print(jina_extract(url))
    elif service == "parallel":
        print(parallel_extract(url))
    elif service == "firecrawl":
        print(firecrawl_extract(url))


if __name__ == "__main__":
    app()
