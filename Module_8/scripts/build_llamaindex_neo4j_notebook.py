#!/usr/bin/env python3
"""Generate Module_8_Using_Knowledge_Graph_with_LlamaIndex.ipynb with rich markdown."""
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
        "# Using Knowledge Graph with LlamaIndex",
        "",
        "**Course module:** Module 8",
        "**Audience:** Beginners with basic graph/Neo4j knowledge, Python, and introductory LlamaIndex experience.",
        "",
        "## Course description",
        "",
        "In this course, you will learn how to integrate **Neo4j** into your **LlamaIndex** applications,",
        "enabling you to leverage graph databases in Generative AI workflows.",
        "",
        "**You will learn how to:**",
        "",
        "- Use **`Neo4jPropertyGraphStore`** and **`Neo4jVectorStore`** to connect LlamaIndex to Neo4j.",
        "- Create **RAG** and **GraphRAG** retrievers.",
        "- Implement and customize a **text-to-Cypher** retriever.",
        "- Create a simple **LlamaIndex agent** that interacts with Neo4j.",
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
        "4. Re-running the notebook is safe: lab data uses the `LlamaIndexLab` label and can be re-seeded.",
    )
)

cells.append(
    md(
        "## Prerequisites",
        "",
        "Before taking this course, you should have:",
        "",
        "- A basic understanding of **graph databases** and **Neo4j** (nodes, relationships, Cypher `MATCH`).",
        "- Knowledge of **Python** and basic familiarity with **LlamaIndex** (indexes, query engines, agents).",
        "- A running Neo4j **5.15+** instance (see `NEO4J_SETUP.md`).",
        "",
        "### Concepts you will use",
        "",
        "| Concept | Meaning in this course |",
        "|---------|------------------------|",
        "| **RAG** | Retrieve relevant text, then ask an LLM with that context |",
        "| **GraphRAG** | RAG plus graph traversal for structured facts |",
        "| **Text-to-Cypher** | LLM writes a Cypher query from natural language |",
        "| **Retriever** | LlamaIndex object that returns `NodeWithScore` items for a query |",
        "| **Agent** | LLM loop that picks tools (Cypher, QA chain) step by step |",
        "",
        "## Course outline",
        "",
        "| Part | Topic |",
        "|------|--------|",
        "| **3.1** | Neo4j and LlamaIndex |",
        "| **3.2** | Vectors |",
        "| **3.3** | Text to Cypher |",
        "",
        "### 3.1 Neo4j and LlamaIndex",
        "",
        "| Section | Topic |",
        "|---------|--------|",
        "| 0 | Development environment & connectivity |",
        "| 3.1.1 | Neo4j integration (`Neo4jPropertyGraphStore`) |",
        "| 3.1.2 | Schema introspection and Cypher helpers |",
        "| 3.1.3 | Seed the LlamaIndex lab graph |",
        "| 3.1.4 | Simple LlamaIndex agent |",
        "",
        "### 3.2 Vectors",
        "",
        "| Section | Topic |",
        "|---------|--------|",
        "| 3.2.1 | Vector search (`Neo4jVectorStore`) |",
        "| 3.2.2 | Vector retriever (RAG) |",
        "| 3.2.3 | Graph retrieval (GraphRAG) |",
        "| 3.2.4 | Additional data (optional) |",
        "",
        "### 3.3 Text to Cypher",
        "",
        "| Section | Topic |",
        "|---------|--------|",
        "| 3.3.1 | Schema introspection |",
        "| 3.3.2 | Cypher generation (`TextToCypherRetriever`) |",
        "| 3.3.3 | Customize the retriever |",
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
        "that **Neo4j** and your **LLM** are reachable before we build LlamaIndex components.",
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
        "| 0d | Wire Ollama runner → LlamaIndex `Settings.llm` |",
        "| 0e | Smoke-test the runner (Ollama only) |",
    )
)

cells.append(
    md(
        "### Step 0a — Install Python packages",
        "",
        "We install the **Neo4j driver**, **LlamaIndex** graph/vector integrations, and **sentence-transformers**",
        "for local embeddings (Section 3.2).",
        "",
        "| Package | Role |",
        "|---------|------|",
        "| `neo4j` | Official database driver (Bolt protocol) |",
        "| `llama-index-core` | Indexes, retrievers, query engines, agents |",
        "| `llama-index-graph-stores-neo4j` | `Neo4jPropertyGraphStore`, `TextToCypherRetriever` |",
        "| `llama-index-vector-stores-neo4jvector` | `Neo4jVectorStore` for vector RAG |",
        "| `llama-index-embeddings-huggingface` | Local `HuggingFaceEmbedding` |",
        "| `llama-index-llms-openai` | OpenAI LLM (optional cloud path) |",
        "| `python-dotenv` | Load `Module_8/.env` without exporting variables manually |",
        "| `sentence-transformers` | Backend for HuggingFace embeddings |",
        "",
        "**Note:** Run this cell once per virtual environment. If versions conflict, restart the kernel after install.",
    )
)

