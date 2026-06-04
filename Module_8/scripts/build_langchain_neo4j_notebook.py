#!/usr/bin/env python3
"""Generate Module_8_Using_Knowledge_Graph_with_LangChain.ipynb with rich markdown."""
import json
from pathlib import Path


def md(*lines: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}


def code(*lines: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "outputs": [], "source": [l + "\n" for l in lines]}


cells: list = []

# =============================================================================
# Title & introduction
# =============================================================================
cells.append(
    md(
        "# Using Knowledge Graph with LangChain",
        "",
        "**Course module:** Module 8",
        "**Audience:** Beginners with basic graph/Neo4j knowledge, Python, and introductory LangChain experience.",
        "",
        "## Course description",
        "",
        "In this course, you will learn how to integrate **Neo4j** into your **LangChain** applications,",
        "enabling you to leverage graph databases in Generative AI workflows.",
        "",
        "**You will learn how to:**",
        "",
        "- Use the **`langchain-neo4j`** package to interact with Neo4j from LangChain.",
        "- Create **RAG** and **GraphRAG** retrievers.",
        "- Implement and customize a **text-to-Cypher** retriever.",
        "- Create a simple **LangChain agent** that interacts with Neo4j.",
        "",
        "> **Language:** All instructional text is in **English**.",
        "",
        "> **Setup (required before code):** Complete **`NEO4J_SETUP.md`** and **`LLM_MODEL_SETUP.md`**.",
        "> For local LLMs, run `ollama serve` and use **`ollama_model_runner.py`** as described in the LLM guide.",
        "",
        "### How to use this notebook",
        "",
        "1. Read each **markdown** cell before running the **code** cell below it.",
        "2. Run cells **in order** from Step 0 downward (later cells depend on earlier variables).",
        "3. If a cell fails, check the troubleshooting notes in the markdown above it.",
        "4. Re-running the notebook is safe: lab data uses the `LangChainLab` label and can be re-seeded.",
    )
)

cells.append(
    md(
        "## Prerequisites",
        "",
        "Before taking this course, you should have:",
        "",
        "- A basic understanding of **graph databases** and **Neo4j** (nodes, relationships, Cypher `MATCH`).",
        "- Knowledge of **Python** and basic familiarity with **LangChain** (chains, prompts, runnables).",
        "- A running Neo4j **5.15+** instance (see `NEO4J_SETUP.md`).",
        "",
        "### Concepts you will use",
        "",
        "| Concept | Meaning in this course |",
        "|---------|------------------------|",
        "| **RAG** | Retrieve relevant text, then ask an LLM with that context |",
        "| **GraphRAG** | RAG plus graph traversal for structured facts |",
        "| **Text-to-Cypher** | LLM writes a Cypher query from natural language |",
        "| **Retriever** | LangChain object that returns `Document` chunks for a query |",
        "| **Agent** | LLM loop that picks tools (Cypher, QA chain) step by step |",
        "",
        "## Course outline",
        "",
        "| Part | Topic |",
        "|------|--------|",
        "| **3.1** | Neo4j and LangChain |",
        "| **3.2** | Vectors |",
        "| **3.3** | Text to Cypher |",
        "",
        "### 3.1 Neo4j and LangChain",
        "",
        "| Section | Topic |",
        "|---------|--------|",
        "| 0 | Development environment & connectivity |",
        "| 3.1.1 | Neo4j integration (`langchain-neo4j`) |",
        "| 3.1.2 | `Neo4jGraph` — schema and queries |",
        "| 3.1.3 | Seed the LangChain lab graph |",
        "| 3.1.4 | Simple LangChain agent |",
        "",
        "### 3.2 Vectors",
        "",
        "| Section | Topic |",
        "|---------|--------|",
        "| 3.2.1 | Vector search (`Neo4jVector`) |",
        "| 3.2.2 | Vector retriever (RAG) |",
        "| 3.2.3 | Graph retrieval (GraphRAG) |",
        "| 3.2.4 | Additional data (optional) |",
        "",
        "### 3.3 Text to Cypher",
        "",
        "| Section | Topic |",
        "|---------|--------|",
        "| 3.3.1 | Schema introspection |",
        "| 3.3.2 | Cypher generation (`GraphCypherQAChain`) |",
        "| 3.3.3 | Customize the chain |",
        "| 3.3.4 | Text-to-Cypher as a retriever |",
    )
)

# =============================================================================
# Step 0
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Step 0 — Development environment",
        "",
        "This section prepares your Python environment, loads secrets from `.env`, and confirms",
        "that **Neo4j** and your **LLM** are reachable before we build LangChain components.",
        "",
        "### Before you run any code",
        "",
        "1. Complete **`NEO4J_SETUP.md`** — Aura, Desktop, or Docker; note URI, username, password.",
        "2. Complete **`LLM_MODEL_SETUP.md`** — Ollama + `ollama_model_runner.py` (recommended) or OpenAI.",
        "3. Copy `Module_8/.env.example` → `Module_8/.env` and fill in credentials.",
        "4. Start Neo4j (instance **Running**) and, for Ollama, run `ollama serve` in a terminal.",
        "",
        "### What Step 0 does",
        "",
        "| Step | Purpose |",
        "|------|---------|",
        "| 0a | Install Python packages |",
        "| 0b | Load paths and environment variables |",
        "| 0c | Verify Neo4j Bolt connectivity |",
        "| 0d | Wire Ollama runner → LangChain `llm` / `chat_llm` |",
        "| 0e | Smoke-test the runner (Ollama only) |",
    )
)

cells.append(
    md(
        "### Step 0a — Install Python packages",
        "",
        "We install the **Neo4j driver**, **LangChain** core libraries, the official **`langchain-neo4j`**",
        "integration, and **sentence-transformers** for local embeddings (Section 3.2).",
        "",
        "| Package | Role |",
        "|---------|------|",
        "| `neo4j` | Official database driver (Bolt protocol) |",
        "| `langchain-neo4j` | `Neo4jGraph`, `Neo4jVector`, `GraphCypherQAChain` |",
        "| `langchain-classic` | ReAct agent helpers (`create_react_agent`) |",
        "| `python-dotenv` | Load `Module_8/.env` without exporting variables manually |",
        "| `sentence-transformers` | Embedding model for vector index |",
        "",
        "**Note:** Run this cell once per virtual environment. If versions conflict, restart the kernel after install.",
    )
)

cells.append(
    code(
        "# Step 0a — Install dependencies (run once per environment)",
        "%pip install -q neo4j python-dotenv requests \\",
        "    langchain langchain-community langchain-classic langchain-neo4j \\",
        "    langchain-openai sentence-transformers",
    )
)

cells.append(
    md(
        "### Step 0b.1 — Resolve the `Module_8` directory",
        "",
        "Jupyter's working directory depends on how you launched the notebook:",
        "",
        "- From repo root → we detect `Module_8/` as a subfolder.",
        "- From `Module_8/` → we use the current folder.",
        "",
        "We then call `load_dotenv(MODULE_DIR / '.env')` so `NEO4J_*` and `LLM_*` variables are available",
        "to every later cell without hard-coding secrets in the notebook.",
    )
)

cells.append(
    code(
        "# Step 0b.1 — Module path and .env",
        "import os",
        "from pathlib import Path",
        "from dotenv import load_dotenv",
        "",
        "MODULE_DIR = Path('.').resolve()",
        "if MODULE_DIR.name != 'Module_8':",
        "    candidate = MODULE_DIR / 'Module_8'",
        "    if candidate.is_dir():",
        "        MODULE_DIR = candidate.resolve()",
        "load_dotenv(MODULE_DIR / '.env')",
        "print('Module directory:', MODULE_DIR)",
    )
)

