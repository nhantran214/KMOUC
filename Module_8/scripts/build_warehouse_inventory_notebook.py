#!/usr/bin/env python3
"""Generate Module_8_Warehouse_Inventory_Management_with_Knowledge_Graphs.ipynb."""
import json
from pathlib import Path


def md(*lines: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}


def code(*lines: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "outputs": [], "source": [l + "\n" for l in lines]}


LAB = "WarehouseInventoryLab"
cells: list = []

# =============================================================================
# Title & outline
# =============================================================================
cells.append(
    md(
        "# Enhancing Warehouse and Inventory Management Practices with Knowledge Graphs",
        "",
        "**Course module:** Module 8",
        "**Audience:** Beginners who want to apply Neo4j to real supply-chain operations data.",
        "",
        "## Course description",
        "",
        "Warehouse and inventory teams juggle **stock levels**, **demand signals**, **equipment availability**,",
        "**supplier reliability**, and **operational risk** — often spread across spreadsheets and dashboards.",
        "A **knowledge graph** connects these facts explicitly so you can ask relationship questions that",
        "are awkward in SQL alone.",
        "",
        "In this hands-on course you will:",
        "",
        "1. Explore the **Logistics and Supply Chain** CSV dataset (warehouse-centric view).",
        "2. Design a **domain graph model** for inventory management.",
        "3. Load a dedicated subgraph into Neo4j (label **`WarehouseInventoryLab`** — isolated from other course graphs).",
        "4. Run **practical Cypher queries** for stock risk, fulfillment, and equipment bottlenecks.",
        "5. (Optional) Ask **natural-language questions** with an LLM + Cypher chain.",
        "",
        "> **Language:** All instructional text is in **English**.",
        "",
        "> **Setup (required):** Complete **`NEO4J_SETUP.md`** before running code.",
        "> For the optional LLM section, complete **`LLM_MODEL_SETUP.md`** and use **`ollama_model_runner.py`**",
        "> (or configure OpenAI).",
        "",
        "### How to use this notebook",
        "",
        "1. Read each **markdown** cell before running the **code** cell below it.",
        "2. Run cells **in order** from Step 0 downward.",
        "3. Lab data uses the label **`WarehouseInventoryLab`** — safe to delete and re-seed without touching",
        "   `CourseKG`, `KGApplicationsLab`, `LangChainLab`, or `LlamaIndexLab`.",
        "4. Code cells are intentionally **short**; markdown explains the *why* before each step.",
    )
)

cells.append(
    md(
        "## Prerequisites",
        "",
        "| Skill | Why you need it |",
        "|-------|-----------------|",
        "| Neo4j basics | Nodes, relationships, `MATCH`, `RETURN` |",
        "| Python & pandas | Load and transform the CSV |",
        "| (Optional) LLMs | Part 10 — natural-language inventory Q&A |",
        "",
        "### Dataset",
        "",
        "| File | Description |",
        "|------|-------------|",
        "| `data/logistics-supply-chain/dynamic_supply_chain_logistics_dataset.csv` | Hourly logistics telemetry (Kaggle, CC0-1.0) |",
        "",
        "We derive **warehouse regions** from GPS coordinates and aggregate readings to **weekly snapshots**",
        "for a manageable beginner-friendly graph (~2,000 nodes).",
        "",
        "## Course outline",
        "",
        "| Part | Topic | Business question |",
        "|------|--------|-------------------|",
        "| **0** | Environment & Neo4j connection | — |",
        "| **1** | Why knowledge graphs for warehouses | When graphs beat flat tables |",
        "| **2** | Explore the CSV | What signals exist in the data? |",
        "| **3** | Design the graph model | What entities and relationships do we need? |",
        "| **4** | Transform data in Python | How do we go from rows to graph records? |",
        "| **5** | Load into Neo4j | How do we seed an isolated lab subgraph? |",
        "| **6** | Low-stock discovery | *Which warehouses are critically low?* |",
        "| **7** | Demand vs inventory | *Where is demand higher than available stock?* |",
        "| **8** | Risk & equipment stress | *Where do risk and equipment constraints overlap?* |",
        "| **9** | Supplier reliability paths | *Which snapshots depend on weak suppliers?* |",
        "| **10** | Business Q&A (LLM + Cypher) | *Ask questions in plain English* |",
        "| **11** | Advanced improvements (reading) | What to explore next on your own |",
        "| **12** | Wrap-up | Map patterns to your organization |",
    )
)

# =============================================================================
# Step 0
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Step 0 — Environment and Neo4j connection",
        "",
        "### Before you run any code",
        "",
        "1. Complete **`NEO4J_SETUP.md`** — Aura, Desktop, or Docker; note URI, username, password.",
        "2. Copy `Module_8/.env.example` → `Module_8/.env` and fill in Neo4j credentials.",
        "3. For **Part 10** (LLM Q&A), also complete **`LLM_MODEL_SETUP.md`** and start `ollama serve`.",
        "",
        "### What Step 0 does",
        "",
        "| Step | Purpose |",
        "|------|---------|",
        "| 0a | Install Python packages |",
        "| 0b | Load paths and environment variables |",
        "| 0c | Verify Neo4j Bolt connectivity |",
        "| 0d | Define helpers (`run_cypher`, optional Ollama runner) |",
    )
)

cells.append(
    md(
        "### Step 0a — Install Python packages",
        "",
        "**What this cell does:** Installs the Python libraries required for the rest of the notebook.",
        "",
        "**When to run it:** Once per virtual environment (conda, venv, or system Python). If you already",
        "installed these packages for another Module 8 notebook, you may skip this cell.",
        "",
        "| Package | Role in this course |",
        "|---------|---------------------|",
        "| `neo4j` | Official Bolt driver — connects Python to your Neo4j database |",
        "| `python-dotenv` | Loads `Module_8/.env` so secrets stay out of the notebook |",
        "| `requests` | HTTP calls used indirectly by `ollama_model_runner.py` |",
        "| `pandas` | Loads and transforms the logistics CSV before graph load |",
        "| `langchain`, `langchain-neo4j`, `langchain-openai` | Part 10 — natural-language → Cypher Q&A |",
        "",
        "**Expected output:** Pip may print nothing (`-q` quiet mode). The next cells should import without `ModuleNotFoundError`.",
        "",
        "> **Troubleshooting:** If install fails, activate your course virtual environment first, then re-run.",
        "> Full dependency notes are in **`NEO4J_SETUP.md`** (Python environment section).",
    )
)

cells.append(
    code(
        "# Step 0a — Install Python dependencies (run once per environment)",
        "%pip install -q neo4j python-dotenv requests pandas \\",
        "    langchain langchain-community langchain-neo4j langchain-openai",
    )
)

cells.append(
    md(
        "### Step 0b.1 — Resolve the `Module_8` folder",
        "",
        "**What this cell does:** Figures out where the `Module_8` directory lives on disk and loads your `.env` file.",
        "",
        "**Why it matters:** Jupyter's *current working directory* depends on how you launched the notebook:",
        "",
        "- If you opened the notebook from the **repo root** (`KMOU_Course/`), paths like `data/...` would be wrong unless we adjust.",
        "- If you opened from **`Module_8/`**, paths work directly.",
        "",
        "The logic checks `Path('.').name`: when it is not `Module_8`, we look for a child folder `Module_8/`.",
        "",
        "**Key lines:**",
        "",
        "- `load_dotenv(MODULE_DIR / '.env')` — reads `NEO4J_URI`, `NEO4J_PASSWORD`, `LLM_BACKEND`, etc.",
        "- `print('Module directory:', ...)` — confirm this points to the folder that contains `data/` and `.env`.",
        "",
        "**Expected output:**",
        "",
        "```text",
        "Module directory: /path/to/KMOU_Course/Module_8",
        "```",
        "",
        "> **Troubleshooting:** If `.env` is missing, copy `Module_8/.env.example` → `Module_8/.env` and fill in Neo4j credentials per **`NEO4J_SETUP.md`**.",
    )
)

cells.append(
    code(
        "# Step 0b.1 — Resolve Module_8 directory",
        "import os",
        "from pathlib import Path",
        "from dotenv import load_dotenv",
        "",
        "MODULE_DIR = Path('.').resolve()",
        "if MODULE_DIR.name != 'Module_8':",
        "    _candidate = MODULE_DIR / 'Module_8'",
        "    if _candidate.is_dir():",
        "        MODULE_DIR = _candidate.resolve()",
        "load_dotenv(MODULE_DIR / '.env')",
        "print('Module directory:', MODULE_DIR)",
    )
)

cells.append(
    md(
        "### Step 0b.2 — Paths, lab label, and Neo4j settings",
        "",
        "**What this cell does:** Defines constants used in every later step — dataset path, lab isolation label,",
        "Neo4j connection parameters, and tunable lab limits.",
        "",
        "**Configuration variables:**",
        "",
        "| Variable | Default | Meaning |",
        "|----------|---------|---------|",
        "| `DATA_PATH` | `data/logistics-supply-chain/...csv` | Source CSV for the warehouse lab |",
        "| `LAB_LABEL` | `WarehouseInventoryLab` | Marker label on **all** nodes in this course |",
        "| `LAB_TOP_WAREHOUSES` | `15` | How many busiest GPS regions to model (override via `.env`) |",
        "| `LAB_BATCH_SIZE` | `100` | Rows per Neo4j `UNWIND` batch during load |",
        "| `NEO4J_URI` | `neo4j://localhost:7687` | Bolt URL — Aura uses `neo4j+s://...` |",
        "| `NEO4J_DATABASE` | `neo4j` | Database name (Aura Free: usually `neo4j`) |",
        "",
        "**Why `LAB_LABEL` is critical:** Other Module 8 notebooks use different labels (`CourseKG`, `LangChainLab`, etc.).",
        "By tagging every node with `WarehouseInventoryLab`, we can delete or query **only** this lab's graph without",
        "affecting graphs you built in other notebooks.",
        "",
        "**Expected output:**",
        "",
        "- `Dataset exists: True` — if `False`, download the Kaggle CSV into `data/logistics-supply-chain/`.",
        "- `Neo4j URI:` should match your setup (local Docker or Aura).",
    )
)

