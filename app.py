import streamlit as st
from src.state import ResearchState
from src.graph import app_graph

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Multi-Agent Deep Research System")
st.caption("Powered by LangGraph, Google Gemini, Tavily, Wikipedia & ArXiv")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    max_iterations = st.number_input("Max Search Iterations", min_value=1, max_value=5, value=3)
    st.markdown("---")
    st.markdown("### Agent Architecture")
    st.markdown("""
    1. **Planner Agent**: Generates core subtopics.
    2. **Search Agent**: Queries ArXiv, Tavily & Wikipedia.
    3. **Analyzer Agent**: Parallel document summarization.
    4. **Quality Reviewer**: Scores depth (0.0 to 1.0).
    5. **Final Reporter**: Compiles research paper.
    """)

# Query Input
query = st.text_input(
    "Enter your research query:",
    placeholder="e.g., Explain the architecture and capabilities of DeepSeek-V3"
)

run_button = st.button("Start Research", type="primary", use_container_width=True)

if run_button and query:
    initial_state: ResearchState = {
        "query": query,
        "topics": [],
        "documents": [],
        "new_documents": [],
        "summaries": [],
        "quality_score": 0.0,
        "need_more_search": False,
        "missing_topics": [],
        "review_feedback": "",
        "final_report": "",
        "search_count": 0,
    }

    # UI Containers for Live Updates
    status_container = st.status("🚀 Initializing research workflow...", expanded=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Research Plan & Topics")
        topics_box = st.empty()

    with col2:
        st.subheader("📊 Quality Review & Iterations")
        metrics_box = st.empty()

    summaries_expander = st.expander("📚 Extracted Summaries", expanded=False)

    # Streaming LangGraph Steps
    for output in app_graph.stream(initial_state, config={"recursion_limit": 40}):
        for node_name, state_update in output.items():

            if node_name == "research":
                status_container.write("💡 **Planner Agent**: Subtopics generated.")
                topics = state_update.get("topics", [])
                topics_box.markdown("\n".join([f"- {t}" for t in topics]))

            elif node_name == "search":
                count = state_update.get("search_count", 1)
                status_container.write(f"🔎 **Search Agent (Iteration {count})**: Querying web, arXiv, & Wikipedia...")

            elif node_name == "analyze":
                status_container.write("⚡ **Analyzer Agent**: Processing & summarizing retrieved documents...")
                if "summaries" in state_update:
                    with summaries_expander:
                        for s in state_update["summaries"]:
                            st.info(s)

            elif node_name == "review":
                status_container.write("⚖️ **Quality Reviewer**: Evaluating coverage and quality score...")
                score = state_update.get("quality_score", 0.0)
                need_more = state_update.get("need_more_search", False)
                missing = state_update.get("missing_topics", [])

                with metrics_box.container():
                    m1, m2 = st.columns(2)
                    m1.metric("Quality Score", f"{score * 100:.0f}%")
                    m2.metric("Needs More Search", "Yes" if need_more else "No")

                    if missing:
                        st.warning(f"**Missing Topics Identified:**\n" + "\n".join([f"- {m}" for m in missing]))

            elif node_name == "final":
                status_container.write("📝 **Reporter Agent**: Drafting final research report...")
                status_container.update(label="✅ Research Complete!", state="complete", expanded=False)

                st.markdown("---")
                st.subheader("📄 Final Research Report")
                st.markdown(state_update.get("final_report", "No report generated."))