cells.append(
    md(
        "**Expected output:** A path ending in `.../Module_8`.",
        "",
        "If this path is wrong, use **File → Open** from inside `Module_8/` or set the Jupyter root accordingly.",
    )
)

cells.append(
    md(
        "### Step 0b.2 — Neo4j connection settings",
        "",
        "These variables must match your deployment (see **`NEO4J_SETUP.md`**):",
        "",
        "| Variable | Typical local (Docker/Desktop) | Aura cloud |",
        "|----------|-------------------------------|------------|",
        "| `NEO4J_URI` | `neo4j://localhost:7687` | `neo4j+s://....databases.neo4j.io` |",
        "| `NEO4J_USERNAME` | `neo4j` | `neo4j` |",
        "| `NEO4J_PASSWORD` | your instance password | from Aura credentials file |",
        "| `NEO4J_DATABASE` | `neo4j` | `neo4j` |",
        "",
        "**Security:** Never commit real passwords to Git. Use `.env` only (gitignored).",
    )
)

cells.append(
    code(
        "# Step 0b.2 — Neo4j settings",
        "NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')",
        "NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')",
        "NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')",
        "NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')",
        "print('Neo4j URI:', NEO4J_URI)",
        "print('Neo4j database:', NEO4J_DATABASE)",
    )
)

cells.append(
    md(
        "### Step 0b.3 — LLM backend and optional corpus path",
        "",
        "This notebook uses an LLM in three ways:",
        "",
        "1. **Text-to-Cypher** (`GraphCypherQAChain`) — needs strong instruction-following.",
        "2. **RAG / GraphRAG answers** — chat-style prompts.",
        "3. **ReAct agent** — multi-step reasoning with tools.",
        "",
        "| `LLM_BACKEND` | How the notebook calls the model |",
        "|---------------|-----------------------------------|",
        "| `ollama` (default) | Subprocess → `ollama_model_runner.py` → Ollama HTTP API |",
        "| `openai` | `ChatOpenAI` with `OPENAI_API_KEY` |",
        "",
        "The **Ollama + runner** path matches other KMOU modules: the Jupyter kernel stays light,",
        "and long prompts run in a separate process (see **`LLM_MODEL_SETUP.md`**).",
        "",
        "`CORPUS_PATH` points to optional extra text for Section 3.2.4 — not required for the core lab.",
    )
)

cells.append(
    code(
        "# Step 0b.3 — LLM settings",
        "LLM_BACKEND = os.getenv('LLM_BACKEND', 'ollama').lower()",
        "OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')",
        "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')",
        "OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', '0'))",
        "OLLAMA_MAX_TOKENS = int(os.getenv('OLLAMA_MAX_TOKENS', '2048'))",
        "OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')",
        "CORPUS_PATH = MODULE_DIR / 'data' / 'dbpedia_maritime_corpus.txt'",
        "print('LLM backend:', LLM_BACKEND)",
        "print('Corpus for vectors:', CORPUS_PATH.name, '| exists:', CORPUS_PATH.is_file())",
        "if LLM_BACKEND == 'ollama':",
        "    print('Ollama host:', OLLAMA_HOST)",
        "    print('Ollama model:', OLLAMA_MODEL)",
    )
)

cells.append(
    md(
        "### Step 0c — Verify Neo4j connectivity",
        "",
        "We open a short-lived **Bolt** session using the official `neo4j` driver.",
        "This is the same protocol LangChain's `Neo4jGraph` uses under the hood.",
        "",
        "**If this cell fails:**",
        "",
        "- `NEO4J_PASSWORD is empty` → fill `Module_8/.env`.",
        "- `ServiceUnavailable` → database not running or wrong URI scheme.",
        "- `Authentication failed` → password mismatch (Docker `NEO4J_AUTH` must match `.env`).",
    )
)

cells.append(
    code(
        "# Step 0c — Neo4j smoke test",
        "from neo4j import GraphDatabase",
        "",
        "if not NEO4J_PASSWORD:",
        "    raise ValueError('NEO4J_PASSWORD is empty. See NEO4J_SETUP.md and Module_8/.env')",
        "",
        "_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))",
        "with _driver.session(database=NEO4J_DATABASE) as session:",
        "    msg = session.run('RETURN \"Neo4j connection OK\" AS message').single()['message']",
        "    print(msg)",
        "_driver.close()",
        "print('Connectivity check passed.')",
    )
)

cells.append(
    md(
        "**Expected output:** `Neo4j connection OK` then `Connectivity check passed.`",
        "",
        "You can also confirm in **Neo4j Browser** with:",
        "",
        "```cypher",
        "RETURN \"Neo4j connection OK\" AS message;",
        "```",
    )
)

cells.append(
    md(
        "### Step 0d — Ollama runner helpers",
        "",
        "LangChain expects model objects (`LLM`, `BaseChatModel`). Our course runner is a **CLI script**",
        "that returns JSON on stdout. We bridge the gap with:",
        "",
        "1. **`call_ollama_runner()`** — writes prompt to temp file, runs subprocess, parses JSON.",
        "2. **`OllamaRunnerLLM`** — used by `GraphCypherQAChain` and the ReAct agent.",
        "3. **`OllamaRunnerChatModel`** — used by RAG chains that expect chat messages.",
        "",
        "This mirrors **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** and **`LLM_MODEL_SETUP.md`**.",
    )
)

cells.append(
    md(
        "#### Step 0d.1 — Locate `ollama_model_runner.py`",
        "",
        "Search order: `Module_8/` → `Module_4/` (fallback) → current directory.",
    )
)

cells.append(
    code(
        "# Step 0d.1 — Locate ollama_model_runner.py",
        "import json",
        "import subprocess",
        "import sys",
        "import tempfile",
        "from typing import Any, List, Optional",
        "",
        "from langchain_core.callbacks import CallbackManagerForLLMRun",
        "from langchain_core.language_models.chat_models import BaseChatModel",
        "from langchain_core.language_models.llms import LLM",
        "from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage",
        "from langchain_core.outputs import ChatGeneration, ChatResult",
        "",
        "",
        "def _resolve_ollama_runner_path() -> Path:",
        "    for candidate in (",
        "        MODULE_DIR / 'ollama_model_runner.py',",
        "        MODULE_DIR.parent / 'Module_4' / 'ollama_model_runner.py',",
        "        Path('ollama_model_runner.py'),",
        "    ):",
        "        if candidate.exists():",
        "            return candidate.resolve()",
        "    raise FileNotFoundError('ollama_model_runner.py not found (see LLM_MODEL_SETUP.md)')",
        "",
        "",
        "OLLAMA_RUNNER = _resolve_ollama_runner_path()",
        "print('OLLAMA_RUNNER:', OLLAMA_RUNNER)",
    )
)

cells.append(
    md(
        "#### Step 0d.2 — `call_ollama_runner()`",
        "",
        "Parameters passed to the script:",
        "",
        "| Flag | Source |",
        "|------|--------|",
        "| `--host` | `OLLAMA_HOST` |",
        "| `--models` | `OLLAMA_MODEL` |",
        "| `--prompt-file` | temp file with full prompt |",
        "| `--temperature` | `OLLAMA_TEMPERATURE` (0 for deterministic lab) |",
        "| `--max-tokens` | `OLLAMA_MAX_TOKENS` (raise if answers are cut off) |",
        "",
        "The function returns `outputs[0].response` from the JSON printed by the runner.",
    )
)