cells.append(
    code(
        "# Step 0b.2 — Dataset path and Neo4j settings",
        "DATA_PATH = MODULE_DIR / 'data' / 'logistics-supply-chain' / 'dynamic_supply_chain_logistics_dataset.csv'",
        "LAB_LABEL = 'WarehouseInventoryLab'",
        "LAB_TOP_WAREHOUSES = int(os.getenv('LAB_TOP_WAREHOUSES', '15'))",
        "LAB_BATCH_SIZE = int(os.getenv('LAB_BATCH_SIZE', '100'))",
        "",
        "NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')",
        "NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')",
        "NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')",
        "NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')",
        "",
        "print('Dataset:', DATA_PATH)",
        "print('Dataset exists:', DATA_PATH.exists())",
        "print('Lab label:', LAB_LABEL)",
        "print('Top warehouses to model:', LAB_TOP_WAREHOUSES)",
        "print('Neo4j URI:', NEO4J_URI)",
    )
)

cells.append(
    md(
        "### Step 0b.3 — LLM settings (Part 10 only)",
        "",
        "**What this cell does:** Reads LLM-related environment variables. Parts 1–9 use **Cypher only**;",
        "Part 10 adds natural-language question answering.",
        "",
        "**Two supported backends:**",
        "",
        "| `LLM_BACKEND` | How the model is called | Setup guide |",
        "|---------------|-------------------------|-------------|",
        "| `ollama` (recommended) | Subprocess → `ollama_model_runner.py` → Ollama HTTP API | **`LLM_MODEL_SETUP.md`** Option 1 |",
        "| `openai` | `langchain_openai.ChatOpenAI` | **`LLM_MODEL_SETUP.md`** Option 2 |",
        "",
        "**Ollama variables:**",
        "",
        "- `OLLAMA_HOST` — usually `http://localhost:11434` while `ollama serve` is running.",
        "- `OLLAMA_MODEL` — e.g. `llama3.2:3b` (faster) or `llama3.1:8b` (better Cypher generation).",
        "- `OLLAMA_MAX_TOKENS` — cap on response length; increase if answers are truncated.",
        "",
        "**You can skip Part 10** if you only want warehouse Cypher exercises — but running this cell is harmless.",
        "",
        "**Expected output:** `LLM backend: ollama` (or `openai`).",
    )
)

cells.append(
    code(
        "# Step 0b.3 — LLM backend (used in Part 10)",
        "LLM_BACKEND = os.getenv('LLM_BACKEND', 'ollama').lower()",
        "OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')",
        "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')",
        "OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', '0'))",
        "OLLAMA_MAX_TOKENS = int(os.getenv('OLLAMA_MAX_TOKENS', '2048'))",
        "OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')",
        "print('LLM backend:', LLM_BACKEND)",
    )
)

cells.append(
    md(
        "### Step 0c — Verify Neo4j connectivity",
        "",
        "**What this cell does:** Opens a short-lived Bolt session to Neo4j and runs a one-line smoke test.",
        "",
        "**Why before loading data:** Catching connection problems early saves debugging time during Part 5.",
        "Common failures happen here — wrong password, database not running, incorrect URI scheme.",
        "",
        "**How it works:**",
        "",
        "1. `GraphDatabase.driver(NEO4J_URI, auth=(username, password))` — creates a driver (connection pool).",
        "2. `session.run('RETURN \"Neo4j connection OK\" AS message')` — simplest possible query.",
        "3. `driver.close()` — release resources.",
        "",
        "**Expected output:**",
        "",
        "```text",
        "Neo4j connection OK",
        "Connectivity check passed.",
        "```",
        "",
        "> **Troubleshooting:** See **`NEO4J_SETUP.md`** — Docker container not running, Aura URI typo,",
        "> or empty `NEO4J_PASSWORD` in `.env`. Aura requires `neo4j+s://`; local Docker uses `neo4j://`.",
    )
)

cells.append(
    code(
        "# Step 0c — Verify Neo4j connectivity",
        "from neo4j import GraphDatabase",
        "",
        "if not NEO4J_PASSWORD:",
        "    raise ValueError(",
        "        'NEO4J_PASSWORD is empty. Set it in Module_8/.env (see NEO4J_SETUP.md).'",
        "    )",
        "",
        "driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))",
        "with driver.session(database=NEO4J_DATABASE) as session:",
        "    record = session.run('RETURN \"Neo4j connection OK\" AS message').single()",
        "    print(record['message'])",
        "driver.close()",
        "print('Connectivity check passed.')",
    )
)

cells.append(
    md(
        "### Step 0d.1 — Cypher helper",
        "",
        "**What this cell does:** Defines `run_cypher(query, params)` — a reusable wrapper around the Neo4j driver.",
        "",
        "**Why a helper instead of repeating driver code:** Every query in Parts 5–9 would otherwise duplicate",
        "5–6 lines of connection boilerplate. The helper keeps **code cells short** and focuses attention on Cypher.",
        "",
        "**Function behavior:**",
        "",
        "- Opens a driver, runs the query with optional parameters (`$rows`, `$values`, etc.),",
        "- Converts each result record to a Python `dict`,",
        "- Returns a `list[dict]` you can loop over or inspect.",
        "",
        "**Parameterized queries:** Passing `params={'rows': batch}` prevents string-concatenation bugs and injection risks.",
        "Neo4j substitutes `$rows` safely inside Cypher.",
        "",
        "**Expected output:** `run_cypher() ready.`",
    )
)

cells.append(
    code(
        "# Step 0d.1 — Cypher helper",
        "def run_cypher(query: str, params: dict | None = None) -> list[dict]:",
        "    \"\"\"Run a read/write Cypher query and return rows as dicts.\"\"\"",
        "    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as drv:",
        "        with drv.session(database=NEO4J_DATABASE) as session:",
        "            result = session.run(query, params or {})",
        "            return [dict(r) for r in result]",
        "",
        "print('run_cypher() ready.')",
    )
)

cells.append(
    md(
        "### Step 0d.2 — Locate `ollama_model_runner.py`",
        "",
        "**What this cell does:** Finds the path to `ollama_model_runner.py` and imports LangChain base classes.",
        "",
        "**Why a separate runner script:** Module 4/5/8 use the same pattern — the Jupyter kernel calls Ollama via a",
        "subprocess instead of loading the model inside the notebook. That avoids kernel crashes on long generations",
        "and matches **`LLM_MODEL_SETUP.md`**.",
        "",
        "**Search order:**",
        "",
        "1. `Module_8/ollama_model_runner.py` (primary)",
        "2. `Module_4/ollama_model_runner.py` (fallback)",
        "3. Current directory",
        "",
        "**Expected output:** Full path printed after `OLLAMA_RUNNER:`.",
        "",
        "> Skip Steps 0d.2–0d.4 until Part 10 if you only practice Cypher.",
    )
)

cells.append(
    code(
        "# Step 0d.2 — Resolve ollama_model_runner.py",
        "import json",
        "import subprocess",
        "import sys",
        "import tempfile",
        "from typing import Any, List, Optional",
        "",
        "from langchain_core.callbacks import CallbackManagerForLLMRun",
        "from langchain_core.language_models.llms import LLM",
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
        "    raise FileNotFoundError('ollama_model_runner.py not found. See LLM_MODEL_SETUP.md.')",
        "",
        "",
        "OLLAMA_RUNNER = _resolve_ollama_runner_path()",
        "print('OLLAMA_RUNNER:', OLLAMA_RUNNER)",
    )
)

cells.append(
    md(
        "### Step 0d.3 — `call_ollama_runner()` and `OllamaRunnerLLM`",
        "",
        "**What this cell does:** Implements two pieces:",
        "",
        "1. **`call_ollama_runner(prompt)`** — writes the prompt to a temp file, invokes the runner script, parses JSON stdout.",
        "2. **`OllamaRunnerLLM`** — a thin LangChain `LLM` wrapper so `GraphCypherQAChain` can call Ollama the same way it calls OpenAI.",
        "",
        "**Why a temp file for the prompt:** Warehouse questions in Part 10 can be long; passing via `--prompt-file`",
        "avoids shell escaping issues.",
        "",
        "**Error handling:** If Ollama is not running or the model name is wrong, you get a `RuntimeError` with stderr —",
        "check `ollama serve` and `ollama list` per **`LLM_MODEL_SETUP.md`**.",
        "",
        "**Expected output:** `Ollama helpers defined.`",
    )
)

cells.append(
    code(
        "# Step 0d.3 — call_ollama_runner() and OllamaRunnerLLM",
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
        "            raise RuntimeError(f'Runner exit {run.returncode}\\n{run.stderr[:2000]}')",
        "        payload = json.loads(run.stdout)",
        "        first = (payload.get('outputs') or [{}])[0]",
        "        if first.get('status') != 'ok':",
        "            raise RuntimeError(f'Ollama error: {first}')",
        "        return (first.get('response') or '').strip()",
        "    finally:",
        "        Path(path).unlink(missing_ok=True)",
        "",
        "",
        "class OllamaRunnerLLM(LLM):",
        "    model: str = OLLAMA_MODEL",
        "",
        "    @property",
        "    def _llm_type(self) -> str:",
        "        return 'ollama_runner'",
        "",
        "    def _call(",
        "        self, prompt: str, stop: Optional[List[str]] = None,",
        "        run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any,",
        "    ) -> str:",
        "        return call_ollama_runner(prompt, model=self.model)",
        "",
        "print('Ollama helpers defined.')",
    )
)

