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


with st.sidebar:
    st.header("Settings")
    max_iterations = st.number_input(
        "Max Search Iterations",
        min_value=1,
        max_value=5,
        value=3,
        help="Caps how many search -> analyze -> review rounds the graph can run before it's forced to write the final report.",
    )
    st.markdown("---")
    st.markdown("### Agent Architecture")
    st.markdown("""
    1. **Planner Agent**: Generates core subtopics.
    2. **Search Agent**: Queries ArXiv, Tavily & Wikipedia.
    3. **Analyzer Agent**: Parallel document summarization.
    4. **Quality Reviewer**: Scores depth (0.0 to 1.0).
    5. **Final Reporter**: Compiles research paper.
    """)

query = st.text_input(
    "Enter your research query:",
    placeholder="e.g., Explain the architecture and capabilities of DeepSeek-V3"
)

run_button = st.button("Start Research", type="primary", use_container_width=True)


if "topics" not in st.session_state:
    st.session_state.topics = []
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "review" not in st.session_state:
    st.session_state.review = None  # {"score":..., "need_more":..., "missing":[...]}
if "final_report" not in st.session_state:
    st.session_state.final_report = None
if "run_complete" not in st.session_state:
    st.session_state.run_complete = False

if run_button and query:
    st.session_state.topics = []
    st.session_state.summaries = []
    st.session_state.review = None
    st.session_state.final_report = None
    st.session_state.run_complete = False

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
        "max_search_iterations": max_iterations,
    }

    status_container = st.status("🚀 Initializing research workflow...", expanded=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Research Plan & Topics")
        topics_box = st.empty()

    with col2:
        st.subheader("📊 Quality Review & Iterations")
        metrics_box = st.empty()

    summaries_expander = st.expander("📚 Extracted Summaries", expanded=False)

    for output in app_graph.stream(initial_state, config={"recursion_limit": 40}):
        for node_name, state_update in output.items():

            if node_name == "research":
                status_container.write("💡 **Planner Agent**: Subtopics generated.")
                topics = state_update.get("topics", [])
                st.session_state.topics = topics
                topics_box.markdown("\n".join([f"- {t}" for t in topics]))

            elif node_name == "search":
                count = state_update.get("search_count", 1)
                status_container.write(f"🔎 **Search Agent (Iteration {count})**: Querying web, arXiv, & Wikipedia...")

            elif node_name == "analyze":
                status_container.write("⚡ **Analyzer Agent**: Processing & summarizing retrieved documents...")
                if "summaries" in state_update:
                    st.session_state.summaries.extend(state_update["summaries"])
                    with summaries_expander:
                        for s in state_update["summaries"]:
                            st.info(s)

            elif node_name == "review":
                status_container.write("⚖️ **Quality Reviewer**: Evaluating coverage and quality score...")
                score = state_update.get("quality_score", 0.0)
                need_more = state_update.get("need_more_search", False)
                missing = state_update.get("missing_topics", [])
                st.session_state.review = {"score": score, "need_more": need_more, "missing": missing}

                with metrics_box.container():
                    m1, m2 = st.columns(2)
                    m1.metric("Quality Score", f"{score * 100:.0f}%")
                    m2.metric("Needs More Search", "Yes" if need_more else "No")

                    if missing:
                        st.warning(f"**Missing Topics Identified:**\n" + "\n".join([f"- {m}" for m in missing]))

            elif node_name == "final":
                status_container.write("📝 **Reporter Agent**: Drafting final research report...")
                status_container.update(label="✅ Research Complete!", state="complete", expanded=False)

                st.session_state.final_report = state_update.get("final_report", "No report generated.")
                st.session_state.run_complete = True

                st.markdown("---")
                st.subheader("📄 Final Research Report")
                st.markdown(st.session_state.final_report)

elif run_button and not query:
    st.warning("⚠️ Please enter a research query before starting.")

elif st.session_state.run_complete:
    st.info("Showing results from the last completed run.")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📋 Research Plan & Topics")
        st.markdown("\n".join([f"- {t}" for t in st.session_state.topics]))

    with col2:
        st.subheader("📊 Quality Review & Iterations")
        if st.session_state.review:
            m1, m2 = st.columns(2)
            m1.metric("Quality Score", f"{st.session_state.review['score'] * 100:.0f}%")
            m2.metric("Needs More Search", "Yes" if st.session_state.review["need_more"] else "No")
            if st.session_state.review["missing"]:
                st.warning(
                    "**Missing Topics Identified:**\n"
                    + "\n".join([f"- {m}" for m in st.session_state.review["missing"]])
                )

    with st.expander("📚 Extracted Summaries", expanded=False):
        for s in st.session_state.summaries:
            st.info(s)

    st.markdown("---")
    st.subheader("📄 Final Research Report")
    st.markdown(st.session_state.final_report or "No report generated.")