cells.append(
    code(
        "# Step 0a — Install dependencies (run once per environment)",
        "%pip install -q neo4j python-dotenv requests \\",
        "    llama-index-core llama-index-graph-stores-neo4j \\",
        "    llama-index-vector-stores-neo4jvector llama-index-embeddings-huggingface \\",
        "    llama-index-llms-openai sentence-transformers",
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
        "1. **Text-to-Cypher** (`TextToCypherRetriever`) — needs strong instruction-following.",
        "2. **RAG / GraphRAG answers** — query engines and `Settings.llm`.",
        "3. **ReAct agent** — multi-step reasoning with tools.",
        "",
        "| `LLM_BACKEND` | How the notebook calls the model |",
        "|---------------|-----------------------------------|",
        "| `ollama` (default) | Subprocess → `ollama_model_runner.py` → LlamaIndex `CustomLLM` |",
        "| `openai` | `llama_index.llms.openai.OpenAI` with `OPENAI_API_KEY` |",
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
        "This is the same Bolt protocol used by `Neo4jPropertyGraphStore` and `Neo4jVectorStore`.",
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
        "LlamaIndex expects an **`LLM`** object on `Settings.llm`. Our course runner is a **CLI script**",
        "that returns JSON on stdout. We bridge the gap with:",
        "",
        "1. **`call_ollama_runner()`** — writes prompt to temp file, runs subprocess, parses JSON.",
        "2. **`OllamaRunnerLLM`** — a LlamaIndex **`CustomLLM`** used by query engines, retrievers, and agents.",
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
        "from typing import Any, Optional",
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
        "#### Step 0d.3 — LlamaIndex `CustomLLM` adapter",
        "",
        "- **`OllamaRunnerLLM`** subclasses **`CustomLLM`** and implements `complete(prompt)`.",
        "- All later sections use **`Settings.llm`** (query engines, `TextToCypherRetriever`, `ReActAgent`).",
    )
)

cells.append(
    code(
        "# Step 0d.3 — LlamaIndex CustomLLM for the Ollama runner",
        "from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata",
        "",
        "",
        "class OllamaRunnerLLM(CustomLLM):",
        "    model: str = OLLAMA_MODEL",
        "",
        "    @property",
        "    def metadata(self) -> LLMMetadata:",
        "        return LLMMetadata(",
        "            context_window=8192,",
        "            num_output=OLLAMA_MAX_TOKENS,",
        "            model_name=self.model,",
        "            is_chat_model=False,",
        "        )",
        "",
        "    def complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:",
        "        return CompletionResponse(text=call_ollama_runner(prompt, model=self.model))",
    )
)

cells.append(
    md(
        "### Step 0d.4 — Configure `Settings.llm`",
        "",
        "`Settings.llm` is the global default for:",
        "",
        "- `TextToCypherRetriever`",
        "- `VectorStoreIndex.as_query_engine()`",
        "- `ReActAgent`",
    )
)

cells.append(
    code(
        "# Step 0d.4 — Select backend and configure LlamaIndex Settings",
        "from llama_index.core import Settings",
        "",
        "if LLM_BACKEND == 'openai':",
        "    if not os.getenv('OPENAI_API_KEY'):",
        "        raise ValueError('OPENAI_API_KEY required when LLM_BACKEND=openai')",
        "    from llama_index.llms.openai import OpenAI",
        "    Settings.llm = OpenAI(model=OPENAI_MODEL, temperature=0)",
        "    print(f'Using OpenAI: {OPENAI_MODEL}')",
        "elif LLM_BACKEND == 'ollama':",
        "    Settings.llm = OllamaRunnerLLM()",
        "    print(f'Using Ollama runner: {OLLAMA_MODEL} @ {OLLAMA_HOST}')",
        "    print('Ensure Ollama is running: ollama serve')",
        "else:",
        "    raise ValueError(\"Set LLM_BACKEND to 'ollama' or 'openai'\")",
        "",
        "print('Settings.llm:', type(Settings.llm).__name__)",
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
# 3.1 Neo4j and LlamaIndex
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# 3.1 Neo4j and LlamaIndex",
        "",
        "### Big picture",
        "",
        "```text",
        "Your app (LlamaIndex)",
        "    │",
        "    ├── Neo4jPropertyGraphStore → schema, text-to-Cypher, graph queries",
        "    ├── Neo4jVectorStore        → embeddings + similarity search",
        "    ├── TextToCypherRetriever   → natural language → Cypher → context",
        "    └── ReActAgent + FunctionTools → agent over the graph",
        "            │",
        "            ▼",
        "      Neo4j Database (Bolt)",
        "```",
        "",
        "LlamaIndex Neo4j integrations live in **`llama-index-graph-stores-neo4j`** and",
        "**`llama-index-vector-stores-neo4jvector`** (see [Neo4j Labs — LlamaIndex](https://neo4j.com/labs/genai-ecosystem/llamaindex/)).",
    )
)