cells.append(
    code(
        "# Step 0d.2 — call_ollama_runner()",
        "def call_ollama_runner(prompt: str, *, model: str | None = None) -> str:",
        "    model_arg = model or OLLAMA_MODEL",
        "    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as pf:",
        "        path = pf.name",
        "        pf.write(prompt)",
        "    try:",
        "        cmd = [",
        "            sys.executable, str(OLLAMA_RUNNER),",
        "            '--host', OLLAMA_HOST,",
        "            '--models', model_arg,",
        "            '--prompt-file', path,",
        "            '--temperature', str(OLLAMA_TEMPERATURE),",
        "            '--max-tokens', str(OLLAMA_MAX_TOKENS),",
        "        ]",
        "        run = subprocess.run(cmd, capture_output=True, text=True)",
        "        if run.returncode != 0:",
        "            raise RuntimeError(f'runner exit {run.returncode}\\n{run.stderr[:4000]}')",
        "        payload = json.loads(run.stdout)",
        "        first = (payload.get('outputs') or [{}])[0]",
        "        if first.get('status') != 'ok':",
        "            raise RuntimeError(f'Ollama error: {first}')",
        "        return (first.get('response') or '').strip()",
        "    finally:",
        "        Path(path).unlink(missing_ok=True)",
    )
)

cells.append(
    md(
        "#### Step 0d.3 — LangChain adapter classes",
        "",
        "- **`OllamaRunnerLLM`** implements `_call(prompt) → str` for classic LLM chains.",
        "- **`OllamaRunnerChatModel`** flattens message lists into one prompt string",
        "  (sufficient for this course; production apps may prefer native chat APIs).",
    )
)

cells.append(
    code(
        "# Step 0d.3 — LangChain LLM and ChatModel adapters",
        "class OllamaRunnerLLM(LLM):",
        "    model: str = OLLAMA_MODEL",
        "",
        "    @property",
        "    def _llm_type(self) -> str:",
        "        return 'ollama_runner'",
        "",
        "    def _call(self, prompt: str, stop: Optional[List[str]] = None,",
        "              run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> str:",
        "        return call_ollama_runner(prompt, model=self.model)",
        "",
        "",
        "class OllamaRunnerChatModel(BaseChatModel):",
        "    model: str = OLLAMA_MODEL",
        "",
        "    @property",
        "    def _llm_type(self) -> str:",
        "        return 'ollama_runner_chat'",
        "",
        "    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:",
        "        parts = []",
        "        for m in messages:",
        "            if isinstance(m, SystemMessage):",
        "                parts.append(f'System: {m.content}')",
        "            elif isinstance(m, HumanMessage):",
        "                parts.append(f'User: {m.content}')",
        "            elif isinstance(m, AIMessage):",
        "                parts.append(f'Assistant: {m.content}')",
        "            else:",
        "                parts.append(str(m.content))",
        "        parts.append('Assistant:')",
        "        return '\\n'.join(parts)",
        "",
        "    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None,",
        "                  run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> ChatResult:",
        "        text = call_ollama_runner(self._messages_to_prompt(messages), model=self.model)",
        "        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])",
    )
)

cells.append(
    md(
        "### Step 0d.4 — Instantiate `llm` and `chat_llm`",
        "",
        "| Variable | Used in |",
        "|----------|---------|",
        "| `llm` | `GraphCypherQAChain`, ReAct agent |",
        "| `chat_llm` | RAG and GraphRAG answer chains |",
        "",
        "For OpenAI we use one `ChatOpenAI` for both. For Ollama we split LLM vs Chat wrappers as above.",
    )
)

cells.append(
    code(
        "# Step 0d.4 — Select backend",
        "if LLM_BACKEND == 'openai':",
        "    if not os.getenv('OPENAI_API_KEY'):",
        "        raise ValueError('OPENAI_API_KEY required when LLM_BACKEND=openai')",
        "    from langchain_openai import ChatOpenAI",
        "    chat_llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)",
        "    llm = chat_llm",
        "    print(f'Using OpenAI: {OPENAI_MODEL}')",
        "elif LLM_BACKEND == 'ollama':",
        "    llm = OllamaRunnerLLM()",
        "    chat_llm = OllamaRunnerChatModel()",
        "    print(f'Using Ollama runner: {OLLAMA_MODEL} @ {OLLAMA_HOST}')",
        "    print('Ensure Ollama is running: ollama serve')",
        "else:",
        "    raise ValueError(\"Set LLM_BACKEND to 'ollama' or 'openai'\")",
    )
)

cells.append(
    md(
        "### Step 0e — Smoke test `ollama_model_runner.py`",
        "",
        "Quick check that the runner, model name, and Ollama service work together.",
        "Terminal equivalent (from `Module_8/`):",
        "",
        "```bash",
        "python ollama_model_runner.py --host http://localhost:11434 \\",
        "  --models llama3.2:3b --prompt \"Reply with exactly: Ollama OK\" --max-tokens 32",
        "```",
    )
)

cells.append(
    code(
        "# Step 0e — Runner smoke test",
        "if LLM_BACKEND == 'ollama':",
        "    smoke = call_ollama_runner('Reply with exactly: Ollama OK', model=OLLAMA_MODEL)",
        "    print('Ollama runner smoke test:', smoke[:120])",
        "    if 'ok' not in smoke.lower():",
        "        print('Warning: unexpected reply — verify model and OLLAMA_HOST')",
        "    print('LLM ready for later sections.')",
        "else:",
        "    print('Skipped — OpenAI backend')",
    )
)

cells.append(
    md(
        "**Expected output (Ollama):** A line containing `Ollama OK` (or similar) and `LLM ready for later sections.`",
        "",
        "If this fails, fix Ollama **before** Section 3.3 — text-to-Cypher is the most LLM-sensitive step.",
    )
)

# =============================================================================
# 3.1 Neo4j and LangChain
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# 3.1 Neo4j and LangChain",
        "",
        "### Big picture",
        "",
        "```text",
        "Your app (LangChain)",
        "    │",
        "    ├── Neo4jGraph      → Cypher, schema, seed data",
        "    ├── Neo4jVector     → embeddings + similarity search",
        "    ├── GraphCypherQAChain → natural language → Cypher → answer",
        "    └── Agent + tools   → chooses when to query the graph",
        "            │",
        "            ▼",
        "      Neo4j Database (Bolt)",
        "```",
        "",
        "The official package is **`langchain-neo4j`** (`import langchain_neo4j`).",
        "Older tutorials may import from `langchain_community` — prefer `langchain_neo4j` for new projects.",
    )
)

cells.append(
    md(
        "## 3.1.1 Neo4j integration — `Neo4jGraph`",
        "",
        "`Neo4jGraph` wraps the Neo4j Python driver with LangChain conventions:",
        "",
        "- **`query(cypher, params)`** — run Cypher and get Python dict rows.",
        "- **`schema`** — text description of labels, relationships, properties (after `refresh_schema()`).",
        "- Shared **URL / credentials** with vector and QA components.",
        "",
        "In production you often use one graph object per request or a connection pool;",
        "for teaching we use a single global `neo4j_graph` in the notebook.",
    )
)

