# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "httpx>=0.28.1",
#     "python-dotenv>=1.2.2",
#     "tavily-python>=0.7.23",
#     "ollama>=0.6.1",
#     "cyclopts>=4.10.1",
#     "exa-py>=2.10.2",
#     "pyyaml>=6.0.3",
# ]
# ///

import os
from typing import Annotated, Literal

import dotenv
import ollama
import yaml
from cyclopts import App, Parameter, validators
from exa_py import Exa
from tavily import TavilyClient

dotenv.load_dotenv()


def _clean_empty(data):
    if hasattr(data, "__dict__"):
        data = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
    if isinstance(data, dict):
        return {
            k: _clean_empty(v) for k, v in data.items() if v not in (None, "", [], {})
        }
    elif isinstance(data, list):
        return [_clean_empty(item) for item in data if item not in (None, "", [], {})]
    return data


app = App(
    help_flags=["-h", "--help"],
    version_flags=["-v", "--version"],
    version="0.6.4",
)


@app.command(
    name="exa",
    help="Search the web using Exa's search capabilities",
)
def exa_search(
    query: str,
    max_results: Annotated[
        int, Parameter(validator=validators.Number(gte=5, lte=20))
    ] = 5,
) -> bool:
    if not os.getenv("EXA_API_KEY"):
        return False
    exa = Exa(api_key=os.getenv("EXA_API_KEY"))
    response = exa.search(
        query,
        num_results=max_results,
    )
    print(
        yaml.dump(_clean_empty(response.results), allow_unicode=True, sort_keys=False)
    )
    return True


@app.command(
    name="ollama",
    help="Search the web using Ollama's search capabilities",
)
def ollama_search(
    query: str,
    max_results: Annotated[
        int, Parameter(validator=validators.Number(gte=5, lte=10))
    ] = 5,
) -> bool:
    if not os.getenv("OLLAMA_API_KEY"):
        return False
    response = ollama.web_search(query, max_results=max_results)
    print(
        yaml.dump(_clean_empty(response.results), allow_unicode=True, sort_keys=False)
    )
    return True


@app.command(
    name="tavily",
    help="Search the web using Tavily's search capabilities",
)
def tavily_search(
    query: str,
    api_key: str | None = None,
    max_results: Annotated[
        int, Parameter(validator=validators.Number(gte=5, lte=10))
    ] = 5,
    topic: Literal["general", "news", "finance"] = "general",
) -> bool:

    key = api_key or os.getenv("TAVILY_API_KEY")
    if not key:
        return False

    client = TavilyClient(api_key=key)
    response = client.search(
        query,
        max_results=max_results,
        topic=topic,
    )
    print(yaml.dump(_clean_empty(response), allow_unicode=True, sort_keys=False))
    return True


if __name__ == "__main__":
    app()