cells.append(
    md(
        "## 3.1.1 Neo4j integration — `Neo4jPropertyGraphStore`",
        "",
        "`Neo4jPropertyGraphStore` is LlamaIndex's property-graph adapter for Neo4j:",
        "",
        "- **`get_schema_str()`** — text schema for `TextToCypherRetriever`.",
        "- **`structured_query(cypher, params)`** — run Cypher when supported.",
        "- Works with **`PropertyGraphIndex`**, retrievers, and query engines.",
        "",
        "For lab seeding we also keep a thin **`run_cypher()`** helper on the official `neo4j` driver",
        "(same Bolt connection, explicit `CREATE` / `MERGE` in teaching cells).",
    )
)

cells.append(
    code(
        "# 3.1.1 — Neo4jPropertyGraphStore + run_cypher helper",
        "from neo4j import GraphDatabase",
        "from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore",
        "",
        "driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))",
        "",
        "",
        "def run_cypher(query: str, params: dict | None = None) -> list[dict]:",
        "    with driver.session(database=NEO4J_DATABASE) as session:",
        "        return [dict(row) for row in session.run(query, params or {})]",
        "",
        "",
        "graph_store = Neo4jPropertyGraphStore(",
        "    username=NEO4J_USERNAME,",
        "    password=NEO4J_PASSWORD,",
        "    url=NEO4J_URI,",
        "    database=NEO4J_DATABASE,",
        ")",
        "print('Neo4jPropertyGraphStore connected.')",
    )
)

cells.append(
    md(
        "**Expected output:** `Neo4jPropertyGraphStore connected.`",
        "",
        "No lab data is created yet — we only open the graph store and driver.",
    )
)

cells.append(
    md(
        "### 3.1.1b — First query through `run_cypher()`",
        "",
        "Same as `RETURN` in Browser, but results arrive as a **list of dictionaries** in Python.",
        "Agent tools and seeding cells use this helper throughout the lab.",
    )
)

cells.append(
    code(
        "# 3.1.1b — Query through run_cypher()",
        "rows = run_cypher('RETURN \"LlamaIndex + Neo4j OK\" AS message')",
        "print(rows)",
    )
)

cells.append(
    md(
        "## 3.1.2 Schema introspection with `get_schema_str()`",
        "",
        "Text-to-Cypher (Section 3.3) sends **schema text** to the LLM so it knows which labels exist.",
        "",
        "- **`graph_store.get_schema_str()`** introspects labels, relationships, and properties.",
        "- After you **seed** or **change** data, call it again before text-to-Cypher demos.",
        "",
        "Better schema in Neo4j (consistent labels, documented properties) → better generated Cypher.",
    )
)

cells.append(
    code(
        "# 3.1.2 — Preview graph schema (truncated)",
        "schema_str = graph_store.get_schema_str()",
        "schema_preview = (schema_str or '')[:1200]",
        "print(schema_preview)",
        "if len(schema_str or '') > 1200:",
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
        "## 3.1.3 Seed the LlamaIndex lab graph",
        "",
        "We build a **toy maritime knowledge graph** plus **text chunks** for vector search.",
        "All lab nodes include the label **`LlamaIndexLab`** so you can delete or filter them safely.",
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
        "| `LlamaIndexLab` | Marker label on all course nodes |",
    )
)

cells.append(
    md(
        "### 3.1.3a — Clear previous lab data",
        "",
        "Re-running the notebook should not duplicate nodes. We delete every node with `LlamaIndexLab`",
        "before inserting fresh data. **Other graphs in the same database are not touched.**",
    )
)