cells.append(
    code(
        "# 3.1.1 — Create Neo4jGraph",
        "from langchain_neo4j import Neo4jGraph",
        "",
        "neo4j_graph = Neo4jGraph(",
        "    url=NEO4J_URI,",
        "    username=NEO4J_USERNAME,",
        "    password=NEO4J_PASSWORD,",
        "    database=NEO4J_DATABASE,",
        ")",
        "print('Neo4jGraph connected.')",
    )
)

cells.append(
    md(
        "**Expected output:** `Neo4jGraph connected.`",
        "",
        "No data is created yet — we only open a LangChain-managed connection.",
    )
)

cells.append(
    md(
        "### 3.1.1b — First query through LangChain",
        "",
        "Same as `RETURN` in Browser, but results arrive as a **list of dictionaries** in Python.",
        "Downstream chains consume this format when executing generated Cypher.",
    )
)

cells.append(
    code(
        "# 3.1.1b — Query through LangChain wrapper",
        "rows = neo4j_graph.query('RETURN \"LangChain + Neo4j OK\" AS message')",
        "print(rows)",
    )
)

cells.append(
    md(
        "## 3.1.2 Schema introspection with `refresh_schema()`",
        "",
        "Text-to-Cypher (Section 3.3) sends **schema text** to the LLM so it knows which labels exist.",
        "",
        "- **`refresh_schema()`** queries the database catalog and builds a summary string.",
        "- The result is stored in **`neo4j_graph.schema`**.",
        "- After you **seed** or **change** data, call `refresh_schema()` again.",
        "",
        "Better schema in Neo4j (consistent labels, documented properties) → better generated Cypher.",
    )
)

cells.append(
    code(
        "# 3.1.2 — Refresh and preview schema (truncated)",
        "neo4j_graph.refresh_schema()",
        "schema_preview = (neo4j_graph.schema or '')[:1200]",
        "print(schema_preview)",
        "if len(neo4j_graph.schema or '') > 1200:",
        "    print('... [truncated for display]')",
    )
)

cells.append(
    md(
        "If the database is empty, schema output may be minimal until Section 3.1.3.",
    )
)

cells.append(
    md(
        "## 3.1.3 Seed the LangChain lab graph",
        "",
        "We build a **toy maritime knowledge graph** plus **text chunks** for vector search.",
        "All lab nodes include the label **`LangChainLab`** so you can delete or filter them safely.",
        "",
        "### Data model (this lab)",
        "",
        "```text",
        "(Document)-[:HAS_CHUNK]->(Chunk)-[:MENTIONS]->(Port|Organization|Canal|...)",
        "   (Port)-[:LOCATED_IN]->(Country)",
        "   (Organization)-[:OPERATES_IN]->(Port)",
        "   (Organization)-[:USES_ROUTE]->(Canal)",
        "```",
        "",
        "| Node label | Role |",
        "|------------|------|",
        "| `Port`, `Organization`, `Canal`, `Country` | Structured entities for Cypher QA |",
        "| `Document`, `Chunk` | Unstructured text + embeddings for RAG |",
        "| `LangChainLab` | Marker label on all course nodes |",
    )
)

cells.append(
    md(
        "### 3.1.3a — Clear previous lab data",
        "",
        "Re-running the notebook should not duplicate nodes. We delete every node with `LangChainLab`",
        "before inserting fresh data. **Other graphs in the same database are not touched.**",
    )
)

cells.append(
    code(
        "# 3.1.3a — Clear previous lab data (safe to re-run)",
        "neo4j_graph.query(",
        "    '''",
        "    MATCH (n:LangChainLab)",
        "    DETACH DELETE n",
        "    '''",
        ")",
        "print('Cleared prior LangChainLab subgraph.')",
    )
)

cells.append(
    md(
        "### 3.1.3b — Structured entities",
        "",
        "This Cypher **CREATE**s ports, Maersk, Panama Canal, countries, and relationships.",
        "Property `id` gives stable identifiers for queries and for `MENTIONS` links later.",
    )
)

cells.append(
    code(
        "# 3.1.3b — Seed structured maritime entities",
        "neo4j_graph.query(",
        "    '''",
        "    CREATE (lab:LangChainLab {course: 'Using Knowledge Graph with LangChain', module: 'Module_8'})",
        "    CREATE (p1:Port:LangChainLab {id: 'Port_of_Rotterdam', name: 'Port of Rotterdam', country: 'Netherlands'})",
        "    CREATE (p2:Port:LangChainLab {id: 'Port_of_Singapore', name: 'Port of Singapore', country: 'Singapore'})",
        "    CREATE (o:Organization:LangChainLab {id: 'Maersk', name: 'Maersk', country: 'Denmark'})",
        "    CREATE (c:Canal:LangChainLab {id: 'Panama_Canal', name: 'Panama Canal', country: 'Panama'})",
        "    CREATE (n1:Country:LangChainLab {id: 'Netherlands', name: 'Netherlands'})",
        "    CREATE (n2:Country:LangChainLab {id: 'Singapore', name: 'Singapore'})",
        "    CREATE (p1)-[:LOCATED_IN]->(n1)",
        "    CREATE (p2)-[:LOCATED_IN]->(n2)",
        "    CREATE (o)-[:OPERATES_IN]->(p1)",
        "    CREATE (o)-[:USES_ROUTE]->(c)",
        "    '''",
        ")",
        "print('Structured graph seeded.')",
    )
)

cells.append(
    md(
        "**Verify in Neo4j Browser:**",
        "",
        "```cypher",
        "MATCH (o:Organization:LangChainLab)-[r]->(x)",
        "RETURN o.id, type(r), x.id;",
        "```",
    )
)

cells.append(
    md(
        "### 3.1.3c — Document chunks",
        "",
        "RAG needs **short passages** stored as nodes. Each chunk has:",
        "",
        "- `text` — embedded and searched in Section 3.2.",
        "- `source` — provenance (`course_seed` here).",
        "- `id` — links to vector metadata and GraphRAG expansion.",
    )
)

cells.append(
    code(
        "# 3.1.3c — Seed document chunks (text for vector index)",
        "chunks = [",
        "    {",
        "        'id': 'chunk_rotterdam',",
        "        'text': 'The Port of Rotterdam is the largest port in Europe and a major hub for container shipping.',",
        "        'source': 'course_seed',",
        "    },",
        "    {",
        "        'id': 'chunk_maersk',",
        "        'text': 'Maersk is a Danish shipping company that operates vessels and uses routes such as the Panama Canal.',",
        "        'source': 'course_seed',",
        "    },",
        "    {",
        "        'id': 'chunk_panama',",
        "        'text': 'The Panama Canal connects the Atlantic and Pacific oceans and shortens voyages for many carriers.',",
        "        'source': 'course_seed',",
        "    },",
        "    {",
        "        'id': 'chunk_singapore',",
        "        'text': 'The Port of Singapore is a leading transshipment hub in Southeast Asia.',",
        "        'source': 'course_seed',",
        "    },",
        "]",
        "for ch in chunks:",
        "    neo4j_graph.query(",
        "        '''",
        "        MERGE (d:Document:LangChainLab {id: $doc_id})",
        "        SET d.title = 'LangChain lab corpus'",
        "        MERGE (c:Chunk:LangChainLab {id: $chunk_id})",
        "        SET c.text = $text, c.source = $source",
        "        MERGE (d)-[:HAS_CHUNK]->(c)",
        "        ''',",
        "        params={'doc_id': 'langchain_lab_doc', 'chunk_id': ch['id'], 'text': ch['text'], 'source': ch['source']},",
        "    )",
        "print(f'Seeded {len(chunks)} chunks.')",
    )
)