cells.append(
    md(
        "### Step 0d.4 — Instantiate the LLM object",
        "",
        "**What this cell does:** Creates the `llm` variable used in Part 10's `GraphCypherQAChain`.",
        "",
        "**Branching logic:**",
        "",
        "- `LLM_BACKEND=openai` → requires `OPENAI_API_KEY` in `.env`; uses `ChatOpenAI`.",
        "- `LLM_BACKEND=ollama` → uses `OllamaRunnerLLM()` (no cloud API key).",
        "- Anything else → `llm = None`; Part 10 cells print a skip message.",
        "",
        "**Expected output:**",
        "",
        "```text",
        "LLM ready: Ollama llama3.2:3b via runner",
        "```",
        "",
        "> Run the smoke test in **`LLM_MODEL_SETUP.md`** if Part 10 fails later.",
    )
)

cells.append(
    code(
        "# Step 0d.4 — Instantiate llm for Part 10",
        "if LLM_BACKEND == 'openai':",
        "    if not os.getenv('OPENAI_API_KEY'):",
        "        raise ValueError('OPENAI_API_KEY required when LLM_BACKEND=openai')",
        "    from langchain_openai import ChatOpenAI",
        "    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)",
        "    print(f'LLM ready: OpenAI {OPENAI_MODEL}')",
        "elif LLM_BACKEND == 'ollama':",
        "    llm = OllamaRunnerLLM()",
        "    print(f'LLM ready: Ollama {OLLAMA_MODEL} via runner')",
        "else:",
        "    llm = None",
        "    print('LLM not configured — Part 10 will be skipped unless you set LLM_BACKEND.')",
    )
)

# =============================================================================
# Part 1
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 1 — Why knowledge graphs for warehouse & inventory management",
        "",
        "### The operational problem",
        "",
        "Warehouse managers track:",
        "",
        "- **Inventory levels** (how much stock is on hand)",
        "- **Demand signals** (what customers or downstream sites need)",
        "- **Fulfillment performance** (are orders being completed on time?)",
        "- **Handling equipment** (forklifts, conveyors, dock doors — are they available?)",
        "- **Supplier reliability** (will replenishment arrive as promised?)",
        "- **Risk factors** (weather, congestion, route disruption)",
        "",
        "In a relational database, each topic often lives in a separate table. Answering",
        "*\"Which warehouses are low on stock **and** have constrained equipment **and** high operational risk in the same week?\"*",
        "requires careful joins across fact tables.",
        "",
        "### What a knowledge graph adds",
        "",
        "| Relational pattern | Graph pattern |",
        "|-------------------|---------------|",
        "| `JOIN` across many tables | Traverse typed relationships |",
        "| Implicit links in column names | Explicit edges (`HAS_SNAPSHOT`, `HAS_RISK`) |",
        "| Hard to explain to business users | Visual model in Neo4j Browser |",
        "",
        "### Basic method taught in this course (structured ETL → graph)",
        "",
        "1. **Understand** the CSV columns and business meaning.",
        "2. **Model** entities: `Warehouse`, `InventorySnapshot`, `RiskCategory`, etc.",
        "3. **Transform** tabular rows into nodes and relationships with Python.",
        "4. **Load** into Neo4j with batched Cypher (`UNWIND`).",
        "5. **Query** with Cypher for inventory decisions.",
        "",
        "> This is the most common **production** pattern when you already have operational data in CSV/ERP/WMS exports.",
    )
)

# =============================================================================
# Part 2 — EDA
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 2 — Explore the logistics dataset",
        "",
        "The Kaggle dataset contains **hourly telemetry** from a synthetic supply-chain network.",
        "GPS coordinates represent vehicle/warehouse locations; we cluster them into **warehouse regions**.",
        "",
        "### Columns most relevant to inventory management",
        "",
        "| Column | Inventory / warehouse meaning |",
        "|--------|------------------------------|",
        "| `warehouse_inventory_level` | Stock on hand (units) |",
        "| `historical_demand` | Demand signal for planning |",
        "| `order_fulfillment_status` | Fulfillment rate (0–1) |",
        "| `handling_equipment_availability` | Equipment availability (0–1) |",
        "| `loading_unloading_time` | Dock activity duration |",
        "| `supplier_reliability_score` | Supplier dependability (0–1) |",
        "| `risk_classification` | Low / Moderate / High operational risk |",
        "| `vehicle_gps_latitude/longitude` | Location proxy for warehouse region |",
    )
)

cells.append(
    md(
        "### Step 2.1 — Load the CSV",
        "",
        "**What this cell does:** Reads the Kaggle logistics CSV into a pandas DataFrame called `raw_df`.",
        "",
        "**Why pandas first:** Knowledge graphs need **structured records** before Neo4j. pandas is the teaching-friendly",
        "layer for filtering, aggregation, and derived columns. Production pipelines might use dbt, Spark, or ETL tools —",
        "the graph modeling steps are the same.",
        "",
        "**Key operations:**",
        "",
        "- `parse_dates=['timestamp']` — enables weekly grouping in Part 4.",
        "- `raw_df.head(3)` — preview first rows; Jupyter displays the table below the cell.",
        "",
        "**Expected output:** Row count (~32,065) and column count (26). A 3-row table preview.",
        "",
        "> **Troubleshooting:** `FileNotFoundError` means the CSV is not at `DATA_PATH`. Download per `data/DATASETS.md`.",
    )
)

cells.append(
    code(
        "# Step 2.1 — Load CSV into pandas",
        "import pandas as pd",
        "",
        "if not DATA_PATH.exists():",
        "    raise FileNotFoundError(",
        "        f'Missing dataset: {DATA_PATH}. Download from Kaggle into data/logistics-supply-chain/.'",
        "    )",
        "",
        "raw_df = pd.read_csv(DATA_PATH, parse_dates=['timestamp'])",
        "print('Rows:', len(raw_df))",
        "print('Columns:', len(raw_df.columns))",
        "raw_df.head(3)",
    )
)

cells.append(
    md(
        "### Step 2.2 — Inspect inventory-related columns",
        "",
        "**What this cell does:** Computes descriptive statistics (`count`, `mean`, `min`, `max`, `std`) for columns",
        "that map to warehouse and inventory management concepts.",
        "",
        "**How to read the table:**",
        "",
        "| Column | What to notice |",
        "|--------|----------------|",
        "| `warehouse_inventory_level` | Typical range 0–1000; drives stock status labels later |",
        "| `historical_demand` | Often larger than inventory — expect positive `demand_gap` in Part 7 |",
        "| `order_fulfillment_status` | 0–1 scale; values near 1 mean strong fulfillment |",
        "| `handling_equipment_availability` | 0–1 scale; low values trigger equipment alerts in Part 8 |",
        "| `supplier_reliability_score` | 0–1 scale; bucketed into Low/Medium/High tiers |",
        "",
        "**Why not load all 26 columns now:** Beginners focus on the inventory story first. Other columns",
        "(`port_congestion_level`, `iot_temperature`) are still stored on snapshot nodes for extension exercises.",
        "",
        "**Expected output:** A styled `describe()` table with one row per statistic.",
    )
)

cells.append(
    code(
        "# Step 2.2 — Summary statistics for warehouse signals",
        "inventory_cols = [",
        "    'warehouse_inventory_level',",
        "    'historical_demand',",
        "    'order_fulfillment_status',",
        "    'handling_equipment_availability',",
        "    'supplier_reliability_score',",
        "    'loading_unloading_time',",
        "]",
        "raw_df[inventory_cols].describe().round(2)",
    )
)

cells.append(
    md(
        "### Step 2.3 — Risk distribution",
        "",
        "**What this cell does:** Counts how many hourly rows fall into each `risk_classification` bucket.",
        "",
        "**Business meaning:** Risk is a composite signal in the synthetic dataset (traffic, weather, disruption, etc.).",
        "For warehouse planners, **High Risk** weeks correlate with harder replenishment and fulfillment.",
        "",
        "**Graph modeling choice:** Instead of storing risk only as a string property on every snapshot, we create",
        "**shared `RiskCategory` nodes** (`Low Risk`, `Moderate Risk`, `High Risk`). Many snapshots link to the same",
        "node via `[:HAS_RISK]`. That enables queries like *\"count all High Risk snapshots across warehouses\"*",
        "without scanning duplicate strings.",
        "",
        "**Expected output:** `High Risk` typically dominates (~75% of rows). Exact counts may vary slightly by pandas version.",
    )
)

cells.append(
    code(
        "# Step 2.3 — Risk classification counts",
        "risk_counts = raw_df['risk_classification'].value_counts()",
        "print(risk_counts.to_string())",
    )
)

cells.append(
    md(
        "### Step 2.4 — Derive warehouse regions from GPS",
        "",
        "**What this cell does:** Creates a synthetic `warehouse_id` by rounding GPS coordinates to whole degrees.",
        "",
        "**Why this hack exists:** Real WMS/ERP exports include `warehouse_code`. This Kaggle file only has",
        "`vehicle_gps_latitude` / `vehicle_gps_longitude` as a location proxy. Binning lat/lon is a **teaching",
        "substitute** for facility master data.",
        "",
        "**ID format:** `WH_40.0_-77.0` means \"region centered near 40°N, 77°W\".",
        "",
        "**Trade-offs:**",
        "",
        "| Approach | Pros | Cons |",
        "|----------|------|------|",
        "| Integer-degree bins (this lab) | Simple, fast, few regions | Coarse geography |",
        "| Finer bins (0.1°) | More precision | ~22k regions — too large for beginners |",
        "| Real warehouse master | Production-accurate | Requires internal data |",
        "",
        "We keep the **top 15 busiest** regions in Part 4 so the Neo4j graph stays classroom-sized.",
        "",
        "**Expected output:** Thousands of distinct regions in full data; top regions show hundreds of hourly readings each.",
    )
)