cells.append(
    code(
        "# 3.1.3a — Clear previous lab data (safe to re-run)",
        "run_cypher(",
        "    '''",
        "    MATCH (n:LlamaIndexLab)",
        "    DETACH DELETE n",
        "    '''",
        ")",
        "print('Cleared prior LlamaIndexLab subgraph.')",
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
        "run_cypher(",
        "    '''",
        "    CREATE (lab:LlamaIndexLab {course: 'Using Knowledge Graph with LlamaIndex', module: 'Module_8'})",
        "    CREATE (p1:Port:LlamaIndexLab {id: 'Port_of_Rotterdam', name: 'Port of Rotterdam', country: 'Netherlands'})",
        "    CREATE (p2:Port:LlamaIndexLab {id: 'Port_of_Singapore', name: 'Port of Singapore', country: 'Singapore'})",
        "    CREATE (o:Organization:LlamaIndexLab {id: 'Maersk', name: 'Maersk', country: 'Denmark'})",
        "    CREATE (c:Canal:LlamaIndexLab {id: 'Panama_Canal', name: 'Panama Canal', country: 'Panama'})",
        "    CREATE (n1:Country:LlamaIndexLab {id: 'Netherlands', name: 'Netherlands'})",
        "    CREATE (n2:Country:LlamaIndexLab {id: 'Singapore', name: 'Singapore'})",
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
        "MATCH (o:Organization:LlamaIndexLab)-[r]->(x)",
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
        "    run_cypher(",
        "        '''",
        "        MERGE (d:Document:LlamaIndexLab {id: $doc_id})",
        "        SET d.title = 'LlamaIndex lab corpus'",
        "        MERGE (c:Chunk:LlamaIndexLab {id: $chunk_id})",
        "        SET c.text = $text, c.source = $source",
        "        MERGE (d)-[:HAS_CHUNK]->(c)",
        "        ''',",
        "        params={'doc_id': 'llamaindex_lab_doc', 'chunk_id': ch['id'], 'text': ch['text'], 'source': ch['source']},",
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
        "    run_cypher(",
        "        '''",
        "        MATCH (c:Chunk:LlamaIndexLab {id: $chunk_id})",
        "        MATCH (e:LlamaIndexLab {id: $entity_id})",
        "        MERGE (c)-[:MENTIONS]->(e)",
        "        ''',",
        "        params={'chunk_id': chunk_id, 'entity_id': entity_id},",
        "    )",
        "print('Chunk–entity links created.')",
    )
)

cells.append(
    md(
        "**Checkpoint:** Re-run **3.1.2** — you should now see `Port`, `Chunk`, `MENTIONS`, etc. in `get_schema_str()`.",
    )
)

cells.append(
    md(
        "## 3.1.4 Simple LlamaIndex agent",
        "",
        "An **agent** loops: think → pick a **tool** → observe result → repeat until done.",
        "",
        "We register two tools:",
        "",
        "| Tool | When to use |",
        "|------|-------------|",
        "| `run_read_cypher` | User gives Cypher or wants raw rows |",
        "| `ask_graph_in_natural_language` | Open-ended question → `TextToCypherRetriever` (Section 3.3) |",
        "",
        "> **Order note:** The natural-language tool needs `CYPHER_QUERY_ENGINE` from Section 3.3.",
        "> You can define the agent here, but run the demo cell **after** 3.3.",
        "",
        "> **Production:** Use read-only DB roles, query allow-lists, and human review for generated Cypher.",
    )
)

cells.append(
    md(
        "### 3.1.4a — Define tools",
        "",
        "`FunctionTool.from_defaults()` wraps Python functions as LlamaIndex tools.",
        "The ReAct agent reads tool names and descriptions to decide which tool to call.",
    )
)

cells.append(
    code(
        "# 3.1.4a — Define tools (Cypher QA chain wired in 3.3; placeholder first)",
        "from llama_index.core.tools import FunctionTool",
        "",
        "CYPHER_QUERY_ENGINE = None  # set in Section 3.3",
        "",
        "",
        "def run_read_cypher_fn(cypher: str) -> str:",
        "    forbidden = ('create ', 'merge ', 'delete ', 'detach ', 'set ', 'remove ')",
        "    if any(word in cypher.lower() for word in forbidden):",
        "        return 'Error: only read-only queries (MATCH/RETURN) are allowed in this lab tool.'",
        "    try:",
        "        return str(run_cypher(cypher))",
        "    except Exception as exc:",
        "        return f'Cypher error: {exc}'",
        "",
        "",
        "def ask_graph_in_natural_language_fn(question: str) -> str:",
        "    if CYPHER_QUERY_ENGINE is None:",
        "        return 'Cypher query engine not initialized yet — run Section 3.3 first, then re-run agent cells.'",
        "    return str(CYPHER_QUERY_ENGINE.query(question))",
        "",
        "",
        "run_read_cypher = FunctionTool.from_defaults(",
        "    fn=run_read_cypher_fn,",
        "    name='run_read_cypher',",
        "    description='Execute read-only Cypher (MATCH/RETURN) on the lab graph.',",
        ")",
        "ask_graph_in_natural_language = FunctionTool.from_defaults(",
        "    fn=ask_graph_in_natural_language_fn,",
        "    name='ask_graph_in_natural_language',",
        "    description='Answer open questions with TextToCypherRetriever (text-to-Cypher).',",
        ")",
        "agent_tools = [run_read_cypher, ask_graph_in_natural_language]",
        "print('Tools:', [t.metadata.name for t in agent_tools])",
    )
)

