from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from src.state import ResearchState
from src.agents import llm_with_tools, llm_with_tools_forced
from src.tools import all_tools
from src.utils import extract_text, extract_documents

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
- After reviewing tool results, if important topics are still uncovered,
  call more tools before you're done. Only stop once every topic has
  meaningful coverage.
"""

tool_node = ToolNode(all_tools)


MAX_REACT_STEPS = 4

def search_agent(state: ResearchState) -> dict:
    current_search_count = state.get("search_count", 0) + 1
    existing_docs_count = len(state.get("documents", []))

    topics = state.get("missing_topics") or state.get("topics", [])
    if not topics:
        return {"documents": [], "new_documents": [], "search_count": current_search_count}

    system_message = SystemMessage(content=SEARCH_AGENT_PROMPT)
    user_message = HumanMessage(content=f"Research these topics:\n{topics}")
    messages = [system_message, user_message]

    new_documents = []
    counter = existing_docs_count

    for step in range(MAX_REACT_STEPS):

        model = llm_with_tools_forced if step == 0 else llm_with_tools
        response = model.invoke(messages)
        messages.append(response)

        if not (hasattr(response, "tool_calls") and response.tool_calls):
            if step == 0:
                print("\n⚠ Search Agent didn't call any tools for these topics:")
                for t in topics:
                    print(f"  - {t}")
            else:
                print(f"\n✓ Search Agent stopped after {step} round(s) of tool calls (model judged coverage sufficient).")
            break

        tool_result = tool_node.invoke({"messages": messages})
        tool_messages = tool_result["messages"]
        messages.extend(tool_messages)

        step_doc_count = 0
        for message in tool_messages:
            if isinstance(message, ToolMessage) and message.content:
                extracted = extract_documents(message.content, counter)
                counter += len(extracted)
                step_doc_count += len(extracted)
                new_documents.extend(extracted)

        print(f"  Round {step + 1}/{MAX_REACT_STEPS}: {len(tool_messages)} tool call(s) -> {step_doc_count} document(s)")
    else:
        print(f"\n⚠ Search Agent hit the {MAX_REACT_STEPS}-round cap; stopping with what's been gathered so far.")

    return {
        "documents": new_documents,
        "new_documents": new_documents,
        "search_count": current_search_count,
    }