cells.append(
    code(
        "# Step 2.4 — Create warehouse region IDs",
        "raw_df['warehouse_id'] = (",
        "    'WH_'",
        "    + raw_df['vehicle_gps_latitude'].round(0).astype(str)",
        "    + '_'",
        "    + raw_df['vehicle_gps_longitude'].round(0).astype(str)",
        ")",
        "print('Distinct warehouse regions (all data):', raw_df['warehouse_id'].nunique())",
        "print('Top 5 busiest regions:')",
        "print(raw_df['warehouse_id'].value_counts().head())",
    )
)

# =============================================================================
# Part 3 — Model
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 3 — Design the warehouse inventory graph model",
        "",
        "## 3.1 Entity-relationship sketch",
        "",
        "```text",
        "(Warehouse)-[:HAS_SNAPSHOT]->(InventorySnapshot)",
        "(InventorySnapshot)-[:IN_WEEK]->(TimeWeek)",
        "(InventorySnapshot)-[:HAS_RISK]->(RiskCategory)",
        "(InventorySnapshot)-[:HAS_INVENTORY_STATUS]->(InventoryStatus)",
        "(InventorySnapshot)-[:HAS_SUPPLIER_TIER]->(SupplierTier)",
        "(InventorySnapshot)-[:HAS_EQUIPMENT_STATUS]->(EquipmentStatus)",
        "(InventorySnapshot)-[:HAS_FULFILLMENT_STATUS]->(FulfillmentStatus)",
        "```",
        "",
        "## 3.2 Node labels",
        "",
        "| Label | Role |",
        "|-------|------|",
        "| `Warehouse` | Geographic inventory hub (clustered from GPS) |",
        "| `InventorySnapshot` | Weekly aggregated operational reading |",
        "| `TimeWeek` | Calendar week bucket |",
        "| `RiskCategory` | Low / Moderate / High risk (shared reference) |",
        "| `InventoryStatus` | Critical / Low / Balanced / Overstock |",
        "| `SupplierTier` | Low / Medium / High supplier reliability |",
        "| `EquipmentStatus` | Critical / Constrained / Available equipment |",
        "| `FulfillmentStatus` | Behind / AtRisk / OnTrack fulfillment |",
        "| **`WarehouseInventoryLab`** | Marker on **every** lab node (isolation from other graphs) |",
        "",
        "## 3.3 Isolation from other Module 8 graphs",
        "",
        "All nodes include `WarehouseInventoryLab`. To wipe only this course:",
        "",
        "```cypher",
        "MATCH (n:WarehouseInventoryLab) DETACH DELETE n;",
        "```",
        "",
        "Other course labels (`CourseKG`, `KGApplicationsLab`, `LangChainLab`, `LlamaIndexLab`) are untouched.",
        "",
        "## 3.4 Design principles (read before Part 4)",
        "",
        "1. **Snapshots as facts** — Each `InventorySnapshot` is one warehouse-week observation (like a fact table row).",
        "2. **Categories as dimensions** — Status nodes (`InventoryStatus`, `RiskCategory`, …) act like dimension tables in a star schema, but as **first-class graph nodes**.",
        "3. **Explicit time** — `TimeWeek` nodes let you query *\"same week across warehouses\"* without parsing strings everywhere.",
        "4. **Properties + relationships** — Numeric metrics stay on snapshots; categorical labels become traversable edges.",
    )
)

# =============================================================================
# Part 4 — Transform
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 4 — Transform tabular data into graph records",
        "",
        "Part 4 is the **ETL bridge** between pandas and Neo4j. Read each markdown cell before running the code below it.",
        "",
        "### Overall strategy",
        "",
        "1. Keep the **top N busiest** warehouse regions (`LAB_TOP_WAREHOUSES`, default 15).",
        "2. Aggregate hourly rows to **weekly** snapshots (mean for numeric fields, mode for risk).",
        "3. Classify continuous values into **business categories** (inventory status, equipment status, etc.).",
        "4. Produce Python dictionaries ready for Neo4j `UNWIND` loading in Part 5.",
        "",
        "**Output of Part 4:** Two lists — `warehouse_records` (~15 dicts) and `snapshot_records` (~2,000 dicts).",
    )
)

cells.append(
    md(
        "### Step 4.1 — Classification helper functions",
        "",
        "**What this cell does:** Defines Python functions that turn continuous measurements into **business categories**",
        "used as graph node IDs.",
        "",
        "**Why classify at all:** Cypher queries in Parts 6–9 filter on labels like `Critical` or `High Risk`.",
        "Bucket functions mirror how operations teams think — planners rarely ask for *\"inventory < 137.2\"*;",
        "they ask for *\"critical stock\"*.",
        "",
        "**Threshold reference (this lab):**",
        "",
        "| Function | Input | Output buckets |",
        "|----------|-------|----------------|",
        "| `classify_inventory_status` | `inventory_level` | Critical (<100), Low (<250), Balanced (<600), Overstock |",
        "| `classify_supplier_tier` | `supplier_score` 0–1 | Low / Medium / High |",
        "| `classify_equipment_status` | `equipment_availability` 0–1 | Critical / Constrained / Available |",
        "| `classify_fulfillment_status` | `fulfillment_rate` 0–1 | Behind / AtRisk / OnTrack |",
        "",
        "> **Production note:** Thresholds should come from SLAs and ABC analysis — adjust these functions for your org.",
        "",
        "**Expected output:** `Classification helpers ready.`",
    )
)

cells.append(
    code(
        "# Step 4.1 — Business classification helpers",
        "def classify_inventory_status(level: float) -> str:",
        "    if level < 100:",
        "        return 'Critical'",
        "    if level < 250:",
        "        return 'Low'",
        "    if level < 600:",
        "        return 'Balanced'",
        "    return 'Overstock'",
        "",
        "",
        "def classify_supplier_tier(score: float) -> str:",
        "    if score >= 0.67:",
        "        return 'High'",
        "    if score >= 0.33:",
        "        return 'Medium'",
        "    return 'Low'",
        "",
        "",
        "def classify_equipment_status(availability: float) -> str:",
        "    if availability >= 0.6:",
        "        return 'Available'",
        "    if availability >= 0.3:",
        "        return 'Constrained'",
        "    return 'Critical'",
        "",
        "",
        "def classify_fulfillment_status(rate: float) -> str:",
        "    if rate >= 0.75:",
        "        return 'OnTrack'",
        "    if rate >= 0.5:",
        "        return 'AtRisk'",
        "    return 'Behind'",
        "",
        "print('Classification helpers ready.')",
    )
)

cells.append(
    md(
        "### Step 4.2 — Filter top warehouses and aggregate by week",
        "",
        "**What this cell does:**",
        "",
        "1. Selects the **top `LAB_TOP_WAREHOUSES`** regions by row count (busiest locations in the CSV).",
        "2. Adds a `week` column using pandas `Period('W')` — ISO-style week buckets.",
        "3. `groupby(['warehouse_id', 'week']).agg(...)` collapses hourly noise into **one row per warehouse per week**.",
        "",
        "**Aggregation choices:**",
        "",
        "| Field | Aggregation | Reason |",
        "|-------|-------------|--------|",
        "| Numeric metrics | `mean` | Smooth hourly spikes into weekly representative value |",
        "| `risk_classification` | `mode` (most frequent) | Pick dominant risk label for that week |",
        "",
        "**Why weekly not hourly:** ~32k hourly rows → ~2k weekly rows for 15 warehouses — faster Neo4j load,",
        "easier Browser visualization, still enough signal for teaching queries.",
        "",
        "**Expected output:**",
        "",
        "```text",
        "Warehouses modeled: 15",
        "Weekly snapshots: ~1995",
        "```",
        "",
        "Plus a 3-row preview of `weekly_df`.",
    )
)

cells.append(
    code(
        "# Step 4.2 — Weekly aggregation for top warehouse regions",
        "top_wh_ids = (",
        "    raw_df['warehouse_id'].value_counts().head(LAB_TOP_WAREHOUSES).index.tolist()",
        ")",
        "wh_df = raw_df[raw_df['warehouse_id'].isin(top_wh_ids)].copy()",
        "wh_df['week'] = wh_df['timestamp'].dt.to_period('W').astype(str)",
        "",
        "weekly_df = (",
        "    wh_df.groupby(['warehouse_id', 'week'])",
        "    .agg(",
        "        latitude=('vehicle_gps_latitude', 'mean'),",
        "        longitude=('vehicle_gps_longitude', 'mean'),",
        "        inventory_level=('warehouse_inventory_level', 'mean'),",
        "        demand=('historical_demand', 'mean'),",
        "        fulfillment_rate=('order_fulfillment_status', 'mean'),",
        "        equipment_availability=('handling_equipment_availability', 'mean'),",
        "        loading_time=('loading_unloading_time', 'mean'),",
        "        lead_time_days=('lead_time_days', 'mean'),",
        "        supplier_score=('supplier_reliability_score', 'mean'),",
        "        port_congestion=('port_congestion_level', 'mean'),",
        "        iot_temperature=('iot_temperature', 'mean'),",
        "        cargo_condition=('cargo_condition_status', 'mean'),",
        "        risk=('risk_classification', lambda s: s.mode().iloc[0]),",
        "    )",
        "    .reset_index()",
        ")",
        "",
        "print('Warehouses modeled:', weekly_df['warehouse_id'].nunique())",
        "print('Weekly snapshots:', len(weekly_df))",
        "weekly_df.head(3)",
    )
)

