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
## Dependency management

Dependencies are declared in `requirements.in` / `requirements-dev.in` and pinned into `requirements.txt` / `requirements-dev.txt` via [pip-tools](https://github.com/jazzband/pip-tools). Lockfiles are compiled with **Python 3.12** to match the project's target and CI environment — don't regenerate them with a different interpreter, as resolved versions can differ across Python versions.

Install (runtime only):
```bash
pip install -r requirements.txt
```

Install (with dev tools, e.g. pytest/ruff):
```bash
pip install -r requirements-dev.txt
```

Recompile the lockfiles after changing an `.in` file:
```bash
pip install pip-tools
pip-compile --output-file=requirements.txt requirements.in
pip-compile --output-file=requirements-dev.txt requirements-dev.in
```


## Configuration notes

- `MAX_SEARCH_ITERATIONS` (default `5`, in `src/config.py`) caps how many times the Search → Analyze → Review loop can repeat before the system forces a final report with whatever research it has.
- The reviewer's pass threshold is a `quality_score >= 0.85`; anything lower triggers another search round (subject to the iteration cap above).
- The app uses OpenRouter as an OpenAI-compatible endpoint, so `OPENROUTER_MODEL` can be swapped for any model OpenRouter supports (e.g. other Gemini, Claude, or GPT variants) without code changes.


## Deployment

Two deployments exist for this app:

- **Streamlit Community Cloud** — quickest path to a public URL, deploys straight from the repo, no Docker involved.
- **Fly.io** — runs the Docker image from the `Dockerfile`, with a healthcheck, real logs, and CI-gated auto-deploy.

### Streamlit Community Cloud

1. Push the branch you want live to GitHub (already required, since Cloud deploys from a GitHub repo).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, click **New app**.
3. Pick this repo, branch `main`, main file path `app.py`.
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   OPENROUTER_API_KEY = "sk-..."
   TAVILY_API_KEY = "tvly-..."
   ```
   Streamlit Cloud injects these as environment variables at runtime, so `src/config.py`'s `os.getenv(...)` picks them up with no code changes. Nothing secret is ever committed.
5. Click **Deploy**. Redeploys happen automatically on every push to the configured branch; you can also trigger a manual redeploy or reboot from the app's "Manage app" menu.
6. **Rollback:** Streamlit Cloud always runs the latest commit on the tracked branch. To roll back, `git revert` the bad commit (or push a previous commit to `main`) and let it redeploy — there's no separate "previous version" button.
7. **Logs:** "Manage app" → the app's log panel, streamed live from the container. This is the fastest place to check when the deployed app errors but your local run doesn't.

### Fly.io (Docker deployment)

**One-time setup:**
```bash
# install the CLI, then:
fly auth login
fly launch --no-deploy   # detects the Dockerfile, writes/confirms fly.toml, picks a region
```
This repo already includes a `fly.toml` (internal port `8501`, healthcheck on `/_stcore/health`, matching the `HEALTHCHECK` in the `Dockerfile`) — `fly launch` will offer to reuse it.

Set secrets on the platform (never in `fly.toml`, which is committed):
```bash
fly secrets set OPENROUTER_API_KEY=sk-... TAVILY_API_KEY=tvly-...
```

Manual deploy (first time, or ad hoc):
```bash
fly deploy
```

**Automatic deploy on merge to `main`, gated on CI:**
`.github/workflows/deploy.yml` listens for the `CI` workflow (`.github/workflows/ci.yml`) to finish on `main`, and only runs `flyctl deploy` if that run's conclusion was `success`. A failing lint/test run does not deploy. This requires one repo secret:
- `FLY_API_TOKEN` — generate with `fly tokens create deploy`, add it under GitHub repo **Settings → Secrets and variables → Actions**.

**Rollback:**
```bash
fly releases           # list past releases with version numbers
fly deploy --image <previous-image-ref>   # or:
fly releases rollback <version>
```

**Logs (including a specific failed request):**
```bash
fly logs                       # live tail
fly logs --region iad          # scope to a region if you run multiple
```
Streamlit's own request/error output goes to stdout/stderr inside the container, which Fly captures automatically — no extra logging setup needed. To find one specific failed request, tail `fly logs` and grep for the timestamp or traceback text; for anything you need to search after the fact (Fly's free-tier log retention is short), pipe `fly logs` into a file or forward to a log drain (`fly logs --json` works well with `jq`/`grep` for that).

**Where to look when something breaks:**
1. `fly status` — is the machine even running / healthy?
2. `fly logs` — the actual error/traceback.
3. GitHub Actions tab, `Deploy` workflow — did the last deploy run at all, and did the CI run it's gated on pass?
4. `fly secrets list` — confirms `OPENROUTER_API_KEY` / `TAVILY_API_KEY` are set (it shows names + digests, never values).


