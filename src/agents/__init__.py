from langchain_openai import ChatOpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from src.tools import all_tools

llm = ChatOpenAI(
    model=OPENROUTER_MODEL,
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    max_tokens=4096, 
    temperature=0,
    extra_body={"reasoning": {"exclude": True}},
)

llm_with_tools_forced = llm.bind_tools(all_tools, tool_choice="required")
llm_with_tools = llm.bind_tools(all_tools)