cells.append(
    md(
        "### Step 4.3 — Attach graph categories to each snapshot",
        "",
        "**What this cell does:** Finishes ETL by adding:",
        "",
        "- `snapshot_id` — unique key `WH_...__2021-01-01/...` for each warehouse-week.",
        "- Category columns — `inventory_status`, `supplier_tier`, `equipment_status`, `fulfillment_status`.",
        "- `demand_gap` — `demand - inventory_level`; positive ⇒ demand exceeds on-hand stock.",
        "",
        "**Two export structures:**",
        "",
        "| Variable | Contents | Used in Part 5 step |",
        "|----------|----------|---------------------|",
        "| `warehouse_records` | One dict per warehouse (`warehouse_id`, lat, lon) | Step 5.3 |",
        "| `snapshot_records` | One dict per warehouse-week with all metrics + categories | Step 5.4 |",
        "",
        "`to_dict(orient='records')` converts DataFrames to lists of dicts — the format Neo4j's Python driver",
        "expects when you pass `$rows` to Cypher.",
        "",
        "**Expected output:** Counts for snapshots and warehouses; 5-row preview with status and `demand_gap`.",
    )
)

cells.append(
    code(
        "# Step 4.3 — Build graph-ready snapshot records",
        "weekly_df['snapshot_id'] = weekly_df['warehouse_id'] + '__' + weekly_df['week']",
        "weekly_df['inventory_status'] = weekly_df['inventory_level'].map(classify_inventory_status)",
        "weekly_df['supplier_tier'] = weekly_df['supplier_score'].map(classify_supplier_tier)",
        "weekly_df['equipment_status'] = weekly_df['equipment_availability'].map(classify_equipment_status)",
        "weekly_df['fulfillment_status'] = weekly_df['fulfillment_rate'].map(classify_fulfillment_status)",
        "weekly_df['demand_gap'] = weekly_df['demand'] - weekly_df['inventory_level']",
        "",
        "snapshot_records = weekly_df.to_dict(orient='records')",
        "warehouse_records = (",
        "    weekly_df.groupby('warehouse_id')",
        "    .agg(latitude=('latitude', 'mean'), longitude=('longitude', 'mean'))",
        "    .reset_index()",
        "    .to_dict(orient='records')",
        ")",
        "",
        "print('Snapshot records:', len(snapshot_records))",
        "print('Warehouse nodes:', len(warehouse_records))",
        "weekly_df[['warehouse_id', 'week', 'inventory_status', 'risk', 'demand_gap']].head(5)",
    )
)

# =============================================================================
# Part 5 — Load
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 5 — Load the warehouse inventory graph into Neo4j",
        "",
        "We load in four stages:",
        "",
        "1. Clear previous `WarehouseInventoryLab` data.",
        "2. Create **reference category** nodes (risk, inventory status, etc.).",
        "3. Create **warehouse** nodes.",
        "4. Batch-load **weekly snapshots** and relationships.",
        "",
        "**Read before each code cell below.** Steps 5.1–5.4 must run in order. Step 5.5 verifies success.",
        "Step 5.6 is a Browser exercise (no Python).",
    )
)

cells.append(
    md(
        "### Step 5.1 — Clear previous lab subgraph",
        "",
        "**What this cell does:** Deletes **all** nodes (and their relationships) that carry the `WarehouseInventoryLab` label.",
        "",
        "**Why delete first:** Re-running Part 5 without clearing would **duplicate** snapshots and inflate counts.",
        "This pattern is standard in course notebooks — wipe lab data, then rebuild.",
        "",
        "**Safety:** The query is `MATCH (n:WarehouseInventoryLab) DETACH DELETE n`.",
        "",
        "- `DETACH DELETE` removes relationships **and** nodes.",
        "- Nodes without `WarehouseInventoryLab` (from other notebooks) are **not matched**.",
        "",
        "**Expected output:** `Cleared prior WarehouseInventoryLab data.`",
        "",
        "> **Warning:** This destroys only this lab's graph. Do not change the label to a broad name like `:Node`.",
    )
)

cells.append(
    code(
        f"# Step 5.1 — Clear prior lab data",
        f"run_cypher(f'MATCH (n:{{LAB_LABEL}}) DETACH DELETE n')".replace("{LAB_LABEL}", LAB),
        "print('Cleared prior WarehouseInventoryLab data.')",
    )
)

cells.append(
    md(
        "### Step 5.2 — Create reference category nodes",
        "",
        "**What this cell does:** Creates **dimension-style** nodes for categorical values before loading snapshots.",
        "",
        "**Why load categories first:** Step 5.4 uses `MATCH (risk:RiskCategory ... {id: row.risk})` — those nodes must exist.",
        "Creating references upfront also guarantees consistent spelling (`High Risk` vs `high risk`).",
        "",
        "**`MERGE` vs `CREATE`:** `MERGE` means *create if missing, otherwise reuse* — safe if you re-run Step 5.2 alone.",
        "",
        "**Node types created:**",
        "",
        "- `RiskCategory` (3 values)",
        "- `InventoryStatus` (4 values)",
        "- `SupplierTier`, `EquipmentStatus`, `FulfillmentStatus` (3 values each)",
        "",
        "Each node gets labels `:RiskCategory:WarehouseInventoryLab` (for example) plus property `id` and `name`.",
        "",
        "**Expected output:** `Reference categories created.`",
    )
)

cells.append(
    code(
        "# Step 5.2 — Reference nodes (shared categories)",
        "reference_specs = [",
        "    ('RiskCategory', ['Low Risk', 'Moderate Risk', 'High Risk']),",
        "    ('InventoryStatus', ['Critical', 'Low', 'Balanced', 'Overstock']),",
        "    ('SupplierTier', ['Low', 'Medium', 'High']),",
        "    ('EquipmentStatus', ['Critical', 'Constrained', 'Available']),",
        "    ('FulfillmentStatus', ['Behind', 'AtRisk', 'OnTrack']),",
        "]",
        "for label, values in reference_specs:",
        "    run_cypher(",
        "        f'''",
        "        UNWIND $values AS name",
        f"        MERGE (n:{{label}}:{LAB} {{{{id: name}}}})",
        "        SET n.name = name",
        "        '''",
        "        , {'values': values},",
        "    )",
        "print('Reference categories created.')",
    )
)

cells.append(
    md(
        "### Step 5.3 — Create warehouse nodes",
        "",
        "**What this cell does:** Loads one `Warehouse` node per entry in `warehouse_records` using `UNWIND $rows`.",
        "",
        "**Properties stored:**",
        "",
        "| Property | Meaning |",
        "|----------|---------|",
        "| `id` | Same as `warehouse_id` from ETL (e.g. `WH_30.0_-70.0`) |",
        "| `latitude`, `longitude` | Mean GPS for that region — useful for map overlays later |",
        "| `region_label` | Duplicate of `id` for readable Browser captions |",
        "",
        "**`UNWIND` pattern:** Cypher iterates the Python list in one transaction — faster than 15 separate queries.",
        "",
        "**Expected output:** `Loaded 15 warehouse nodes.` (or your `LAB_TOP_WAREHOUSES` value).",
    )
)

cells.append(
    code(
        "# Step 5.3 — Warehouse nodes",
        "run_cypher(",
        "    '''",
        "    UNWIND $rows AS row",
        f"    MERGE (w:Warehouse:{LAB} {{id: row.warehouse_id}})",
        "    SET w.latitude = row.latitude,",
        "        w.longitude = row.longitude,",
        "        w.region_label = row.warehouse_id",
        "    '''",
        "    , {'rows': warehouse_records},",
        ")",
        "print(f'Loaded {len(warehouse_records)} warehouse nodes.')",
    )
)

cells.append(
    md(
        "### Step 5.4 — Batch-load inventory snapshots",
        "",
        "**What this cell does:** Loads all `snapshot_records` in batches of `LAB_BATCH_SIZE` (default 100).",
        "For each row it creates an `InventorySnapshot` node and **six relationships**.",
        "",
        "**Per-row graph pattern created:**",
        "",
        "```text",
        "(Warehouse)-[:HAS_SNAPSHOT]->(InventorySnapshot)-[:IN_WEEK]->(TimeWeek)",
        "(InventorySnapshot)-[:HAS_RISK]->(RiskCategory)",
        "(InventorySnapshot)-[:HAS_INVENTORY_STATUS]->(InventoryStatus)",
        "(InventorySnapshot)-[:HAS_SUPPLIER_TIER]->(SupplierTier)",
        "(InventorySnapshot)-[:HAS_EQUIPMENT_STATUS]->(EquipmentStatus)",
        "(InventorySnapshot)-[:HAS_FULFILLMENT_STATUS]->(FulfillmentStatus)",
        "```",
        "",
        "**Why batch:** ~2,000 snapshots in one query can timeout on slow instances; 20 batches of 100 is gentler.",
        "",
        "**`MERGE` on `TimeWeek`:** Multiple warehouses share the same calendar week — one `TimeWeek` node per week string.",
        "",
        "**Runtime:** Expect 30 seconds to a few minutes depending on Neo4j deployment (Aura vs local Docker).",
        "",
        "**Expected output:** `Loaded 1995 inventory snapshots.` (approximate).",
    )
)