cells.append(
    md(
        "### 3.1.3d — Link chunks to entities (GraphRAG bridge)",
        "",
        "`(Chunk)-[:MENTIONS]->(Entity)` connects **unstructured** text to **structured** graph nodes.",
        "Section 3.2.3 traverses these edges after vector search to enrich the LLM context.",
    )
)

cells.append(
    code(
        "# 3.1.3d — Link chunks to entities (for GraphRAG expansion)",
        "links = [",
        "    ('chunk_rotterdam', 'Port_of_Rotterdam'),",
        "    ('chunk_maersk', 'Maersk'),",
        "    ('chunk_panama', 'Panama_Canal'),",
        "    ('chunk_singapore', 'Port_of_Singapore'),",
        "]",
        "for chunk_id, entity_id in links:",
        "    neo4j_graph.query(",
        "        '''",
        "        MATCH (c:Chunk:LangChainLab {id: $chunk_id})",
        "        MATCH (e:LangChainLab {id: $entity_id})",
        "        MERGE (c)-[:MENTIONS]->(e)",
        "        ''',",
        "        params={'chunk_id': chunk_id, 'entity_id': entity_id},",
        "    )",
        "neo4j_graph.refresh_schema()",
        "print('Chunk–entity links created; schema refreshed.')",
    )
)

cells.append(
    md(
        "**Checkpoint:** You should now see `Port`, `Chunk`, `MENTIONS`, etc. in `neo4j_graph.schema`.",
    )
)

cells.append(
    md(
        "## 3.1.4 Simple LangChain agent",
        "",
        "An **agent** loops: think → pick a **tool** → observe result → repeat until done.",
        "",
        "We register two tools:",
        "",
        "| Tool | When to use |",
        "|------|-------------|",
        "| `run_read_cypher` | User gives Cypher or wants raw rows |",
        "| `ask_graph_in_natural_language` | Open-ended question → `GraphCypherQAChain` (Section 3.3) |",
        "",
        "> **Order note:** The natural-language tool needs `CYPHER_QA_CHAIN` from Section 3.3.",
        "> You can define the agent here, but run the demo cell **after** 3.3.",
        "",
        "> **Production:** Use read-only DB roles, query allow-lists, and human review for generated Cypher.",
    )
)

cells.append(
    md(
        "### 3.1.4a — Define tools",
        "",
        "`@tool` turns a Python function into a LangChain tool with name, docstring, and schema.",
        "The agent reads docstrings to decide which tool to call.",
    )
)

cells.append(
    code(
        "# 3.1.4a — Define tools (Cypher QA chain wired in 3.3; placeholder first)",
        "from langchain_core.tools import tool",
        "",
        "CYPHER_QA_CHAIN = None  # set in Section 3.3",
        "",
        "",
        "@tool",
        "def run_read_cypher(cypher: str) -> str:",
        "    \"\"\"Execute a read-only Cypher query on the LangChain lab graph.\"\"\"",
        "    forbidden = ('create ', 'merge ', 'delete ', 'detach ', 'set ', 'remove ')",
        "    if any(word in cypher.lower() for word in forbidden):",
        "        return 'Error: only read-only queries (MATCH/RETURN) are allowed in this lab tool.'",
        "    try:",
        "        return str(neo4j_graph.query(cypher))",
        "    except Exception as exc:",
        "        return f'Cypher error: {exc}'",
        "",
        "",
        "@tool",
        "def ask_graph_in_natural_language(question: str) -> str:",
        "    \"\"\"Answer a question about the Neo4j graph using natural language (text-to-Cypher).\"\"\"",
        "    if CYPHER_QA_CHAIN is None:",
        "        return 'GraphCypherQAChain not initialized yet — run Section 3.3 first, then re-run agent cells.'",
        "    out = CYPHER_QA_CHAIN.invoke({'query': question})",
        "    return out.get('result', str(out))",
        "",
        "agent_tools = [run_read_cypher, ask_graph_in_natural_language]",
        "print('Tools:', [t.name for t in agent_tools])",
    )
)

cells.append(
    md(
        "### 3.1.4b — ReAct agent",
        "",
        "**ReAct** (Reason + Act) prompts the model in plain text:",
        "`Thought` → `Action` → `Action Input` → `Observation` → … → `Final Answer`.",
        "",
        "We use `create_react_agent` instead of native **tool-calling** so the lab works with",
        "`ollama_model_runner.py` (which returns free text, not structured tool JSON).",
        "",
        "| Parameter | Value | Why |",
        "|-----------|-------|-----|",
        "| `max_iterations` | 5 | Prevents infinite tool loops |",
        "| `handle_parsing_errors` | True | Small models may mis-format actions |",
        "| `verbose` | True | Shows reasoning in notebook output |",
    )
)

cells.append(
    code(
        "# 3.1.4b — Build ReAct agent",
        "from langchain_classic.agents import AgentExecutor, create_react_agent",
        "from langchain_core.prompts import PromptTemplate",
        "",
        "react_template = '''Answer using the Neo4j lab tools.",
        "",
        "Tools:",
        "{tools}",
        "",
        "Use this format:",
        "Question: the question",
        "Thought: reasoning",
        "Action: one of [{tool_names}]",
        "Action Input: tool input",
        "Observation: tool output",
        "... repeat as needed ...",
        "Thought: I know the final answer",
        "Final Answer: answer for the user",
        "",
        "Question: {input}",
        "Thought:{agent_scratchpad}'''",
        "",
        "react_prompt = PromptTemplate.from_template(react_template)",
        "react_agent = create_react_agent(llm, agent_tools, react_prompt)",
        "agent_executor = AgentExecutor(",
        "    agent=react_agent, tools=agent_tools, verbose=True, max_iterations=5, handle_parsing_errors=True",
        ")",
        "print('ReAct agent ready (run Section 3.3 before natural-language tool works).')",
    )
)

cells.append(
    md(
        "### 3.1.4c — Try the agent (preview)",
        "",
        "This cell **skips** until `CYPHER_QA_CHAIN` exists. After Section 3.3, re-run **3.3.4b** for a full demo.",
    )
)

cells.append(
    code(
        "# 3.1.4c — Example agent question (preview)",
        "if CYPHER_QA_CHAIN is not None:",
        "    response = agent_executor.invoke({",
        "        'input': 'Which organization operates in the Port of Rotterdam?'",
        "    })",
        "    print(response.get('output', response))",
        "else:",
        "    print('Skip until CYPHER_QA_CHAIN is defined in Section 3.3 (then run cell 3.3.4b).')",
    )
)

# =============================================================================
# 3.2 Vectors
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# 3.2 Vectors",
        "",
        "### Why vectors in a graph course?",
        "",
        "Many GenAI apps combine:",
        "",
        "- **Vector search** — find relevant *text* by semantic similarity.",
        "- **Graph traversal** — find related *entities* and *facts* by relationships.",
        "",
        "Neo4j 5.x can store embeddings on nodes and query them with a **vector index**.",
        "`Neo4jVector` in `langchain-neo4j` creates the index and exposes LangChain retriever APIs.",
        "",
        "```text",
        "User question",
        "    → embed question",
        "    → vector index (top-k Chunk nodes)",
        "    → optional graph expansion (MENTIONS, OPERATES_IN, ...)",
        "    → LLM answer",
        "```",
    )
)