cells.append(
    md(
        "### 3.1.4b — ReAct agent",
        "",
        "**ReAct** (Reason + Act) prompts the model in plain text:",
        "`Thought` → `Action` → `Action Input` → `Observation` → … → `Final Answer`.",
        "",
        "LlamaIndex **`ReActAgent`** uses the same text-based ReAct loop, which works well with",
        "`ollama_model_runner.py` (free-text responses, not structured tool JSON).",
        "",
        "| Parameter | Value | Why |",
        "|-----------|-------|-----|",
        "| `max_iterations` | 5 | Prevents infinite tool loops |",
        "| `verbose` | True | Shows reasoning in notebook output |",
    )
)

cells.append(
    code(
        "# 3.1.4b — Build LlamaIndex ReActAgent",
        "from llama_index.core.agent import ReActAgent",
        "",
        "agent = ReActAgent.from_tools(",
        "    agent_tools,",
        "    llm=Settings.llm,",
        "    verbose=True,",
        "    max_iterations=5,",
        ")",
        "print('ReActAgent ready (run Section 3.3 before natural-language tool works).')",
    )
)

cells.append(
    md(
        "### 3.1.4c — Try the agent (preview)",
        "",
        "This cell **skips** until `CYPHER_QUERY_ENGINE` exists. After Section 3.3, re-run **3.3.4b** for a full demo.",
    )
)

cells.append(
    code(
        "# 3.1.4c — Example agent question (preview)",
        "if CYPHER_QUERY_ENGINE is not None:",
        "    response = agent.query('Which organization operates in the Port of Rotterdam?')",
        "    print(response)",
        "else:",
        "    print('Skip until CYPHER_QUERY_ENGINE is defined in Section 3.3 (then run cell 3.3.4b).')",
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
        "**`Neo4jVectorStore`** (LlamaIndex) creates the index and powers **`VectorStoreIndex`** retrievers.",
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
        "## 3.2.1 Vector search with `Neo4jVectorStore`",
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
        "# 3.2.1a — Embedding model (LlamaIndex Settings)",
        "from llama_index.core import Settings",
        "from llama_index.embeddings.huggingface import HuggingFaceEmbedding",
        "",
        "EMBED_DIM = 384",
        "Settings.embed_model = HuggingFaceEmbedding(",
        "    model_name='sentence-transformers/all-MiniLM-L6-v2'",
        ")",
        "sample_vec = Settings.embed_model.get_text_embedding('maritime port')",
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
        "### 3.2.1b — Load chunks as LlamaIndex `TextNode` objects",
        "",
        "We read `Chunk` nodes from Neo4j and map them to **`TextNode(text=..., metadata=...)`**.",
        "Metadata `chunk_id` is required later for GraphRAG expansion.",
    )
)

cells.append(
    code(
        "# 3.2.1b — Load chunk texts from Neo4j",
        "from llama_index.core.schema import TextNode",
        "",
        "chunk_rows = run_cypher(",
        "    '''",
        "    MATCH (c:Chunk:LlamaIndexLab)",
        "    RETURN c.id AS id, c.text AS text, c.source AS source",
        "    ORDER BY c.id",
        "    '''",
        ")",
        "chunk_nodes = [",
        "    TextNode(text=row['text'], metadata={'chunk_id': row['id'], 'source': row.get('source')})",
        "    for row in chunk_rows",
        "]",
        "print('TextNodes for indexing:', len(chunk_nodes))",
        "for n in chunk_nodes[:2]:",
        "    print('-', n.metadata['chunk_id'], ':', n.text[:60], '...')",
    )
)

cells.append(
    md(
        "### 3.2.1c — Create `VectorStoreIndex` with `Neo4jVectorStore`",
        "",
        "| Component | This lab |",
        "|-----------|----------|",
        "| Vector store | `Neo4jVectorStore` |",
        "| Index | `VectorStoreIndex` |",
        "| Embedding dim | `384` (MiniLM-L6-v2) |",
        "",
        "`VectorStoreIndex` **embeds** each `TextNode` and persists vectors through `Neo4jVectorStore`.",
        "Re-running this cell may add duplicate vector entries — use a fresh lab DB or drop the vector index if needed.",
    )
)

cells.append(
    code(
        "# 3.2.1c — Build VectorStoreIndex backed by Neo4j",
        "from llama_index.vector_stores.neo4jvector import Neo4jVectorStore",
        "from llama_index.core import StorageContext, VectorStoreIndex",
        "",
        "neo4j_vector = Neo4jVectorStore(",
        "    NEO4J_USERNAME,",
        "    NEO4J_PASSWORD,",
        "    NEO4J_URI,",
        "    EMBED_DIM,",
        ")",
        "storage_context = StorageContext.from_defaults(vector_store=neo4j_vector)",
        "vector_index = VectorStoreIndex(",
        "    chunk_nodes,",
        "    storage_context=storage_context,",
        ")",
        "print('VectorStoreIndex ready (Neo4jVectorStore).')",
    )
)