cells.append(
    code(
        "# Step 5.4 — Load snapshots in batches",
        "LOAD_SNAPSHOT_CYPHER = '''",
        "UNWIND $rows AS row",
        f"MATCH (w:Warehouse:{LAB} {{id: row.warehouse_id}})",
        f"MERGE (tw:TimeWeek:{LAB} {{id: row.week}})",
        "SET tw.week = row.week",
        f"CREATE (s:InventorySnapshot:{LAB} {{",
        "    id: row.snapshot_id,",
        "    week: row.week,",
        "    inventory_level: row.inventory_level,",
        "    demand: row.demand,",
        "    demand_gap: row.demand_gap,",
        "    fulfillment_rate: row.fulfillment_rate,",
        "    equipment_availability: row.equipment_availability,",
        "    loading_time: row.loading_time,",
        "    lead_time_days: row.lead_time_days,",
        "    supplier_score: row.supplier_score,",
        "    port_congestion: row.port_congestion,",
        "    iot_temperature: row.iot_temperature,",
        "    cargo_condition: row.cargo_condition",
        "})",
        "CREATE (w)-[:HAS_SNAPSHOT]->(s)",
        "CREATE (s)-[:IN_WEEK]->(tw)",
        "WITH s, row",
        f"MATCH (risk:RiskCategory:{LAB} {{id: row.risk}})",
        f"MATCH (inv:InventoryStatus:{LAB} {{id: row.inventory_status}})",
        f"MATCH (sup:SupplierTier:{LAB} {{id: row.supplier_tier}})",
        f"MATCH (eq:EquipmentStatus:{LAB} {{id: row.equipment_status}})",
        f"MATCH (ful:FulfillmentStatus:{LAB} {{id: row.fulfillment_status}})",
        "CREATE (s)-[:HAS_RISK]->(risk)",
        "CREATE (s)-[:HAS_INVENTORY_STATUS]->(inv)",
        "CREATE (s)-[:HAS_SUPPLIER_TIER]->(sup)",
        "CREATE (s)-[:HAS_EQUIPMENT_STATUS]->(eq)",
        "CREATE (s)-[:HAS_FULFILLMENT_STATUS]->(ful)",
        "'''",
        "",
        "for start in range(0, len(snapshot_records), LAB_BATCH_SIZE):",
        "    batch = snapshot_records[start : start + LAB_BATCH_SIZE]",
        "    run_cypher(LOAD_SNAPSHOT_CYPHER, {'rows': batch})",
        "",
        "print(f'Loaded {len(snapshot_records)} inventory snapshots.')",
    )
)

cells.append(
    md(
        "#### After Step 5.4 — What just happened?",
        "",
        "You loaded roughly **two thousand** `InventorySnapshot` nodes, each wired to:",
        "",
        "- one `Warehouse` (parent site),",
        "- one `TimeWeek` (shared calendar bucket),",
        "- five category nodes (risk, inventory, supplier, equipment, fulfillment).",
        "",
        "If the cell finished without exception but Part 6 returns empty results, run Step 5.5 next —",
        "counts should show `InventorySnapshot` in the thousands.",
    )
)

cells.append(
    md(
        "### Step 5.5 — Verify graph counts",
        "",
        "**What this cell does:** Groups all `WarehouseInventoryLab` nodes by their *primary* label and prints counts.",
        "",
        "**How to interpret results:**",
        "",
        "| node_type | Approximate count | Sanity check |",
        "|-----------|-------------------|--------------|",
        "| `InventorySnapshot` | ~1,995 | Largest count — one per warehouse-week |",
        "| `TimeWeek` | ~hundreds | Smaller — weeks shared across warehouses |",
        "| `Warehouse` | 15 | Matches `LAB_TOP_WAREHOUSES` |",
        "| `RiskCategory`, etc. | 3–4 each | Small fixed reference sets |",
        "",
        "If `InventorySnapshot` is 0, re-run Steps 5.1–5.4 and check for Cypher errors above.",
        "",
        "**Expected output:** A printed list of label → count pairs.",
    )
)

cells.append(
    code(
        "# Step 5.5 — Graph summary",
        "summary = run_cypher(",
        "    f'''",
        f"    MATCH (n:{LAB})",
        f"    RETURN [lbl IN labels(n) WHERE lbl <> '{LAB}'][0] AS node_type, count(*) AS cnt",
        "    ORDER BY cnt DESC",
        "    '''",
        ")",
        "for row in summary:",
        "    print(f\"{row['node_type']}: {row['cnt']}\")",
    )
)

cells.append(
    md(
        "### Step 5.6 — Visualize in Neo4j Browser",
        "",
        "Open Neo4j Browser and run:",
        "",
        "```cypher",
        "MATCH (w:Warehouse:WarehouseInventoryLab)-[:HAS_SNAPSHOT]->(s)-[:HAS_INVENTORY_STATUS]->(st)",
        "RETURN w, s, st LIMIT 50;",
        "```",
        "",
        "You should see warehouses connected to weekly snapshots and inventory status categories.",
        "",
        "**How to use Neo4j Browser:**",
        "",
        "1. Open [http://localhost:7474](http://localhost:7474) (Docker) or your Aura **Query** link.",
        "2. Paste the Cypher above and click **Run**.",
        "3. Switch to the **graph** view (not table) to see nodes and edges.",
        "4. Click a `Warehouse` node — inspect `latitude`, `longitude`, `id` in the side panel.",
        "",
        "This visual check builds intuition before writing more Cypher in Parts 6–9.",
    )
)

# =============================================================================
# Part 6 — Low stock
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 6 — Application: Discover critically low inventory",
        "",
        "**Business question:** *Which warehouse regions had critically low stock, and when?*",
        "",
        "Traverse from `Warehouse` → `InventorySnapshot` → `InventoryStatus` where status is `Critical` or `Low`.",
        "",
        "**Graph pattern used in Part 6:**",
        "",
        "```cypher",
        "(w:Warehouse)-[:HAS_SNAPSHOT]->(s:InventorySnapshot)-[:HAS_INVENTORY_STATUS]->(st:InventoryStatus)",
        "```",
        "",
        "This is a **two-hop traversal** from facility to status category — the same pattern as traversing",
        "`Store → Order → ProductCategory` in retail graphs.",
    )
)

cells.append(
    md(
        "### Step 6.1 — Critical inventory snapshots",
        "",
        "**What this cell does:** Lists warehouse-weeks where `InventoryStatus.id = 'Critical'` (inventory < 100 units",
        "after weekly averaging).",
        "",
        "**Cypher walkthrough:**",
        "",
        "1. `MATCH` the warehouse → snapshot → status chain.",
        "2. `WHERE st.id = 'Critical'` filters to critically low stock only.",
        "3. `ORDER BY s.inventory_level ASC` shows the most severe cases first.",
        "4. `LIMIT 15` keeps output readable in the notebook.",
        "",
        "**Operational action:** These rows are candidates for **emergency replenishment** or **transfer from another DC**.",
        "",
        "**Expected output:** Lines like `WH_30.0_-70.0 | week 2023-05-09 | inventory=42.3`.",
    )
)

cells.append(
    code(
        f"# Step 6.1 — Warehouses with critical inventory",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (w:Warehouse:{{LAB_LABEL}})-[:HAS_SNAPSHOT]->(s:InventorySnapshot:{{LAB_LABEL}})",
        f"          -[:HAS_INVENTORY_STATUS]->(st:InventoryStatus:{{LAB_LABEL}})",
        f"    WHERE st.id = 'Critical'",
        f"    RETURN w.id AS warehouse, s.week AS week, round(s.inventory_level, 1) AS inventory_level",
        f"    ORDER BY s.inventory_level ASC",
        f"    LIMIT 15",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['warehouse']} | week {r['week']} | inventory={r['inventory_level']}\")",
    )
)

cells.append(
    md(
        "### Step 6.2 — Count low-stock weeks per warehouse",
        "",
        "**What this cell does:** Aggregates **how often** each warehouse was in `Critical` or `Low` status across all weeks.",
        "",
        "**Why aggregation matters:** Step 6.1 shows individual bad weeks; this step ranks **chronic** problem sites.",
        "A warehouse with 40 stressed weeks needs structural fixes (safety stock, supplier change), not a one-off shipment.",
        "",
        "**Cypher concept:** `count(s)` counts matching snapshots per `w.id` after `RETURN w.id AS warehouse, count(s)`.",
        "",
        "**Expected output:** Top warehouses with the highest `stressed_weeks` integer.",
    )
)

cells.append(
    code(
        f"# Step 6.2 — Warehouses with the most low/critical weeks",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (w:Warehouse:{{LAB_LABEL}})-[:HAS_SNAPSHOT]->(s)-[:HAS_INVENTORY_STATUS]->(st)",
        f"    WHERE st.id IN ['Critical', 'Low']",
        f"    RETURN w.id AS warehouse, count(s) AS stressed_weeks",
        f"    ORDER BY stressed_weeks DESC",
        f"  LIMIT 10",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['warehouse']}: {r['stressed_weeks']} stressed week(s)\")",
    )
)

# =============================================================================
# Part 7 — Demand gap
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 7 — Application: Demand exceeds inventory",
        "",
        "**Business question:** *Where is historical demand higher than on-hand inventory?*",
        "",
        "The property `demand_gap = demand - inventory_level` was computed during ETL.",
        "Positive values indicate **under-stocked** conditions relative to demand signal.",
        "",
        "**SQL vs graph:** In SQL you might `JOIN warehouse_facts` to itself with filters. Here the snapshot node",
        "already stores `demand_gap` as a property — but you still **traverse** from warehouse to snapshot for regional context.",
    )
)

cells.append(
    md(
        "### Step 7.1 — Top demand gaps",
        "",
        "**What this cell does:** Finds snapshots where `demand_gap > 0` and ranks by largest gap.",
        "",
        "**Reading the columns:**",
        "",
        "- `inventory` — weekly mean on-hand stock.",
        "- `demand` — weekly mean historical demand signal.",
        "- `demand_gap` — how far demand exceeds inventory (same units as the CSV).",
        "",
        "**Business insight:** Large positive gaps suggest **stockout risk** even if status is not yet `Critical`",
        "(classification uses fixed thresholds; demand context adds nuance).",
        "",
        "**Expected output:** 15 lines sorted by descending `demand_gap`.",
    )
)