cells.append(
    md(
        "## 3.2.1 Vector search with `Neo4jVector`",
        "",
        "### Embedding model",
        "",
        "We use **`sentence-transformers/all-MiniLM-L6-v2`** (384 dimensions) via Hugging Face.",
        "",
        "- **Pros:** No API key; runs locally.",
        "- **Cons:** First run downloads model weights (**internet required** once).",
        "",
        "Alternatives for production: OpenAI `text-embedding-3-small`, Cohere, etc.",
    )
)

cells.append(
    code(
        "# 3.2.1a — Embedding model",
        "from langchain_community.embeddings import HuggingFaceEmbeddings",
        "",
        "embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')",
        "sample_vec = embeddings.embed_query('maritime port')",
        "print('Embedding dimension:', len(sample_vec))",
    )
)

cells.append(
    md(
        "**Expected output:** `Embedding dimension: 384`",
        "",
        "If download fails, check network/firewall or pre-download the model with `huggingface-cli`.",
    )
)

cells.append(
    md(
        "### 3.2.1b — Load chunks as LangChain `Document` objects",
        "",
        "We read `Chunk` nodes from Neo4j and map them to `Document(page_content=..., metadata=...)`.",
        "Metadata `chunk_id` is required later for GraphRAG expansion.",
    )
)

cells.append(
    code(
        "# 3.2.1b — Load chunk texts from Neo4j",
        "from langchain_core.documents import Document",
        "",
        "chunk_rows = neo4j_graph.query(",
        "    '''",
        "    MATCH (c:Chunk:LangChainLab)",
        "    RETURN c.id AS id, c.text AS text, c.source AS source",
        "    ORDER BY c.id",
        "    '''",
        ")",
        "documents = [",
        "    Document(page_content=row['text'], metadata={'chunk_id': row['id'], 'source': row.get('source')})",
        "    for row in chunk_rows",
        "]",
        "print('Documents for indexing:', len(documents))",
        "for d in documents[:2]:",
        "    print('-', d.metadata['chunk_id'], ':', d.page_content[:60], '...')",
    )
)

cells.append(
    md(
        "### 3.2.1c — Create vector index with `Neo4jVector.from_documents`",
        "",
        "| Parameter | This lab |",
        "|-----------|----------|",
        "| `index_name` | `langchain_lab_chunk_index` |",
        "| `node_label` | `Chunk` |",
        "| `text_node_property` | `text` |",
        "| `embedding_node_property` | `embedding` |",
        "",
        "The helper **embeds** each document, **writes** vectors to matching nodes, and **creates** the index if missing.",
        "We clear old `embedding` properties first so re-runs stay idempotent.",
    )
)

cells.append(
    code(
        "# 3.2.1c — Create Neo4j vector index from documents",
        "from langchain_neo4j import Neo4jVector",
        "",
        "VECTOR_INDEX_NAME = 'langchain_lab_chunk_index'",
        "VECTOR_NODE_LABEL = 'Chunk'",
        "VECTOR_TEXT_PROPERTY = 'text'",
        "VECTOR_EMBEDDING_PROPERTY = 'embedding'",
        "",
        "neo4j_graph.query('MATCH (c:Chunk:LangChainLab) REMOVE c.embedding')",
        "",
        "vector_store = Neo4jVector.from_documents(",
        "    documents,",
        "    embeddings,",
        "    url=NEO4J_URI,",
        "    username=NEO4J_USERNAME,",
        "    password=NEO4J_PASSWORD,",
        "    database=NEO4J_DATABASE,",
        "    index_name=VECTOR_INDEX_NAME,",
        "    node_label=VECTOR_NODE_LABEL,",
        "    text_node_property=VECTOR_TEXT_PROPERTY,",
        "    embedding_node_property=VECTOR_EMBEDDING_PROPERTY,",
        ")",
        "print('Neo4jVector index ready:', VECTOR_INDEX_NAME)",
    )
)

cells.append(
    md(
        "### 3.2.1d — Similarity search",
        "",
        "`similarity_search(query, k=2)` embeds the query string and returns the top-k nearest chunks.",
        "Compare results to the Rotterdam / Europe question — the Rotterdam chunk should rank high.",
    )
)

cells.append(
    code(
        "# 3.2.1d — Similarity search",
        "query = 'Which port is the largest in Europe?'",
        "hits = vector_store.similarity_search(query, k=2)",
        "print('Query:', query)",
        "for i, doc in enumerate(hits, 1):",
        "    print(f'{i}. {doc.metadata} -> {doc.page_content[:80]}...')",
    )
)

cells.append(
    md(
        "## 3.2.2 Vector retriever (RAG)",
        "",
        "### What is a retriever?",
        "",
        "In LangChain, a **retriever** implements `invoke(query) → list[Document]`.",
        "Chains treat retrievers as black boxes — swap Neo4j for Chroma, Pinecone, etc. without rewriting the LLM step.",
        "",
        "### Minimal RAG pipeline",
        "",
        "1. **Retrieve** documents similar to the user question.",
        "2. **Format** them into one context string.",
        "3. **Prompt** the LLM with context + question.",
        "4. **Parse** the model output as the final answer.",
    )
)

cells.append(
    md(
        "### 3.2.2a — `as_retriever()`",
        "",
        "`search_kwargs={'k': 3}` returns three chunks per query. Increase `k` for broader context",
        "(more tokens, higher cost/latency).",
    )
)

cells.append(
    code(
        "# 3.2.2a — Create vector retriever",
        "vector_retriever = vector_store.as_retriever(search_kwargs={'k': 3})",
        "retrieved = vector_retriever.invoke('Panama Canal shipping route')",
        "print('Retrieved', len(retrieved), 'chunks')",
        "for doc in retrieved:",
        "    print('-', doc.page_content[:70])",
    )
)

cells.append(
    md(
        "### 3.2.2b — LCEL RAG chain",
        "",
        "We use **LangChain Expression Language** (`|` pipe):",
        "",
        "```text",
        "{context: retriever | format_docs, question: input} → prompt → chat_llm → parser",
        "```",
        "",
        "The system message tells the model to **stay grounded** in retrieved text.",
    )
)

cells.append(
    code(
        "# 3.2.2b — Minimal RAG chain (retrieve + LLM)",
        "from langchain_core.prompts import ChatPromptTemplate",
        "from langchain_core.output_parsers import StrOutputParser",
        "from langchain_core.runnables import RunnablePassthrough",
        "",
        "def format_docs(docs):",
        "    return '\\n\\n'.join(f'- {d.page_content}' for d in docs)",
        "",
        "rag_prompt = ChatPromptTemplate.from_messages([",
        "    ('system', 'Answer using only the context below. If unsure, say you do not know.'),",
        "    ('human', 'Context:\\n{context}\\n\\nQuestion: {question}'),",
        "])",
        "",
        "rag_chain = (",
        "    {'context': vector_retriever | format_docs, 'question': RunnablePassthrough()}",
        "    | rag_prompt",
        "    | chat_llm",
        "    | StrOutputParser()",
        ")",
        "",
        "rag_answer = rag_chain.invoke('What does Maersk use for routes?')",
        "print(rag_answer)",
    )
)

cells.append(
    md(
        "**Tip:** If the answer ignores context, lower temperature, increase `k`, or use a larger Ollama model (`llama3.1:8b`).",
    )
)