cells.append(
    md(
        "### 3.2.1d — Similarity search",
        "",
        "`as_retriever(similarity_top_k=2).retrieve(query)` embeds the query and returns top-k `NodeWithScore` items.",
        "Compare results to the Rotterdam / Europe question — the Rotterdam chunk should rank high.",
    )
)

cells.append(
    code(
        "# 3.2.1d — Similarity search",
        "query = 'Which port is the largest in Europe?'",
        "hits = vector_index.as_retriever(similarity_top_k=2).retrieve(query)",
        "print('Query:', query)",
        "for i, hit in enumerate(hits, 1):",
        "    print(f'{i}. {hit.metadata} -> {hit.text[:80]}...')",
    )
)

cells.append(
    md(
        "## 3.2.2 Vector retriever (RAG)",
        "",
        "### What is a retriever?",
        "",
        "In LlamaIndex, a **retriever** returns `NodeWithScore` objects.",
        "A **`RetrieverQueryEngine`** combines retrieval + synthesis in one `query()` call.",
        "",
        "### Minimal RAG pipeline",
        "",
        "1. **Retrieve** chunk nodes similar to the user question (`VectorStoreIndex` retriever).",
        "2. **Synthesize** an answer with `Settings.llm` grounded in retrieved nodes.",
    )
)

cells.append(
    md(
        "### 3.2.2a — `as_retriever()`",
        "",
        "`similarity_top_k=3` returns three chunks per query. Increase `k` for broader context",
        "(more tokens, higher cost/latency).",
    )
)

cells.append(
    code(
        "# 3.2.2a — Create vector retriever",
        "vector_retriever = vector_index.as_retriever(similarity_top_k=3)",
        "retrieved = vector_retriever.retrieve('Panama Canal shipping route')",
        "print('Retrieved', len(retrieved), 'chunks')",
        "for hit in retrieved:",
        "    print('-', hit.text[:70])",
    )
)

cells.append(
    md(
        "### 3.2.2b — RAG with `as_query_engine()`",
        "",
        "`VectorStoreIndex.as_query_engine()` combines retrieval + synthesis using **`Settings.llm`**.",
        "This is the idiomatic LlamaIndex RAG pattern over **`Neo4jVectorStore`**.",
    )
)

cells.append(
    code(
        "# 3.2.2b — RAG query engine",
        "rag_engine = vector_index.as_query_engine(similarity_top_k=3)",
        "rag_response = rag_engine.query('What does Maersk use for routes?')",
        "print(rag_response)",
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
        "2. Read `chunk_id` metadata from each retrieved node.",
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
        "    rows = run_cypher(",
        "        '''",
        "        UNWIND $ids AS chunk_id",
        "        MATCH (c:Chunk:LlamaIndexLab {id: chunk_id})-[:MENTIONS]->(e:LlamaIndexLab)",
        "        OPTIONAL MATCH (e)-[r]-(n:LlamaIndexLab)",
        "        WHERE type(r) IN ['LOCATED_IN', 'OPERATES_IN', 'USES_ROUTE']",
        "        RETURN DISTINCT c.id AS chunk, e.id AS entity, type(r) AS rel, n.id AS related",
        "        LIMIT 30",
        "        ''',",
        "        {'ids': chunk_ids},",
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
        "    hits = vector_retriever.retrieve(question)[:k]",
        "    chunk_ids = [h.metadata.get('chunk_id') for h in hits if h.metadata.get('chunk_id')]",
        "    return {",
        "        'chunks': hits,",
        "        'graph_context': graph_context_for_chunks(chunk_ids),",
        "    }",
        "",
        "sample = graphrag_retrieve('Rotterdam Europe port')",
        "print('Graph context preview:\\n', sample['graph_context'][:500])",
    )
)

cells.append(
    md(
        "### 3.2.3b — GraphRAG answer with `Settings.llm`",
        "",
        "We combine chunk text and graph facts in one prompt, then call **`Settings.llm.complete()`**.",
    )
)

cells.append(
    code(
        "# 3.2.3b — GraphRAG answer",
        "def format_nodes(hits):",
        "    return '\\n\\n'.join(f'- {h.text}' for h in hits)",
        "",
        "",
        "def run_graphrag(question: str) -> str:",
        "    pack = graphrag_retrieve(question)",
        "    chunks_txt = format_nodes(pack['chunks'])",
        "    prompt = (",
        "        'Answer using chunk text and graph facts. Cite relationships when relevant.\\n\\n'",
        "        f'Chunks:\\n{chunks_txt}\\n\\nGraph facts:\\n{pack[\"graph_context\"]}\\n\\n'",
        "        f'Question: {question}'",
        "    )",
        "    return str(Settings.llm.complete(prompt))",
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
        "3. Rebuild `VectorStoreIndex` with new `TextNode` objects.",
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
        "### How `TextToCypherRetriever` works",
        "",
        "```text",
        "User question",
        "    → LLM + graph_store schema → Cypher query",
        "    → Execute on Neo4j → result rows",
        "    → Format rows into retrieved TextNode context",
        "```",
        "",
        "Wrap the retriever in a **`RetrieverQueryEngine`** to add a final natural-language answer step.",
        "Quality depends on schema clarity, model size, and question phrasing.",
    )
)