cells.append(
    code(
        f"# Step 7.1 — Largest demand gaps",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (w:Warehouse:{{LAB_LABEL}})-[:HAS_SNAPSHOT]->(s:InventorySnapshot:{{LAB_LABEL}})",
        f"    WHERE s.demand_gap > 0",
        f"    RETURN w.id AS warehouse, s.week AS week,",
        f"           round(s.inventory_level, 1) AS inventory,",
        f"           round(s.demand, 1) AS demand,",
        f"           round(s.demand_gap, 1) AS demand_gap",
        f"    ORDER BY s.demand_gap DESC",
        f"    LIMIT 15",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(",
        "        f\"{r['warehouse']} | {r['week']} | inv={r['inventory']} demand={r['demand']} gap={r['demand_gap']}\"",
        "    )",
    )
)

cells.append(
    md(
        "### Step 7.2 — Under-stocked and behind on fulfillment",
        "",
        "**What this cell does:** Combines a **numeric filter** (`demand_gap > 500`) with a **relationship filter**",
        "(`FulfillmentStatus.id = 'Behind'`).",
        "",
        "**Why multi-factor:** Inventory alone does not tell the full story — a site can be under-stocked **and**",
        "already failing to fulfill orders (`Behind`). That is a priority queue for operations managers.",
        "",
        "**Cypher pattern:** Single `MATCH` path through `HAS_FULFILLMENT_STATUS`; numeric condition on snapshot property.",
        "",
        "**Adjust the threshold:** Change `500` to match your product unit scale in production data.",
        "",
        "**Expected output:** Warehouse-week pairs with large gap and `Behind` fulfillment.",
    )
)

cells.append(
    code(
        f"# Step 7.2 — Demand gap + poor fulfillment (multi-condition traversal)",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (w:Warehouse:{{LAB_LABEL}})-[:HAS_SNAPSHOT]->(s)",
        f"          -[:HAS_FULFILLMENT_STATUS]->(f:FulfillmentStatus:{{LAB_LABEL}})",
        f"    WHERE s.demand_gap > 500 AND f.id = 'Behind'",
        f"    RETURN w.id AS warehouse, s.week AS week, round(s.demand_gap, 0) AS gap, f.id AS fulfillment",
        f"    ORDER BY gap DESC",
        f"    LIMIT 10",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['warehouse']} | {r['week']} | gap={r['gap']} | {r['fulfillment']}\")",
    )
)

# =============================================================================
# Part 8 — Risk + equipment
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 8 — Application: Risk and equipment bottlenecks",
        "",
        "**Business question:** *Where do high operational risk and constrained equipment overlap?*",
        "",
        "This is a classic **multi-factor** warehouse alert: even adequate stock is hard to move",
        "when equipment availability is low.",
        "",
        "**Real-world analogy:** A warehouse may have pallets in the rack, but if dock doors and forklifts are down,",
        "effective inventory is **trapped** — graph links make that visible in one query.",
    )
)

cells.append(
    md(
        "### Step 8.1 — High risk + critical equipment",
        "",
        "**What this cell does:** Finds snapshots linked to **both** `High Risk` and `Critical` equipment status.",
        "",
        "**Two `MATCH` clauses on the same snapshot:**",
        "",
        "1. First path: `HAS_RISK` → `RiskCategory` where `id = 'High Risk'`.",
        "2. Second path: `HAS_EQUIPMENT_STATUS` → `EquipmentStatus` where `id = 'Critical'`.",
        "",
        "Neo4j binds both to the same `s` node — logical **AND** across relationships.",
        "",
        "**Expected output:** Warehouse-week rows with very low `equipment_availability` (near 0).",
    )
)

cells.append(
    code(
        f"# Step 8.1 — Snapshots with High Risk and Critical equipment",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (w:Warehouse:{{LAB_LABEL}})-[:HAS_SNAPSHOT]->(s)",
        f"          -[:HAS_RISK]->(r:RiskCategory:{{LAB_LABEL}})",
        f"    MATCH (s)-[:HAS_EQUIPMENT_STATUS]->(e:EquipmentStatus:{{LAB_LABEL}})",
        f"    WHERE r.id = 'High Risk' AND e.id = 'Critical'",
        f"    RETURN w.id AS warehouse, s.week AS week,",
        f"           round(s.equipment_availability, 3) AS equipment_availability",
        f"    ORDER BY s.equipment_availability ASC",
        f"    LIMIT 15",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['warehouse']} | {r['week']} | equipment={r['equipment_availability']}\")",
    )
)

cells.append(
    md(
        "### Step 8.2 — Warehouses with recurring equipment stress",
        "",
        "**What this cell does:** Counts weeks where a warehouse had **High Risk** and equipment **Critical or Constrained**.",
        "",
        "**Difference from Step 8.1:** Step 8.1 lists individual weeks; Step 8.2 ranks warehouses by **frequency** —",
        "useful for capital planning (where to invest in new handling equipment).",
        "",
        "**Inline node filter:** `RiskCategory {id: 'High Risk'}` in the `MATCH` reduces rows early — a common Cypher optimization.",
        "",
        "**Expected output:** Warehouses sorted by `alert_weeks` descending.",
    )
)

cells.append(
    code(
        f"# Step 8.2 — Count high-risk + constrained/critical equipment weeks",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (w:Warehouse:{{LAB_LABEL}})-[:HAS_SNAPSHOT]->(s)",
        f"          -[:HAS_RISK]->(r:RiskCategory:{{LAB_LABEL}} {{{{id: 'High Risk'}}}})",
        f"    MATCH (s)-[:HAS_EQUIPMENT_STATUS]->(e:EquipmentStatus:{{LAB_LABEL}})",
        f"    WHERE e.id IN ['Critical', 'Constrained']",
        f"    RETURN w.id AS warehouse, count(s) AS alert_weeks",
        f"    ORDER BY alert_weeks DESC",
        f"    LIMIT 10",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['warehouse']}: {r['alert_weeks']} alert week(s)\")",
    )
)

# =============================================================================
# Part 9 — Supplier
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 9 — Application: Supplier reliability and replenishment risk",
        "",
        "**Business question:** *Which inventory snapshots depend on low-reliability suppliers while stock is already low?*",
        "",
        "Graph traversal links **inventory status** and **supplier tier** on the same snapshot —",
        "a pattern you would extend to real supplier master data in production.",
        "",
        "**Extension idea:** Add `(Supplier)-[:REPLENISHES]->(Warehouse)` nodes from your ERP vendor master.",
    )
)

cells.append(
    md(
        "### Step 9.1 — Low stock with low supplier tier",
        "",
        "**What this cell does:** Finds snapshots that are simultaneously:",
        "",
        "- Low or critical inventory (`InventoryStatus` in `Critical`, `Low`), **and**",
        "- Served by a **Low** supplier tier (`supplier_score` below 0.33 after weekly averaging).",
        "",
        "**Replenishment risk:** These sites are vulnerable — stock is already low and the supplier channel is unreliable.",
        "",
        "**Expected output:** Rows sorted by ascending `supplier_score` (worst suppliers first).",
    )
)

cells.append(
    code(
        f"# Step 9.1 — Critical/Low inventory + Low supplier tier",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (w:Warehouse:{{LAB_LABEL}})-[:HAS_SNAPSHOT]->(s)",
        f"          -[:HAS_INVENTORY_STATUS]->(inv:InventoryStatus:{{LAB_LABEL}})",
        f"    MATCH (s)-[:HAS_SUPPLIER_TIER]->(sup:SupplierTier:{{LAB_LABEL}} {{{{id: 'Low'}}}})",
        f"    WHERE inv.id IN ['Critical', 'Low']",
        f"    RETURN w.id AS warehouse, s.week AS week, inv.id AS inventory_status,",
        f"           round(s.supplier_score, 3) AS supplier_score",
        f"    ORDER BY s.supplier_score ASC",
        f"    LIMIT 15",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(",
        "        f\"{r['warehouse']} | {r['week']} | {r['inventory_status']} | supplier={r['supplier_score']}\"",
        "    )",
    )
)

cells.append(
    md(
        "### Step 9.2 — Supplier tier distribution across warehouses",
        "",
        "**What this cell does:** Counts how many snapshots link to each `SupplierTier` — a **portfolio view** of supplier exposure.",
        "",
        "**Why useful:** If most snapshots are `Low` tier, your network may need supplier development or dual-sourcing.",
        "",
        "**Cypher note:** Aggregation starts from `InventorySnapshot` nodes, not warehouses — each week at each site counts once.",
        "",
        "**Expected output:** Three lines (`High`, `Medium`, `Low`) with snapshot counts.",
    )
)

cells.append(
    code(
        f"# Step 9.2 — Snapshot counts by supplier tier",
        "rows = run_cypher(",
        f"    f'''",
        f"    MATCH (s:InventorySnapshot:{{LAB_LABEL}})-[:HAS_SUPPLIER_TIER]->(sup:SupplierTier:{{LAB_LABEL}})",
        f"    RETURN sup.id AS supplier_tier, count(s) AS snapshots",
        f"    ORDER BY snapshots DESC",
        f"    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['supplier_tier']}: {r['snapshots']} snapshot(s)\")",
    )
)

# =============================================================================
# Part 10 — LLM
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 10 — Application: Natural-language warehouse Q&A",
        "",
        "**Business question:** *Can a planner ask questions in English instead of writing Cypher?*",
        "",
        "We use LangChain **`GraphCypherQAChain`**: question → LLM generates Cypher → execute → summarized answer.",
        "See also `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb` for deeper GraphRAG patterns.",
        "",
        "> **Requires:** `LLM_MODEL_SETUP.md` and working `llm` from Step 0d.",
    )
)

