import json

import arxiv
import wikipedia
import wikipediaapi
from langchain_core.tools import Tool, tool
from langchain_tavily import TavilySearch

wiki_api = wikipediaapi.Wikipedia(
    user_agent="MyResearchAgent/1.0 (contact@yourdomain.com)",
    language="en",
)


def wikipedia_search(query: str) -> str:
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return json.dumps({"error": f"No Wikipedia page found for '{query}'."})

        best_title = search_results[0]

        page = wiki_api.page(best_title)
        if not page.exists():
            return json.dumps({"error": f"No Wikipedia page found for '{query}'."})

        return json.dumps(
            {
                "title": page.title,
                "url": page.fullurl,
                "source": "Wikipedia",
                "content": page.summary[:4000],
            }
        )
    except Exception as e:
        return json.dumps({"error": f"Wikipedia lookup failed: {e}"})


wiki_tool = Tool(
    name="wikipedia",
    description="General definitions, concepts, and background knowledge.",
    func=wikipedia_search,
)


_arxiv_client = arxiv.Client(num_retries=3, delay_seconds=3.0)


@tool
def arxiv_tool(query: str) -> str:
    """Useful for searching scientific and research papers on ArXiv."""
    try:
        search = arxiv.Search(query=query, max_results=2)
        results = []
        for result in _arxiv_client.results(search):
            results.append(
                {
                    "title": result.title,
                    "url": result.entry_id,
                    "authors": [a.name for a in result.authors],
                    "published": str(result.updated.date()),
                    "source": "ArXiv",
                    "content": result.summary[:1000],
                }
            )
        return json.dumps(results) if results else json.dumps([])
    except Exception as e:
        return json.dumps({"error": f"ArXiv search failed: {e}"})


tavily_tool = TavilySearch(max_results=5)

all_tools = [wiki_tool, tavily_tool, arxiv_tool]
