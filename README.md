# 🔍 AI Research Agent

A multi-agent deep-research system built with **LangGraph**. Give it a research question and it will plan sub-topics, search the web/Wikipedia/ArXiv, summarize what it finds, grade its own research quality, loop back to search again if coverage is weak, and produce a final, cited report.

Comes with two interfaces:
- **CLI** (`main.py`) — quick terminal usage
- **Streamlit web app** (`app.py`) — live, visual view of the agent working through each step

## How it works

```
Planner → Search → Analyze → Review ─┬─▶ (loop back to Search if quality < 0.85)
                                       └─▶ Reporter → Final cited report
```

1. **Planner Agent** — breaks your question into 4–5 focused, independently-researchable sub-topics.
2. **Search Agent** — researches each topic using Wikipedia, Tavily (web search), and ArXiv, choosing the right tool per topic.
3. **Analyzer Agent** — summarizes every retrieved document in parallel.
4. **Quality Reviewer** — scores the research (0.0–1.0) for completeness, relevance, depth, accuracy, and coverage. If the score is below 0.85, it sends the agent back to search for the specific missing topics (up to 5 iterations).
5. **Reporter Agent** — writes the final answer as a structured, cited Markdown report with a References section.

## Requirements

- Python 3.10+
- API keys for:
  - **OpenRouter** (LLM access) — [openrouter.ai](https://openrouter.ai)
  - **Tavily** (web search) — [tavily.com](https://tavily.com)

## Setup

1. **Clone and enter the project**
   ```bash
   git clone <your-repo-url>
   cd AIResearchAgent
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example file and fill in your keys:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:
   ```env
   OPENROUTER_API_KEY="your_openrouter_api_key_here"
   OPENROUTER_MODEL="google/gemini-2.5-flash"
   TAVILY_API_KEY="your_tavily_api_key_here"
   ```

## Usage

### Command line

```bash
python main.py
```

You'll be prompted to enter a research question. The final report prints to the terminal once the agent finishes.

### Web app (Streamlit)

```bash
streamlit run app.py
```

Opens a browser dashboard where you can:
- Enter a research query and set the max search iterations
- Watch the research plan, search rounds, extracted summaries, and quality score update live
- Read the final report, fully formatted with citations

## Project structure

```
AIResearchAgent/
├── main.py                # CLI entry point
├── app.py                 # Streamlit web UI
├── requirements.txt
├── .env.example            # Template for required API keys
└── src/
    ├── config.py            # Env vars & settings (model, max iterations)
    ├── state.py             # Shared graph state (ResearchState) definition
    ├── schemas.py           # Pydantic schemas for structured LLM output
    ├── tools.py             # Wikipedia / Tavily / ArXiv tool definitions
    ├── utils.py             # Helpers for parsing LLM/tool output
    ├── graph.py             # LangGraph wiring: nodes, edges, routing logic
    └── agents/
        ├── __init__.py       # Shared LLM client setup
        ├── planner.py        # Research Agent — generates sub-topics
        ├── search.py         # Search Agent — ReAct tool-calling loop
        ├── analyzer.py       # Analyzer Agent — parallel summarization
        ├── reviewer.py       # Quality Reviewer — scores & routes
        └── reporter.py       # Final Reporter — writes the cited report
```

## Configuration notes

- `MAX_SEARCH_ITERATIONS` (default `5`, in `src/config.py`) caps how many times the Search → Analyze → Review loop can repeat before the system forces a final report with whatever research it has.
- The reviewer's pass threshold is a `quality_score >= 0.85`; anything lower triggers another search round (subject to the iteration cap above).
- The app uses OpenRouter as an OpenAI-compatible endpoint, so `OPENROUTER_MODEL` can be swapped for any model OpenRouter supports (e.g. other Gemini, Claude, or GPT variants) without code changes.