cells.append(
    md(
        "## 3.3.1 Schema for Cypher generation",
        "",
        "Before building the chain, we:",
        "",
        "1. **`get_schema_str()`** — preview schema text sent to the LLM.",
        "2. **Count nodes** by label — confirm `LlamaIndexLab` data is present.",
        "",
        "If counts are zero, re-run Section **3.1.3**.",
    )
)

cells.append(
    code(
        "# 3.3.1 — Schema and label inspection",
        "print('Schema preview:', graph_store.get_schema_str()[:600], '...')",
        "label_rows = run_cypher(",
        "    '''",
        "    MATCH (n:LlamaIndexLab)",
        "    RETURN DISTINCT labels(n) AS labels, count(*) AS cnt",
        "    ORDER BY cnt DESC",
        "    '''",
        ")",
        "print('LlamaIndexLab nodes by label combination:')",
        "for row in label_rows:",
        "    print(row)",
    )
)

cells.append(
    md(
        "## 3.3.2 Text-to-Cypher retriever + query engine",
        "",
        "### Safety note",
        "",
        "Generated Cypher could theoretically **write** data. This course uses a **disposable lab graph** only.",
        "In production: read-only DB roles, `cypher_validator`, and query allow-lists.",
        "",
        "### Components",
        "",
        "| Component | Role |",
        "|-----------|------|",
        "| `TextToCypherRetriever` | NL → Cypher → graph rows as nodes |",
        "| `RetrieverQueryEngine` | Retriever + `Settings.llm` → final answer |",
    )
)

cells.append(
    code(
        "# 3.3.2 — TextToCypherRetriever + RetrieverQueryEngine",
        "from llama_index.core.indices.property_graph import TextToCypherRetriever",
        "from llama_index.core.query_engine import RetrieverQueryEngine",
        "from llama_index.core.prompts import PromptTemplate",
        "",
        "DEFAULT_RESPONSE_TEMPLATE = (",
        "    'Generated Cypher query:\\n{query}\\n\\nCypher Response:\\n{response}'",
        ")",
        "",
        "text_to_cypher_retriever = TextToCypherRetriever(",
        "    graph_store,",
        "    llm=Settings.llm,",
        "    text_to_cypher_template=PromptTemplate(graph_store.text_to_cypher_template),",
        "    response_template=DEFAULT_RESPONSE_TEMPLATE,",
        ")",
        "CYPHER_QUERY_ENGINE = RetrieverQueryEngine.from_args(",
        "    text_to_cypher_retriever,",
        "    llm=Settings.llm,",
        ")",
        "print('TextToCypherRetriever + query engine ready.')",
    )
)

cells.append(
    md(
        "### 3.3.2b — Example question",
        "",
        "The response should mention ports in the **Netherlands** and **Singapore**.",
        "If Cypher fails, inspect retrieved node text (contains generated query) and compare with Browser.",
    )
)

cells.append(
    code(
        "# 3.3.2b — Ask a natural language question",
        "qa_response = CYPHER_QUERY_ENGINE.query(",
        "    'Which ports are located in the Netherlands or Singapore?'",
        ")",
        "print('Answer:', qa_response)",
        "retrieved_ctx = text_to_cypher_retriever.retrieve(",
        "    'Which ports are located in the Netherlands or Singapore?'",
        ")",
        "print('Retriever context preview:', retrieved_ctx[0].text[:500] if retrieved_ctx else '(empty)')",
    )
)

cells.append(
    md(
        "## 3.3.3 Customize Cypher generation",
        "",
        "Key knobs on **`TextToCypherRetriever`**:",
        "",
        "| Option | Effect |",
        "|--------|--------|",
        "| `llm` | Model for Cypher generation (defaults to `Settings.llm`) |",
        "| `text_to_cypher_template` | Prompt with `{schema}` and `{question}` |",
        "| `response_template` | How Cypher results become node text |",
        "| `cypher_validator` | Callable to reject unsafe / invalid Cypher |",
        "",
        "Below we add a lab hint so the LLM prefers **`LlamaIndexLab`** nodes.",
    )
)