cells.append(
    md(
        "## 3.2.3 Graph retrieval (GraphRAG)",
        "",
        "### Limitation of vector-only RAG",
        "",
        "Similarity search may return **correct text** but miss **explicit edges**",
        "(e.g. `Maersk -[:USES_ROUTE]-> Panama_Canal`) unless that fact appears verbatim in the chunk.",
        "",
        "### GraphRAG pattern (this lab)",
        "",
        "1. Vector-retrieve top-k `Chunk` nodes.",
        "2. Read `chunk_id` metadata from each `Document`.",
        "3. Run Cypher: `Chunk -[:MENTIONS]-> Entity` and one hop of entity relationships.",
        "4. Pass **chunk text + graph facts** to the LLM.",
    )
)

cells.append(
    md(
        "### 3.2.3a — `graph_context_for_chunks()` and `graphrag_retrieve()`",
        "",
        "These functions are **teaching helpers** — in production you might use `neo4j-graphrag`",
        "or a packaged retriever from Neo4j Labs.",
    )
)

cells.append(
    code(
        "# 3.2.3a — Graph expansion from retrieved chunk IDs",
        "def graph_context_for_chunks(chunk_ids: list[str]) -> str:",
        "    rows = neo4j_graph.query(",
        "        '''",
        "        UNWIND $ids AS chunk_id",
        "        MATCH (c:Chunk:LangChainLab {id: chunk_id})-[:MENTIONS]->(e:LangChainLab)",
        "        OPTIONAL MATCH (e)-[r]-(n:LangChainLab)",
        "        WHERE type(r) IN ['LOCATED_IN', 'OPERATES_IN', 'USES_ROUTE']",
        "        RETURN DISTINCT c.id AS chunk, e.id AS entity, type(r) AS rel, n.id AS related",
        "        LIMIT 30",
        "        '''",
        "        , params={'ids': chunk_ids},",
        "    )",
        "    lines = []",
        "    for row in rows:",
        "        lines.append(",
        "            f\"Chunk {row.get('chunk')} mentions {row.get('entity')}; \"",
        "            f\"{row.get('rel')} -> {row.get('related')}\"",
        "        )",
        "    return '\\n'.join(lines) if lines else '(no graph context)'",
        "",
        "",
        "def graphrag_retrieve(question: str, k: int = 2) -> dict:",
        "    docs = vector_retriever.invoke(question)[:k]",
        "    chunk_ids = [d.metadata.get('chunk_id') for d in docs if d.metadata.get('chunk_id')]",
        "    return {",
        "        'chunks': docs,",
        "        'graph_context': graph_context_for_chunks(chunk_ids),",
        "    }",
        "",
        "sample = graphrag_retrieve('Rotterdam Europe port')",
        "print('Graph context preview:\\n', sample['graph_context'][:500])",
    )
)

cells.append(
    md(
        "### 3.2.3b — GraphRAG answer chain",
        "",
        "Same LCEL pattern as RAG, but the human message includes a **`graph`** block with relationship lines.",
    )
)

cells.append(
    code(
        "# 3.2.3b — GraphRAG answer chain",
        "graphrag_prompt = ChatPromptTemplate.from_messages([",
        "    ('system',",
        "     'You answer using chunk text and graph facts. Cite relationships when relevant.'),",
        "    ('human',",
        "     'Chunks:\\n{chunks}\\n\\nGraph facts:\\n{graph}\\n\\nQuestion: {question}'),",
        "])",
        "",
        "def run_graphrag(question: str) -> str:",
        "    pack = graphrag_retrieve(question)",
        "    chunks_txt = format_docs(pack['chunks'])",
        "    chain = graphrag_prompt | chat_llm | StrOutputParser()",
        "    return chain.invoke({'chunks': chunks_txt, 'graph': pack['graph_context'], 'question': question})",
        "",
        "print(run_graphrag('How is Maersk connected to the Panama Canal?'))",
    )
)

cells.append(
    md(
        "**Compare:** Run the same question through **3.2.2b** (vector-only RAG) vs this cell.",
        "GraphRAG should surface the `USES_ROUTE` path even when wording differs.",
    )
)

cells.append(
    md(
        "## 3.2.4 Additional data (optional)",
        "",
        "To scale beyond four seed chunks:",
        "",
        "1. Parse **`data/dbpedia_maritime_corpus.txt`** (or `dbpedia_course_corpus.txt`).",
        "2. `MERGE` new `Chunk` nodes and optional `MENTIONS` edges.",
        "3. `Neo4jVector.add_documents()` or rebuild the index.",
        "",
        "See **`data/DATASETS.md`** for licenses and rebuild scripts.",
        "",
        "The cell below only **previews** two articles — it does not rebuild the index.",
    )
)

cells.append(
    code(
        "# 3.2.4 — Optional: load sample articles from maritime corpus",
        "import re",
        "",
        "def load_corpus_articles(path: Path, max_articles: int = 2):",
        "    text = path.read_text(encoding='utf-8')",
        "    blocks = re.split(r'\\n\\[(\\d+)\\]\\s+', text)",
        "    articles = []",
        "    it = iter(blocks)",
        "    _ = next(it, None)",
        "    for num, body in zip(it, it):",
        "        title_line, _, abstract = body.partition('\\n')",
        "        articles.append({'n': num, 'title': title_line.strip(), 'text': abstract.strip()[:800]})",
        "        if len(articles) >= max_articles:",
        "            break",
        "    return articles",
        "",
        "if CORPUS_PATH.is_file():",
        "    extra = load_corpus_articles(CORPUS_PATH, max_articles=2)",
        "    print('Optional corpus sample:', [a['title'] for a in extra])",
        "else:",
        "    print('Optional corpus not found:', CORPUS_PATH)",
    )
)

# =============================================================================
# 3.3 Text to Cypher
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# 3.3 Text to Cypher",
        "",
        "### How `GraphCypherQAChain` works",
        "",
        "```text",
        "User question",
        "    → LLM + graph.schema → Cypher query",
        "    → Execute on Neo4j → result rows",
        "    → LLM + rows + question → natural language answer",
        "```",
        "",
        "This is **not** magic — quality depends on schema clarity, model size, and question phrasing.",
        "Enable `return_intermediate_steps=True` to debug generated Cypher in the notebook.",
    )
)

cells.append(
    md(
        "## 3.3.1 Schema for Cypher generation",
        "",
        "Before building the chain, we:",
        "",
        "1. **`refresh_schema()`** — update `neo4j_graph.schema` for the LLM.",
        "2. **Count nodes** by label — confirm `LangChainLab` data is present.",
        "",
        "If counts are zero, re-run Section **3.1.3**.",
    )
)

cells.append(
    code(
        "# 3.3.1 — Refresh schema and inspect labels used by the lab",
        "neo4j_graph.refresh_schema()",
        "label_rows = neo4j_graph.query(",
        "    '''",
        "    MATCH (n:LangChainLab)",
        "    RETURN DISTINCT labels(n) AS labels, count(*) AS cnt",
        "    ORDER BY cnt DESC",
        "    '''",
        ")",
        "print('LangChainLab nodes by label combination:')",
        "for row in label_rows:",
        "    print(row)",
    )
)

cells.append(
    md(
        "## 3.3.2 Cypher QA chain",
        "",
        "### `allow_dangerous_requests=True`",
        "",
        "Generated Cypher could theoretically **write** data. Neo4j's integration requires you to",
        "opt in explicitly. This course uses a **disposable lab graph** only.",
        "",
        "### Input / output",
        "",
        "| Key | Content |",
        "|-----|---------|",
        "| Input `query` | User question in English |",
        "| Output `result` | Final natural language answer |",
        "| Output `intermediate_steps` | Generated Cypher and DB records (when enabled) |",
    )
)

