from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from src.state import ResearchState
from src.agents import llm_with_tools
from src.tools import all_tools
from src.utils import extract_text

SEARCH_AGENT_PROMPT = """
You are a Search Agent.

Your job is to research the given topics by selecting and calling
the most appropriate search tools.

Available tools:

1. Wikipedia
   - General definitions
   - Concepts and background
   - Established knowledge

2. Tavily
   - General web search
   - Recent information
   - Practical applications
   - Diverse sources

3. arXiv
   - Academic papers
   - Scientific research
   - Machine learning
   - Artificial intelligence
   - Technical topics

Rules:
- Do NOT answer the research topics yourself.
- Use the tools to retrieve information.
- You may call multiple tools.
- You may call the same tool multiple times if necessary.
- Select the most appropriate tool for each topic.
"""

tool_node = ToolNode(all_tools)

def search_agent(state: ResearchState) -> dict:
    current_search_count = state.get("search_count", 0) + 1
    topics = state.get("missing_topics") or state.get("topics", [])

    if not topics:
        return {"documents": [], "new_documents": []}

    system_message = SystemMessage(content=SEARCH_AGENT_PROMPT)
    user_message = HumanMessage(content=f"Research these topics:\n{topics}")

    response = llm_with_tools.invoke([system_message, user_message])
    new_documents = []

    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_result = tool_node.invoke({"messages": [response]})
        new_documents = [
            extract_text(message.content)
            for message in tool_result["messages"]
            if message.content
        ]
        new_documents = [doc for doc in new_documents if doc]
    else:
        print("\n⚠ Search Agent didn't call any tools.")

    return {
        "documents": new_documents,
        "new_documents": new_documents,
        "search_count": current_search_count,
    }