cells.append(
    code(
        "# 3.3.3 — Custom text-to-Cypher template (lab scope hint)",
        "LAB_CYPHER_TEMPLATE = (",
        "    graph_store.text_to_cypher_template",
        "    + '\\n\\nOnly use nodes labeled LlamaIndexLab from this course lab.'",
        ")",
        "filtered_retriever = TextToCypherRetriever(",
        "    graph_store,",
        "    llm=Settings.llm,",
        "    text_to_cypher_template=PromptTemplate(LAB_CYPHER_TEMPLATE),",
        "    response_template=DEFAULT_RESPONSE_TEMPLATE,",
        ")",
        "filtered_engine = RetrieverQueryEngine.from_args(filtered_retriever, llm=Settings.llm)",
        "filtered_answer = filtered_engine.query('What route does Maersk use?')",
        "print(filtered_answer)",
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
        "`TextToCypherRetriever.retrieve()` already returns **`NodeWithScore`** objects.",
        "Downstream RAG can merge these nodes with vector chunks before synthesis.",
    )
)

cells.append(
    code(
        "# 3.3.4a — Text-to-Cypher as a retriever (direct)",
        "cypher_nodes = text_to_cypher_retriever.retrieve('Which organization operates in Rotterdam?')",
        "print('Retrieved nodes:', len(cypher_nodes))",
        "if cypher_nodes:",
        "    print(cypher_nodes[0].text[:500])",
    )
)

cells.append(
    md(
        "### 3.3.4b — Re-run the agent with a live `CYPHER_QUERY_ENGINE`",
        "",
        "Now `ask_graph_in_natural_language` can call the query engine. Expect verbose ReAct steps",
        "and a final answer mentioning **Maersk** and **Rotterdam**.",
        "",
        "**Note:** This may take 30–90 seconds on local Ollama — normal for multi-step LLM calls.",
    )
)

cells.append(
    code(
        "# 3.3.4b — Re-run agent now that CYPHER_QUERY_ENGINE exists",
        "response = agent.query('Which organization operates in the Port of Rotterdam?')",
        "print(response)",
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
        "| Neo4j + LlamaIndex | `Neo4jPropertyGraphStore` | Connect, schema, graph queries |",
        "| Lab data | Cypher `CREATE` / `MERGE` | Maritime graph + chunks + `MENTIONS` |",
        "| Vector RAG | `Neo4jVectorStore` + `VectorStoreIndex` | Embed, index, retrieve, answer |",
        "| GraphRAG | Custom expansion + `Settings.llm` | Vectors + relationship context |",
        "| Text to Cypher | `TextToCypherRetriever` | NL → Cypher → context → answer |",
        "| Agent | `ReActAgent` + `FunctionTool` | Tool choice over graph |",
        "",
        "### Troubleshooting quick reference",
        "",
        "| Symptom | Check |",
        "|---------|-------|",
        "| Neo4j connection error | `NEO4J_SETUP.md`, instance running, `.env` password |",
        "| Ollama runner error | `ollama serve`, `ollama pull`, `LLM_MODEL_SETUP.md` |",
        "| Empty vector results | Re-run 3.1.3c and 3.2.1c |",
        "| Bad / invalid Cypher | `get_schema_str()`, larger model, custom template |",
        "| Agent parsing error | Re-run with `verbose=True`; try `llama3.1:8b` |",
        "",
        "### Next steps",
        "",
        "- **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** — build graphs from unstructured text with LLMs.",
        "- **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** — same lab topics with LangChain orchestration.",
        "- Combine **`VectorContextRetriever`** + **`TextToCypherRetriever`** for full GraphRAG (see [Neo4j Labs](https://neo4j.com/labs/genai-ecosystem/genai-frameworks/llamaindex-agents/)).",
        "- Add corpus chunks (Section 3.2.4) and tune `similarity_top_k`, embeddings, and prompts.",
        "- Production hardening: read-only DB user, `cypher_validator`, observability on generated Cypher.",
        "",
        "### References",
        "",
        "- [Property Graph Index guide](https://developers.llamaindex.ai/python/framework/module_guides/indexing/lpg_index_guide/)",
        "- [Neo4j vector store (LlamaIndex)](https://developers.llamaindex.ai/python/framework/integrations/vector_stores/neo4jvectordemo/)",
        "- [Neo4j GenAI — LlamaIndex](https://neo4j.com/labs/genai-ecosystem/genai-frameworks/llamaindex-agents/)",
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

out = Path(__file__).resolve().parents[1] / "Module_8_Using_Knowledge_Graph_with_LlamaIndex.ipynb"
out.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
md_count = sum(1 for c in cells if c["cell_type"] == "markdown")
code_count = sum(1 for c in cells if c["cell_type"] == "code")
print(f"Wrote {out}")
print(f"Total cells: {len(cells)} (markdown: {md_count}, code: {code_count})")