cells.append(
    md(
        "### Step 10.1 — Connect LangChain Neo4jGraph",
        "",
        "**What this cell does:** Wraps your Neo4j database in LangChain's `Neo4jGraph` helper, which **introspects**",
        "node labels, relationship types, and property keys.",
        "",
        "**Why schema introspection:** `GraphCypherQAChain` feeds this schema to the LLM so it can write valid Cypher",
        "(table names become node labels, foreign keys become relationship types).",
        "",
        "**Caveat:** If you have **many** course graphs in one database, the schema may include labels from other labs.",
        "Ask questions that mention **warehouse**, **inventory**, or **WarehouseInventoryLab** concepts for best results.",
        "",
        "**Expected output:** First ~900 characters of the schema text.",
    )
)

cells.append(
    code(
        "# Step 10.1 — Schema-aware Neo4jGraph",
        "from langchain_neo4j import Neo4jGraph",
        "",
        "neo4j_graph = Neo4jGraph(",
        "    url=NEO4J_URI,",
        "    username=NEO4J_USERNAME,",
        "    password=NEO4J_PASSWORD,",
        "    database=NEO4J_DATABASE,",
        ")",
        "neo4j_graph.refresh_schema()",
        "print('Schema snippet (first 900 chars):')",
        "print((neo4j_graph.schema or '')[:900])",
    )
)

cells.append(
    md(
        "### Step 10.2 — GraphCypherQAChain demo",
        "",
        "**What this cell does:** Runs the full **NL → Cypher → execute → NL answer** pipeline once.",
        "",
        "**Pipeline steps (when `verbose=True`):**",
        "",
        "1. Your English question is sent to the LLM with graph schema context.",
        "2. The LLM proposes a Cypher query.",
        "3. Neo4j executes the query.",
        "4. The LLM summarizes results in plain English.",
        "",
        "**Demo question:** Asks for warehouses with **critical inventory** — you already know the answer from Part 6;",
        "use this to verify the LLM path works before trying harder questions.",
        "",
        "**Requirements:** `ollama serve` running, model pulled, `llm` from Step 0d.4.",
        "",
        "**Expected output:** Verbose chain logs plus a natural-language answer listing warehouse ids and weeks.",
    )
)

cells.append(
    code(
        "# Step 10.2 — Natural language → Cypher → answer",
        "from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain",
        "",
        "if llm is None:",
        "    print('Skip: configure LLM_BACKEND in .env (see LLM_MODEL_SETUP.md).')",
        "else:",
        "    chain = GraphCypherQAChain.from_llm(",
        "        llm=llm,",
        "        graph=neo4j_graph,",
        "        verbose=True,",
        "        allow_dangerous_requests=True,",
        "        top_k=10,",
        "    )",
        "    question = (",
        "        'Which warehouses had critical inventory status? List warehouse id and week.'",
        "    )",
        "    answer = chain.invoke({'query': question})",
        "    print('\\nQuestion:', question)",
        "    print('Answer:', answer.get('result', answer))",
    )
)

cells.append(
    md(
        "### Step 10.3 — Try your own questions",
        "",
        "Examples that work well on this lab graph:",
        "",
        "- *How many inventory snapshots have High Risk?*",
        "- *Which warehouses have the most Low supplier tier snapshots?*",
        "- *List weeks where fulfillment status is Behind and inventory status is Critical.*",
        "",
        "**Tips for better LLM answers:**",
        "",
        "- Mention node types: *inventory snapshots*, *warehouses*, *supplier tier*.",
        "- Ask for counts or top-N lists — easier than open-ended summaries.",
        "- If Cypher fails, rephrase with explicit labels from Part 3 (`InventoryStatus`, `EquipmentStatus`).",
    )
)

cells.append(
    md(
        "### Step 10.3 — Run your own question",
        "",
        "**What this cell does:** Invokes the same `chain` with `MY_QUESTION` — **edit the string** to experiment.",
        "",
        "**Default question:** Finds which warehouse has the most **constrained equipment** snapshots —",
        "combines aggregation with equipment status traversal (compare with Part 8).",
        "",
        "**If `llm is None`:** Set `LLM_BACKEND` in `.env` and re-run Steps 0b.3, 0d.2–0d.4.",
    )
)

cells.append(
    code(
        "# Step 10.3 — Your question (edit the string)",
        "MY_QUESTION = 'Which warehouse has the most snapshots with constrained equipment?'",
        "",
        "if llm is not None:",
        "    result = chain.invoke({'query': MY_QUESTION})",
        "    print('Q:', MY_QUESTION)",
        "    print('A:', result.get('result', result))",
        "else:",
        "    print('Configure LLM to run this cell.')",
    )
)

# =============================================================================
# Part 11 — Advanced reading
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 11 — Advanced improvements (self-study reading)",
        "",
        "The **basic method** in this course is: **structured ETL → explicit graph model → Cypher analytics**.",
        "That is the right starting point for warehouse data that already lives in CSV, WMS, or ERP exports.",
        "",
        "Below are **improvement paths** to research on your own. You do not need to implement them to finish this lab.",
        "",
        "## 11.1 Richer domain modeling",
        "",
        "| Improvement | Why | Starting resource |",
        "|-------------|-----|-------------------|",
        "| Real **facility master data** (warehouse IDs, zones, SKUs) | Replace GPS binning with authoritative locations | Your WMS/ERP schema |",
        "| **SKU-level** inventory nodes | Track item granularity, not just regional stock | Neo4j supply-chain modeling guides |",
        "| **Lot / batch** tracking | Expiry, recall, FEFO picking | GS1 standards, cold-chain KG papers |",
        "",
        "## 11.2 LLM-based graph construction",
        "",
        "| Improvement | Why | Module 8 notebook |",
        "|-------------|-----|-----------------|",
        "| Extract entities from **unstructured reports** (incident logs, emails) | Capture what CSVs miss | `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb` |",
        "| **Schema-guided** LLM extraction | Higher precision node types | Same notebook, Section 2.3 |",
        "",
        "## 11.3 GraphRAG and agents",
        "",
        "| Improvement | Why | Module 8 notebook |",
        "|-------------|-----|-----------------|",
        "| **GraphRAG** (vector + graph retrieval) | Answer questions with document evidence | `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb` |",
        "| **Evaluation** with RAGAS | Measure faithfulness of answers | `Module_8_Evaluating_GraphRAG_with_RAGAS.ipynb` |",
        "| **Agent** workflows | Multi-step planning (reorder, reroute) | LangChain / LlamaIndex notebooks |",
        "",
        "## 11.4 Analytics and operations",
        "",
        "| Improvement | Why | Starting resource |",
        "|-------------|-----|-------------------|",
        "| **Neo4j Graph Data Science** (PageRank, Louvain) | Find bottleneck warehouses and communities | [Neo4j GDS docs](https://neo4j.com/docs/graph-data-science/) |",
        "| **Streaming ingestion** (Kafka → Neo4j) | Near-real-time inventory events | Neo4j streaming integrations |",
        "| **Digital twin** linking IoT sensors | Live `iot_temperature`, equipment telemetry | IIoT + knowledge graph literature |",
        "",
        "## 11.5 Data quality and governance",
        "",
        "- **Entity resolution**: merge duplicate warehouse codes across systems (see Part 5 in",
        "  `Module_8_Practical_Knowledge_Graph_Applications.ipynb`).",
        "- **Lineage**: tag snapshots with `source_file`, `loaded_at` for auditability.",
        "- **Role-based access**: Neo4j RBAC for planner vs analyst vs executive views.",
    )
)

# =============================================================================
# Part 12 — Wrap up
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 12 — Wrap-up",
        "",
        "## What you practiced",
        "",
        "| Part | Skill | Business outcome |",
        "|------|-------|------------------|",
        "| 2–4 | pandas ETL + classification | Turn CSV into graph records |",
        "| 5 | Batched Cypher load | Seed an isolated warehouse subgraph |",
        "| 6 | Status traversal | Find low-stock warehouses |",
        "| 7 | Numeric + status filters | Detect demand–inventory mismatches |",
        "| 8 | Multi-factor patterns | Risk + equipment alerts |",
        "| 9 | Supplier linkage | Replenishment risk view |",
        "| 10 | LLM + Cypher | Natural-language inventory Q&A |",
        "",
        "## Map to your organization",
        "",
        "Replace `Warehouse` / `InventorySnapshot` with your entities:",
        "",
        "| Your system | Graph node | Example relationship |",
        "|-------------|------------|----------------------|",
        "| WMS | `Warehouse`, `Zone`, `SKU` | `(Warehouse)-[:STORES]->(SKU)` |",
        "| TMS | `Shipment`, `Carrier` | `(Shipment)-[:ORIGIN]->(Warehouse)` |",
        "| ERP | `PurchaseOrder`, `Supplier` | `(Supplier)-[:REPLENISHES]->(Warehouse)` |",
        "",
        "## Clean up (optional)",
        "",
        "```cypher",
        "MATCH (n:WarehouseInventoryLab) DETACH DELETE n;",
        "```",
        "",
        "## Continue learning",
        "",
        "1. **`Module_8_Practical_Knowledge_Graph_Applications.ipynb`** — more application patterns.",
        "2. **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** — graphs from documents.",
        "3. **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** — GraphRAG and agents.",
        "",
        "---",
        "",
        "*End of course — Enhancing Warehouse and Inventory Management Practices with Knowledge Graphs*",
    )
)

# =============================================================================
# Write notebook
# =============================================================================
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    },
    "cells": cells,
}

out_path = Path(__file__).resolve().parent.parent / "Module_8_Warehouse_Inventory_Management_with_Knowledge_Graphs.ipynb"
out_path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {out_path} ({len(cells)} cells)")
