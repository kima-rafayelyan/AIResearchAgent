import arxiv
import wikipediaapi
from langchain_core.tools import Tool, tool
#from langchain_community.tools.tavily_search import TavilySearchResults

wiki_api = wikipediaapi.Wikipedia(
    user_agent="MyResearchAgent/1.0 (contact@yourdomain.com)",
    language="en",
)

def wikipedia_search(query: str) -> str:
    try:
        page = wiki_api.page(query)
        if not page.exists():
            return f"No Wikipedia page found for '{query}'."
        return page.summary[:4000]
    except Exception as e:
        return f"Wikipedia lookup failed for '{query}': {e}"

wiki_tool = Tool(
    name="wikipedia",
    description=(
        "Use for general definitions, concepts, background, and established knowledge. "
        "Input should be a search query or topic name."
    ),
    func=wikipedia_search,
)

_arxiv_client = arxiv.Client(num_retries=3, delay_seconds=3.0)

@tool
def arxiv_tool(query: str) -> str:
    """Useful for searching scientific and research papers on ArXiv."""
    try:
        search = arxiv.Search(query=query, max_results=2)
        docs = []
        for result in _arxiv_client.results(search):
            docs.append(
                f"Published: {result.updated.date()}\n"
                f"Title: {result.title}\n"
                f"Authors: {', '.join(a.name for a in result.authors)}\n"
                f"Summary: {result.summary[:300]}"
            )
        return "\n\n".join(docs) if docs else "No papers found."
    except arxiv.HTTPError as e:
        return f"ArXiv search temporarily failed for '{query}': {e}"
    except Exception as e:
        return f"Unexpected error searching ArXiv for '{query}': {e}"

#tavily_tool = TavilySearchResults(max_results=5)

from langchain_tavily import TavilySearch

tavily_tool = TavilySearch(max_results=5)

all_tools = [wiki_tool, tavily_tool, arxiv_tool]
