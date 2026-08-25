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
    existing_docs_count = len(state.get("documents", []))

    topics = state.get("missing_topics") or state.get("topics", [])
    if not topics:
        return {"documents": [], "new_documents": []}

    system_message = SystemMessage(content=SEARCH_AGENT_PROMPT)
    user_message = HumanMessage(content=f"Research these topics:\n{topics}")
    messages = [system_message, user_message]

    response = llm_with_tools.invoke(messages)
    new_documents = []

    if hasattr(response, "tool_calls") and response.tool_calls:
        messages.append(response)
        tool_result = tool_node.invoke({"messages": messages})

        counter = existing_docs_count
        for message in tool_result["messages"]:
            if isinstance(message, ToolMessage) and message.content:
                extracted = extract_documents(message.content, counter)
                counter += len(extracted)
                new_documents.extend(extracted)

    return {
        "documents": new_documents,
        "new_documents": new_documents,
        "search_count": current_search_count,
    }