cells.append(
    code(
        "# 3.3.2 — GraphCypherQAChain",
        "from langchain_neo4j import GraphCypherQAChain",
        "",
        "neo4j_graph.refresh_schema()",
        "CYPHER_QA_CHAIN = GraphCypherQAChain.from_llm(",
        "    llm=llm,",
        "    graph=neo4j_graph,",
        "    verbose=True,",
        "    allow_dangerous_requests=True,",
        "    return_intermediate_steps=True,",
        ")",
        "print('GraphCypherQAChain ready.')",
    )
)

cells.append(
    md(
        "### 3.3.2b — Example question",
        "",
        "Watch **verbose** output: you should see a `MATCH` on `Port` / `Country` labels.",
        "If Cypher fails, compare the query to the graph in Browser and adjust seed data or model.",
    )
)

cells.append(
    code(
        "# 3.3.2b — Ask a natural language question",
        "qa_result = CYPHER_QA_CHAIN.invoke({'query': 'Which ports are located in the Netherlands or Singapore?'})",
        "print('Answer:', qa_result.get('result'))",
        "print('Intermediate steps:', qa_result.get('intermediate_steps'))",
    )
)

cells.append(
    md(
        "## 3.3.3 Customize Cypher generation",
        "",
        "Advanced options on `GraphCypherQAChain.from_llm`:",
        "",
        "| Option | Effect |",
        "|--------|--------|",
        "| `cypher_llm` / `qa_llm` | Different models for query vs answer |",
        "| `cypher_prompt` / `qa_prompt` | Override default prompts |",
        "| `include_types` | Limit schema to listed node/rel types |",
        "| `exclude_types` | Omit noisy labels from schema |",
        "| `validate_cypher` | Extra validation step (package version dependent) |",
        "",
        "Below we restrict to maritime-related types so the LLM ignores unrelated labels in the DB.",
    )
)

cells.append(
    code(
        "# 3.3.3 — Chain with include_types filter (maritime entities only)",
        "filtered_chain = GraphCypherQAChain.from_llm(",
        "    llm=llm,",
        "    graph=neo4j_graph,",
        "    include_types=['Port', 'Organization', 'Canal', 'Country', 'Chunk'],",
        "    verbose=False,",
        "    allow_dangerous_requests=True,",
        ")",
        "filtered_answer = filtered_chain.invoke({'query': 'What route does Maersk use?'})",
        "print(filtered_answer.get('result', filtered_answer))",
    )
)

cells.append(
    md(
        "## 3.3.4 Text-to-Cypher as a retriever",
        "",
        "Some architectures treat **graph QA as retrieval**:",
        "",
        "- Downstream RAG merges **vector chunks** + **Cypher result text**.",
        "- Agents call a retriever instead of a full QA chain when they only need **context**.",
        "",
        "We subclass `BaseRetriever` and return one `Document` whose `page_content` is the chain answer",
        "(metadata stores a truncated `intermediate_steps` string for debugging).",
    )
)

cells.append(
    code(
        "# 3.3.4a — Cypher retriever wrapper",
        "from langchain_core.retrievers import BaseRetriever",
        "from langchain_core.callbacks import CallbackManagerForRetrieverRun",
        "from langchain_core.documents import Document",
        "from pydantic import ConfigDict, Field",
        "",
        "",
        "class CypherContextRetriever(BaseRetriever):",
        "    \"\"\"Returns graph QA output as Documents for downstream RAG.\"\"\"",
        "    model_config = ConfigDict(arbitrary_types_allowed=True)",
        "    chain: GraphCypherQAChain = Field(...)",
        "",
        "    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun):",
        "        out = self.chain.invoke({'query': query})",
        "        steps = out.get('intermediate_steps') or []",
        "        context = out.get('result', '')",
        "        meta = {'intermediate_steps': str(steps)[:2000]}",
        "        return [Document(page_content=str(context), metadata=meta)]",
        "",
        "",
        "cypher_retriever = CypherContextRetriever(chain=CYPHER_QA_CHAIN)",
        "cypher_docs = cypher_retriever.invoke('Which organization operates in Rotterdam?')",
        "print(cypher_docs[0].page_content[:400])",
    )
)

cells.append(
    md(
        "### 3.3.4b — Re-run the agent with a live `CYPHER_QA_CHAIN`",
        "",
        "Now `ask_graph_in_natural_language` can call the QA chain. Expect verbose ReAct steps",
        "and a final answer mentioning **Maersk** and **Rotterdam**.",
        "",
        "**Note:** This may take 30–90 seconds on local Ollama — normal for multi-step LLM calls.",
    )
)

cells.append(
    code(
        "# 3.3.4b — Re-run agent now that CYPHER_QA_CHAIN exists",
        "response = agent_executor.invoke({",
        "    'input': 'Which organization operates in the Port of Rotterdam?'",
        "})",
        "print(response.get('output', response))",
    )
)

cells.append(
    md(
        "---",
        "",
        "## Summary",
        "",
        "| Topic | Key API | What you practiced |",
        "|-------|---------|-------------------|",
        "| Neo4j + LangChain | `Neo4jGraph` | Connect, query, refresh schema |",
        "| Lab data | Cypher `CREATE` / `MERGE` | Maritime graph + chunks + `MENTIONS` |",
        "| Vector RAG | `Neo4jVector`, `as_retriever()` | Embed, index, retrieve, answer |",
        "| GraphRAG | Custom expansion + LCEL | Vectors + relationship context |",
        "| Text to Cypher | `GraphCypherQAChain` | NL → Cypher → NL |",
        "| Agent | `create_react_agent` | Tool choice over graph |",
        "",
        "### Troubleshooting quick reference",
        "",
        "| Symptom | Check |",
        "|---------|-------|",
        "| Neo4j connection error | `NEO4J_SETUP.md`, instance running, `.env` password |",
        "| Ollama runner error | `ollama serve`, `ollama pull`, `LLM_MODEL_SETUP.md` |",
        "| Empty vector results | Re-run 3.1.3c and 3.2.1c |",
        "| Bad / invalid Cypher | `refresh_schema()`, larger model, `include_types` |",
        "| Agent parsing error | Re-run with `verbose=True`; try `llama3.1:8b` |",
        "",
        "### Next steps",
        "",
        "- **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** — build graphs from unstructured text with LLMs.",
        "- Add corpus chunks (Section 3.2.4) and tune `k`, embeddings, and prompts.",
        "- Production hardening: read-only DB user, Cypher validation, observability on `intermediate_steps`.",
        "",
        "### References",
        "",
        "- [LangChain Neo4j integration](https://python.langchain.com/docs/integrations/providers/neo4j/)",
        "- [Neo4j GenAI — LangChain](https://neo4j.com/labs/genai-ecosystem/langchain/)",
        "- [`langchain-neo4j` on PyPI](https://pypi.org/project/langchain-neo4j/)",
    )
)

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.0"},
    },
    "cells": cells,
}

out = Path(__file__).resolve().parents[1] / "Module_8_Using_Knowledge_Graph_with_LangChain.ipynb"
out.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
md_count = sum(1 for c in cells if c["cell_type"] == "markdown")
code_count = sum(1 for c in cells if c["cell_type"] == "code")
print(f"Wrote {out}")
print(f"Total cells: {len(cells)} (markdown: {md_count}, code: {code_count})")
