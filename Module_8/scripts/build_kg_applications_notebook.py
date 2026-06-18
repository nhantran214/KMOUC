#!/usr/bin/env python3
"""Generate Module_8_Practical_Knowledge_Graph_Applications.ipynb."""
import json
from pathlib import Path


def md(*lines: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}


def code(*lines: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "outputs": [], "source": [l + "\n" for l in lines]}


cells: list = []

# =============================================================================
# Title
# =============================================================================
cells.append(
    md(
        "# Practical Knowledge Graph Applications for Real-World Problems",
        "",
        "**Course module:** Module 8",
        "**Audience:** Beginners who understand basic Neo4j, Cypher, and (optionally) LLMs.",
        "",
        "## Course description",
        "",
        "Knowledge graphs are not only a storage format — they power **real applications**",
        "where relationships drive decisions: logistics, compliance, risk, recommendations,",
        "and grounded question answering.",
        "",
        "In this hands-on course you will:",
        "",
        "1. Build a **maritime / supply-chain knowledge graph** in Neo4j.",
        "2. Solve **seven practical problems** with Cypher (and LLM-assisted Q&A where useful).",
        "3. Connect each exercise to a **business question** you might hear in industry.",
        "",
        "> **Language:** All instructional text is in **English**.",
        "",
        "> **Setup (required):** Complete **`NEO4J_SETUP.md`** before running code.",
        "> For LLM sections, complete **`LLM_MODEL_SETUP.md`** and run **`ollama_model_runner.py`**",
        "> (or configure OpenAI).",
        "",
        "### How to use this notebook",
        "",
        "1. Read each **markdown** cell before running the **code** cell below it.",
        "2. Run cells **in order** from Step 0 downward.",
        "3. Lab data uses the label **`KGApplicationsLab`** — safe to delete and re-seed.",
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
        "| Python | Run notebook cells |",
        "| (Optional) LLMs | Part 8 — natural-language business Q&A |",
        "",
        "### Related Module 8 notebooks",
        "",
        "| Notebook | Focus |",
        "|----------|-------|",
        "| `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb` | Extract graphs from text with LLMs |",
        "| `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb` | LangChain RAG / GraphRAG / agents |",
        "| `Module_8_Evaluating_GraphRAG_with_RAGAS.ipynb` | Measure GraphRAG quality |",
        "",
        "**This notebook** focuses on **what you can do** once a graph exists — applications, not framework APIs.",
        "",
        "## Course outline",
        "",
        "| Part | Topic | Real-world problem |",
        "|------|--------|-------------------|",
        "| **0** | Environment & Neo4j connection | — |",
        "| **1** | Application landscape | When graphs beat tables |",
        "| **2** | Build the lab graph | Maritime logistics domain model |",
        "| **3** | Network discovery | *Who operates where?* |",
        "| **4** | Path & impact analysis | *What breaks if a route fails?* |",
        "| **5** | Entity resolution | *Are these two records the same company?* |",
        "| **6** | Recommendations | *Which ports are similar?* |",
        "| **7** | Compliance mapping | *Which rules apply to which carriers?* |",
        "| **8** | Business Q&A (LLM + Cypher) | *Ask questions in plain English* |",
        "| **9** | Graph analytics | *Which hubs matter most?* |",
        "| **10** | Wrap-up | Map exercises to your domain |",
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
        "3. For **Part 8** (LLM Q&A), also complete **`LLM_MODEL_SETUP.md`** and start `ollama serve`.",
        "",
        "### What Step 0 does",
        "",
        "| Step | Purpose |",
        "|------|---------|",
        "| 0a | Install Python packages |",
        "| 0b | Load paths and environment variables |",
        "| 0c | Verify Neo4j Bolt connectivity |",
        "| 0d | (Optional) Wire Ollama runner for Part 8 |",
    )
)

cells.append(
    md(
        "### Step 0a — Install Python packages",
        "",
        "Core packages: Neo4j driver, `python-dotenv`, and LangChain pieces used in Part 8.",
        "Run once per virtual environment.",
    )
)

cells.append(
    code(
        "# Step 0a — Install Python dependencies (run once per environment)",
        "%pip install -q neo4j python-dotenv requests \\",
        "    langchain langchain-community langchain-neo4j langchain-openai",
    )
)

cells.append(
    md(
        "### Step 0b.1 — Resolve the `Module_8` folder",
        "Jupyter may start in the repo root or inside `Module_8`. This cell finds the folder with `.env` and `data/`.",
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
        "### Step 0b.2 — Neo4j connection settings",
        "Values come from `Module_8/.env` (see **`NEO4J_SETUP.md`**).",
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
        "### Step 0b.3 — LLM settings (Part 8 only)",
        "",
        "Parts 1–7 use **Cypher only**. Part 8 adds natural-language Q&A.",
        "",
        "- **`LLM_BACKEND=ollama`** → `ollama_model_runner.py` (recommended)",
        "- **`LLM_BACKEND=openai`** → `ChatOpenAI`",
    )
)

cells.append(
    code(
        "# Step 0b.3 — LLM backend (used in Part 8)",
        "LLM_BACKEND = os.getenv('LLM_BACKEND', 'ollama').lower()",
        "OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')",
        "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')",
        "OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', '0'))",
        "OLLAMA_MAX_TOKENS = int(os.getenv('OLLAMA_MAX_TOKENS', '2048'))",
        "OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')",
        "LAB_LABEL = 'KGApplicationsLab'",
        "print('LLM backend:', LLM_BACKEND)",
        "if LLM_BACKEND == 'ollama':",
        "    print('Ollama host:', OLLAMA_HOST)",
        "    print('Ollama model:', OLLAMA_MODEL)",
    )
)

cells.append(
    md(
        "### Step 0c — Verify Neo4j connectivity",
        "If this fails, return to **`NEO4J_SETUP.md`** troubleshooting.",
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
        "### Step 0d — Neo4j helper and (optional) Ollama runner",
        "",
        "We define a small `run_cypher()` helper used throughout the notebook.",
        "The Ollama runner block is only needed for **Part 8** — skip 0d.2–0d.4 until then if you prefer.",
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
    code(
        "# Step 0d.2 — Resolve ollama_model_runner.py (Part 8)",
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
        "    raise FileNotFoundError(",
        "        'ollama_model_runner.py not found. See LLM_MODEL_SETUP.md.'",
        "    )",
        "",
        "",
        "OLLAMA_RUNNER = _resolve_ollama_runner_path()",
        "print('OLLAMA_RUNNER:', OLLAMA_RUNNER)",
    )
)

cells.append(
    code(
        "# Step 0d.3 — call_ollama_runner() helper",
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
    code(
        "# Step 0d.4 — Instantiate llm for Part 8",
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
        "    print('LLM not configured — Part 8 will be skipped unless you set LLM_BACKEND.')",
    )
)

# =============================================================================
# Part 1
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 1 — Knowledge graph applications in the real world",
        "",
        "Relational databases excel at **rows and joins**. Knowledge graphs excel when:",
        "",
        "- The **shape of connections** is the product (supply chains, org charts, fraud rings).",
        "- You need **multi-hop reasoning** (*supplier → factory → port → canal*).",
        "- Different teams share a **single connected model** (ops, compliance, data science).",
        "",
        "### Application map (this course)",
        "",
        "| Industry | Graph application | Notebook part |",
        "|----------|-------------------|---------------|",
        "| Logistics | Route & hub analysis | 3, 4, 9 |",
        "| Retail | Product recommendations | 6 |",
        "| Finance | Entity resolution, AML paths | 5 |",
        "| Healthcare | Treatment pathways | (same patterns as Part 4) |",
        "| Enterprise | Policy / compliance mapping | 7 |",
        "| GenAI | Grounded business Q&A | 8 |",
        "",
        "### Domain for hands-on labs: maritime & supply chain",
        "",
        "We use **ports, carriers, canals, countries, and regulations** — a realistic slice of",
        "global trade. Data is seeded in Cypher (structured) plus optional text from",
        "`data/dbpedia_maritime_corpus.txt` (see `data/DATASETS.md`).",
    )
)

# =============================================================================
# Part 2 — Build graph
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 2 — Build the application knowledge graph",
        "",
        "## 2.1 Data model",
        "",
        "```text",
        "(Port)-[:LOCATED_IN]->(Country)",
        "(Organization)-[:OPERATES_IN]->(Port)",
        "(Organization)-[:USES_ROUTE]->(Waterway)",
        "(Organization)-[:HEADQUARTERED_IN]->(Country)",
        "(Regulation)-[:ISSUED_BY]->(Agency)",
        "(Organization)-[:SUBJECT_TO]->(Regulation)",
        "(Port)-[:CONNECTED_TO]->(Port)   // trade lanes",
        "```",
        "",
        "Every lab node also has label **`KGApplicationsLab`** so we can wipe and rebuild safely.",
    )
)

cells.append(
    md(
        "### Step 2.1a — Clear previous lab data",
        "Re-running the notebook should not duplicate nodes.",
    )
)

cells.append(
    code(
        "# Step 2.1a — Clear prior lab subgraph",
        "run_cypher(f'MATCH (n:{LAB_LABEL}) DETACH DELETE n')",
        "print('Cleared prior KGApplicationsLab data.')",
    )
)

cells.append(
    md(
        "### Step 2.1b — Create countries and waterways",
        "Start with **reference entities** that other nodes will link to.",
    )
)

cells.append(
    code(
        "# Step 2.1b — Countries and waterways",
        "run_cypher(",
        "    f'''",
        "    CREATE (meta:{LAB_LABEL} {{course: 'Practical KG Applications', module: 'Module_8'}})",
        "    CREATE (nl:Country:{LAB_LABEL} {{id: 'Netherlands', name: 'Netherlands'}})",
        "    CREATE (sg:Country:{LAB_LABEL} {{id: 'Singapore', name: 'Singapore'}})",
        "    CREATE (pa:Country:{LAB_LABEL} {{id: 'Panama', name: 'Panama'}})",
        "    CREATE (eg:Country:{LAB_LABEL} {{id: 'Egypt', name: 'Egypt'}})",
        "    CREATE (dk:Country:{LAB_LABEL} {{id: 'Denmark', name: 'Denmark'}})",
        "    CREATE (panama:Waterway:{LAB_LABEL} {{id: 'Panama_Canal', name: 'Panama Canal', type: 'canal'}})",
        "    CREATE (suez:Waterway:{LAB_LABEL} {{id: 'Suez_Canal', name: 'Suez Canal', type: 'canal'}})",
        "    CREATE (panama)-[:LOCATED_IN]->(pa)",
        "    CREATE (suez)-[:LOCATED_IN]->(eg)",
        "    '''",
        ")",
        "print('Countries and waterways created.')",
    )
)

cells.append(
    md(
        "### Step 2.1c — Create ports",
        "Ports are **hubs** in the network. We store throughput rank for analytics in Part 9.",
    )
)

cells.append(
    code(
        "# Step 2.1c — Major container ports",
        "extra_countries = [",
        "    ('China', 'China'),",
        "    ('United States', 'United States'),",
        "    ('South Korea', 'South Korea'),",
        "]",
        "for cid, cname in extra_countries:",
        "    run_cypher(",
        "        f'MERGE (c:Country:{LAB_LABEL} {{id: $id}}) SET c.name = $name',",
        "        {'id': cid, 'name': cname},",
        "    )",
        "ports = [",
        "    ('Port_of_Rotterdam', 'Port of Rotterdam', 'Netherlands', 1),",
        "    ('Port_of_Singapore', 'Port of Singapore', 'Singapore', 2),",
        "    ('Port_of_Shanghai', 'Port of Shanghai', 'China', 3),",
        "    ('Port_of_Busan', 'Port of Busan', 'South Korea', 4),",
        "    ('Port_of_Los_Angeles', 'Port of Los Angeles', 'United States', 5),",
        "]",
        "for pid, name, country, rank in ports:",
        "    run_cypher(",
        "        f'''",
        "        MATCH (c:Country:{LAB_LABEL} {{id: $country}})",
        "        CREATE (p:Port:{LAB_LABEL} {{id: $id, name: $name, throughput_rank: $rank}})",
        "        CREATE (p)-[:LOCATED_IN]->(c)",
        "        ''',",
        "        {'id': pid, 'name': name, 'country': country, 'rank': rank},",
        "    )",
        "print(f'Created {len(ports)} ports.')",
    )
)

cells.append(
    md(
        "### Step 2.1d — Create shipping organizations",
        "Carriers **operate** at ports and **use** strategic waterways.",
    )
)

cells.append(
    code(
        "# Step 2.1d — Shipping organizations",
        "run_cypher(",
        "    f'''",
        "    MERGE (dk:Country:{LAB_LABEL} {{id: 'Denmark'}}) SET dk.name = 'Denmark'",
        "    MERGE (ch:Country:{LAB_LABEL} {{id: 'Switzerland'}}) SET ch.name = 'Switzerland'",
        "    CREATE (maersk:Organization:{LAB_LABEL} {{id: 'Maersk', name: 'Maersk', sector: 'shipping'}})",
        "    CREATE (msc:Organization:{LAB_LABEL} {{id: 'MSC', name: 'Mediterranean Shipping Company', sector: 'shipping'}})",
        "    CREATE (cosco:Organization:{LAB_LABEL} {{id: 'COSCO', name: 'COSCO Shipping', sector: 'shipping'}})",
        "    CREATE (maersk)-[:HEADQUARTERED_IN]->(dk)",
        "    CREATE (msc)-[:HEADQUARTERED_IN]->(ch)",
        "    WITH maersk, msc, cosco",
        "    MATCH (rot:Port:{LAB_LABEL} {{id: 'Port_of_Rotterdam'}}),",
        "          (sin:Port:{LAB_LABEL} {{id: 'Port_of_Singapore'}}),",
        "          (sha:Port:{LAB_LABEL} {{id: 'Port_of_Shanghai'}}),",
        "          (panama:Waterway:{LAB_LABEL} {{id: 'Panama_Canal'}}),",
        "          (suez:Waterway:{LAB_LABEL} {{id: 'Suez_Canal'}})",
        "    CREATE (maersk)-[:OPERATES_IN]->(rot), (maersk)-[:OPERATES_IN]->(sin)",
        "    CREATE (maersk)-[:USES_ROUTE]->(panama), (maersk)-[:USES_ROUTE]->(suez)",
        "    CREATE (msc)-[:OPERATES_IN]->(rot), (msc)-[:OPERATES_IN]->(sha)",
        "    CREATE (msc)-[:USES_ROUTE]->(suez)",
        "    CREATE (cosco)-[:OPERATES_IN]->(sha), (cosco)-[:OPERATES_IN]->(sin)",
        "    CREATE (cosco)-[:USES_ROUTE]->(panama)",
        "    '''",
        ")",
        "print('Organizations and relationships created.')",
    )
)

cells.append(
    md(
        "### Step 2.1e — Trade lanes between ports",
        "`CONNECTED_TO` edges represent **frequent trade lanes** (undirected for simplicity).",
    )
)

cells.append(
    code(
        "# Step 2.1e — Port-to-port trade lanes",
        "lanes = [",
        "    ('Port_of_Rotterdam', 'Port_of_Singapore', 'Asia-Europe'),",
        "    ('Port_of_Singapore', 'Port_of_Shanghai', 'Intra-Asia'),",
        "    ('Port_of_Shanghai', 'Port_of_Los_Angeles', 'Trans-Pacific'),",
        "    ('Port_of_Busan', 'Port_of_Los_Angeles', 'Trans-Pacific'),",
        "    ('Port_of_Rotterdam', 'Port_of_Los_Angeles', 'Europe-Americas'),",
        "]",
        "for a, b, lane in lanes:",
        "    run_cypher(",
        "        f'''",
        "        MATCH (p1:Port:{LAB_LABEL} {{id: $a}}), (p2:Port:{LAB_LABEL} {{id: $b}})",
        "        MERGE (p1)-[:CONNECTED_TO {{lane: $lane}}]-(p2)",
        "        ''',",
        "        {'a': a, 'b': b, 'lane': lane},",
        "    )",
        "print(f'Created {len(lanes)} trade lanes.')",
    )
)

cells.append(
    md(
        "### Step 2.1f — Regulations and compliance edges",
        "Regulatory knowledge is a classic KG use case: **which rules apply to whom?**",
    )
)

cells.append(
    code(
        "# Step 2.1f — Regulations",
        "run_cypher(",
        "    f'''",
        "    MERGE (uk:Country:{LAB_LABEL} {{id: 'United_Kingdom'}}) SET uk.name = 'United Kingdom'",
        "    CREATE (imo:Agency:{LAB_LABEL} {{id: 'IMO', name: 'International Maritime Organization'}})",
        "    CREATE (imo)-[:HEADQUARTERED_IN]->(uk)",
        "    CREATE (solas:Regulation:{LAB_LABEL} {{id: 'SOLAS', name: 'Safety of Life at Sea', code: 'SOLAS'}})",
        "    CREATE (marpol:Regulation:{LAB_LABEL} {{id: 'MARPOL', name: 'Marine Pollution Prevention', code: 'MARPOL'}})",
        "    CREATE (solas)-[:ISSUED_BY]->(imo), (marpol)-[:ISSUED_BY]->(imo)",
        "    WITH solas, marpol",
        "    MATCH (o:Organization:{LAB_LABEL}) WHERE o.sector = 'shipping'",
        "    CREATE (o)-[:SUBJECT_TO]->(solas), (o)-[:SUBJECT_TO]->(marpol)",
        "    '''",
        ")",
        "print('Regulations linked to shipping organizations.')",
    )
)

cells.append(
    md(
        "### Step 2.1g — Verify the graph",
        "Run this after seeding. Open Neo4j Browser and visualize `KGApplicationsLab` nodes.",
    )
)

cells.append(
    code(
        "# Step 2.1g — Graph summary",
        "summary = run_cypher(",
        "    f'''",
        "    MATCH (n:{LAB_LABEL})",
        "    RETURN labels(n) AS labels, count(*) AS cnt",
        "    ORDER BY cnt DESC",
        "    '''",
        ")",
        "for row in summary:",
        "    print(row)",
        "rels = run_cypher(",
        "    f'''",
        "    MATCH ()-[r]->()",
        "    WHERE all(l IN labels(startNode(r)) WHERE l = '{LAB_LABEL}' OR l <> '{LAB_LABEL}')",
        "    AND (startNode(r):{LAB_LABEL} OR endNode(r):{LAB_LABEL})",
        "    RETURN type(r) AS rel, count(*) AS cnt ORDER BY cnt DESC LIMIT 10",
        "    '''",
        ")",
        "print('\\nTop relationship types:')",
        "for row in rels:",
        "    print(' ', row)",
    )
)

# =============================================================================
# Part 3 — Network discovery
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 3 — Application: Network discovery & search",
        "",
        "**Business question:** *Which shipping companies operate in European ports?*",
        "",
        "SQL often needs many joins. In a graph, **follow edges** from `Organization` to `Port` to `Country`.",
    )
)

cells.append(
    md(
        "### Step 3.1 — Carriers operating in the Netherlands",
    )
)

cells.append(
    code(
        "# Step 3.1 — Organizations at Dutch ports",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL})-[:OPERATES_IN]->(p:Port:{LAB_LABEL})-[:LOCATED_IN]->(c:Country:{LAB_LABEL} {{id: 'Netherlands'}})",
        "    RETURN o.name AS carrier, p.name AS port, c.name AS country",
        "    ORDER BY carrier",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['carrier']} → {r['port']} ({r['country']})\")",
    )
)

cells.append(
    md(
        "### Step 3.2 — All ports a given carrier serves",
        "**Business question:** *Where does Maersk operate?*",
    )
)

cells.append(
    code(
        "# Step 3.2 — Ports for Maersk",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL} {{id: 'Maersk'}})-[:OPERATES_IN]->(p:Port:{LAB_LABEL})",
        "    RETURN p.name AS port, p.throughput_rank AS global_rank",
        "    ORDER BY global_rank",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['port']} (rank {r['global_rank']})\")",
    )
)

cells.append(
    md(
        "### Step 3.3 — Parameterized search function",
        "Wrap Cypher in Python so product teams can call one function from an API.",
    )
)

cells.append(
    code(
        "# Step 3.3 — Reusable discovery helper",
        "def carriers_in_country(country_id: str) -> list[str]:",
        "    rows = run_cypher(",
        "        f'''",
        "        MATCH (o:Organization:{LAB_LABEL})-[:OPERATES_IN]->(:Port:{LAB_LABEL})-[:LOCATED_IN]->(c:Country:{LAB_LABEL} {{id: $country}})",
        "        RETURN DISTINCT o.name AS carrier ORDER BY carrier",
        "        ''',",
        "        {'country': country_id},",
        "    )",
        "    return [r['carrier'] for r in rows]",
        "",
        "print('Netherlands:', carriers_in_country('Netherlands'))",
        "print('China:', carriers_in_country('China'))",
    )
)

# =============================================================================
# Part 4 — Path & impact
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 4 — Application: Path & impact analysis",
        "",
        "**Business question:** *If the Suez Canal is disrupted, which carriers and ports are affected?*",
        "",
        "Graphs make **dependency traversal** explicit: carrier → `USES_ROUTE` → waterway.",
    )
)

cells.append(
    md(
        "### Step 4.1 — Carriers using the Suez Canal",
    )
)

cells.append(
    code(
        "# Step 4.1 — Suez-dependent carriers",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL})-[:USES_ROUTE]->(w:Waterway:{LAB_LABEL} {{id: 'Suez_Canal'}})",
        "    RETURN o.name AS carrier, w.name AS waterway",
        "    ORDER BY carrier",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['carrier']} depends on {r['waterway']}\")",
    )
)

cells.append(
    md(
        "### Step 4.2 — Downstream ports for affected carriers",
        "Two-hop pattern: **waterway → carrier → port**.",
    )
)

cells.append(
    code(
        "# Step 4.2 — Ports served by Suez-dependent carriers",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (w:Waterway:{LAB_LABEL} {{id: 'Suez_Canal'}})<-[:USES_ROUTE]-(o:Organization:{LAB_LABEL})-[:OPERATES_IN]->(p:Port:{LAB_LABEL})",
        "    RETURN DISTINCT w.name AS disrupted_route, o.name AS carrier, p.name AS affected_port",
        "    ORDER BY carrier, affected_port",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['disrupted_route']}: {r['carrier']} → {r['affected_port']}\")",
    )
)

cells.append(
    md(
        "### Step 4.3 — Shortest trade path between two ports",
        "**Business question:** *How are Rotterdam and Los Angeles connected in our lane model?*",
    )
)

cells.append(
    code(
        "# Step 4.3 — Shortest path (trade lanes)",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH path = shortestPath(",
        "      (a:Port:{LAB_LABEL} {{id: 'Port_of_Rotterdam'}})-[:CONNECTED_TO*]-(b:Port:{LAB_LABEL} {{id: 'Port_of_Los_Angeles'}})",
        "    )",
        "    RETURN [n IN nodes(path) | n.name] AS route, length(path) AS hops",
        "    '''",
        ")",
        "for r in rows:",
        "    print('Route:', ' → '.join(r['route']), f\"({r['hops']} hops)\")",
    )
)

cells.append(
    md(
        "### Step 4.4 — Impact report helper",
        "Package graph results for an operations dashboard.",
    )
)

cells.append(
    code(
        "# Step 4.4 — Impact analysis function",
        "def impact_if_waterway_blocked(waterway_id: str) -> dict:",
        "    carriers = run_cypher(",
        "        f'''",
        "        MATCH (w:Waterway:{LAB_LABEL} {{id: $wid}})<-[:USES_ROUTE]-(o:Organization:{LAB_LABEL})",
        "        RETURN collect(DISTINCT o.name) AS carriers",
        "        ''',",
        "        {'wid': waterway_id},",
        "    )[0]['carriers']",
        "    ports = run_cypher(",
        "        f'''",
        "        MATCH (w:Waterway:{LAB_LABEL} {{id: $wid}})<-[:USES_ROUTE]-(o:Organization:{LAB_LABEL})-[:OPERATES_IN]->(p:Port:{LAB_LABEL})",
        "        RETURN collect(DISTINCT p.name) AS ports",
        "        ''',",
        "        {'wid': waterway_id},",
        "    )[0]['ports']",
        "    return {'waterway': waterway_id, 'carriers': carriers, 'ports': ports}",
        "",
        "import json",
        "print(json.dumps(impact_if_waterway_blocked('Suez_Canal'), indent=2))",
    )
)

# =============================================================================
# Part 5 — Entity resolution
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 5 — Application: Entity resolution",
        "",
        "**Business question:** *Are \"MSC\" and \"Mediterranean Shipping Company\" the same organization?*",
        "",
        "Real data arrives from **multiple sources** with different names. Graphs support:",
        "",
        "1. **Candidate generation** — find similar names",
        "2. **Merge** — unify to one canonical node",
        "3. **Provenance** — keep `alt_names` for audit",
    )
)

cells.append(
    md(
        "### Step 5.1 — Seed a duplicate record (simulating a second data feed)",
    )
)

cells.append(
    code(
        "# Step 5.1 — Duplicate organization from another source",
        "run_cypher(",
        "    f'''",
        "    CREATE (dup:Organization:{LAB_LABEL} {{id: 'MSC_DUP', name: 'MSC', alt_name: 'Mediterranean Shipping Co.'}})",
        "    WITH dup",
        "    MATCH (rot:Port:{LAB_LABEL} {{id: 'Port_of_Rotterdam'}})",
        "    CREATE (dup)-[:OPERATES_IN]->(rot)",
        "    '''",
        ")",
        "print('Duplicate MSC record created (id=MSC_DUP).')",
    )
)

cells.append(
    md(
        "### Step 5.2 — Find resolution candidates",
        "Simple rule: same **normalized name** or overlapping **port operations**.",
    )
)

cells.append(
    code(
        "# Step 5.2 — Candidate pairs",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (a:Organization:{LAB_LABEL}), (b:Organization:{LAB_LABEL})",
        "    WHERE id(a) < id(b) AND a.name = b.name",
        "    RETURN a.id AS id_a, b.id AS id_b, a.name AS shared_name",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"Candidate merge: {r['id_a']} + {r['id_b']} (name={r['shared_name']})\")",
    )
)

cells.append(
    md(
        "### Step 5.3 — Merge duplicates onto canonical node",
        "Use `MERGE` + `apoc.refactor.mergeNodes` pattern manually with `MATCH` for teaching clarity.",
    )
)

cells.append(
    code(
        "# Step 5.3 — Merge MSC_DUP into canonical MSC",
        "run_cypher(",
        "    f'''",
        "    MATCH (canonical:Organization:{LAB_LABEL} {{id: 'MSC'}})",
        "    MATCH (dup:Organization:{LAB_LABEL} {{id: 'MSC_DUP'}})",
        "    SET canonical.alt_names = coalesce(canonical.alt_names, []) + coalesce([dup.alt_name], [])",
        "    WITH canonical, dup",
        "    MATCH (dup)-[r:OPERATES_IN]->(p:Port:{LAB_LABEL})",
        "    MERGE (canonical)-[:OPERATES_IN]->(p)",
        "    DELETE r",
        "    WITH canonical, dup",
        "    DETACH DELETE dup",
        "    '''",
        ")",
        "print('Merged MSC_DUP into MSC.')",
    )
)

cells.append(
    code(
        "# Step 5.3b — Verify single MSC node",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL}) WHERE o.name CONTAINS 'Mediterranean' OR o.id = 'MSC'",
        "    RETURN o.id, o.name, o.alt_names",
        "    '''",
        ")",
        "for r in rows:",
        "    print(r)",
    )
)

# =============================================================================
# Part 6 — Recommendations
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 6 — Application: Recommendations & similarity",
        "",
        "**Business question:** *Which ports are similar to Singapore for expansion planning?*",
        "",
        "**Collaborative pattern:** ports linked to the **same carriers** are similar.",
        "This is the same idea as *users who bought X also bought Y* — but on a graph.",
    )
)

cells.append(
    md(
        "### Step 6.1 — Ports sharing carriers with Singapore",
    )
)

cells.append(
    code(
        "# Step 6.1 — Similar ports (shared carriers)",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (target:Port:{LAB_LABEL} {{id: 'Port_of_Singapore'}})<-[:OPERATES_IN]-(o:Organization:{LAB_LABEL})-[:OPERATES_IN]->(other:Port:{LAB_LABEL})",
        "    WHERE target <> other",
        "    RETURN other.name AS similar_port, count(DISTINCT o) AS shared_carriers",
        "    ORDER BY shared_carriers DESC",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['similar_port']}: {r['shared_carriers']} shared carrier(s)\")",
    )
)

cells.append(
    md(
        "### Step 6.2 — Recommend carriers for a new port (co-location pattern)",
        "If a new port is in **Europe**, recommend carriers already operating in European ports.",
    )
)

cells.append(
    code(
        "# Step 6.2 — Carrier recommendations for European expansion",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL})-[:OPERATES_IN]->(p:Port:{LAB_LABEL})-[:LOCATED_IN]->(c:Country:{LAB_LABEL})",
        "    WHERE c.id IN ['Netherlands', 'Denmark']",
        "    RETURN o.name AS recommended_carrier, count(DISTINCT p) AS european_ports",
        "    ORDER BY european_ports DESC",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['recommended_carrier']}: {r['european_ports']} EU port(s)\")",
    )
)

# =============================================================================
# Part 7 — Compliance
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 7 — Application: Compliance & regulatory mapping",
        "",
        "**Business question:** *Which IMO regulations apply to Maersk? Who issued them?*",
        "",
        "Compliance graphs link **policies → authorities → entities**. Auditors traverse edges instead of reading PDFs in isolation.",
    )
)

cells.append(
    md(
        "### Step 7.1 — Regulations for a carrier",
    )
)

cells.append(
    code(
        "# Step 7.1 — Maersk compliance view",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL} {{id: 'Maersk'}})-[:SUBJECT_TO]->(reg:Regulation:{LAB_LABEL})-[:ISSUED_BY]->(agency:Agency:{LAB_LABEL})",
        "    RETURN o.name AS organization, reg.code AS regulation, agency.name AS issued_by",
        "    ORDER BY regulation",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['organization']} must follow {r['regulation']} (issued by {r['issued_by']})\")",
    )
)

cells.append(
    md(
        "### Step 7.2 — All carriers under a regulation",
    )
)

cells.append(
    code(
        "# Step 7.2 — Organizations subject to SOLAS",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL})-[:SUBJECT_TO]->(reg:Regulation:{LAB_LABEL} {{code: 'SOLAS'}})",
        "    RETURN o.name AS carrier ORDER BY carrier",
        "    '''",
        ")",
        "print('SOLAS applies to:', [r['carrier'] for r in rows])",
    )
)

cells.append(
    md(
        "### Step 7.3 — Compliance checklist export",
    )
)

cells.append(
    code(
        "# Step 7.3 — Build compliance checklist for all shipping orgs",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL} {{sector: 'shipping'}})-[:SUBJECT_TO]->(reg:Regulation:{LAB_LABEL})",
        "    RETURN o.name AS carrier, collect(reg.code) AS regulations",
        "    ORDER BY carrier",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['carrier']}: {', '.join(r['regulations'])}\")",
    )
)

# =============================================================================
# Part 8 — LLM Q&A
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 8 — Application: Business Q&A with LLM + Cypher",
        "",
        "**Business question:** *Stakeholders ask in plain English; analysts should not write Cypher for every question.*",
        "",
        "We use LangChain's **`GraphCypherQAChain`** with schema introspection — the same pattern as",
        "`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`, scoped to our lab graph.",
        "",
        "> **Requires:** `LLM_MODEL_SETUP.md` and a working `llm` from Step 0d.",
    )
)

cells.append(
    md(
        "### Step 8.1 — Connect LangChain Neo4jGraph",
    )
)

cells.append(
    code(
        "# Step 8.1 — LangChain Neo4jGraph (schema-aware)",
        "from langchain_neo4j import Neo4jGraph",
        "",
        "neo4j_graph = Neo4jGraph(",
        "    url=NEO4J_URI,",
        "    username=NEO4J_USERNAME,",
        "    password=NEO4J_PASSWORD,",
        "    database=NEO4J_DATABASE,",
        ")",
        "neo4j_graph.refresh_schema()",
        "print('Schema snippet (first 800 chars):')",
        "print((neo4j_graph.schema or '')[:800])",
    )
)

cells.append(
    md(
        "### Step 8.2 — GraphCypherQAChain",
        "The chain: question → LLM writes Cypher → execute → LLM summarizes answer.",
    )
)

cells.append(
    code(
        "# Step 8.2 — Natural language → Cypher → answer",
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
        "    question = 'Which organizations use the Suez Canal and which ports do they operate?'",
        "    answer = chain.invoke({'query': question})",
        "    print('\\nQuestion:', question)",
        "    print('Answer:', answer.get('result', answer))",
    )
)

cells.append(
    md(
        "### Step 8.3 — Try your own business questions",
        "Examples that work well on this lab graph:",
        "",
        "- *Which ports are in the Netherlands?*",
        "- *What regulations apply to COSCO?*",
        "- *Which waterway does Maersk use?*",
    )
)

cells.append(
    code(
        "# Step 8.3 — Your question (edit the string)",
        "MY_QUESTION = 'Which ports are connected to Rotterdam via trade lanes?'",
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
# Part 9 — Analytics
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 9 — Application: Graph analytics (hub importance)",
        "",
        "**Business question:** *Which ports are the most connected hubs in our trade-lane network?*",
        "",
        "Centrality metrics highlight **bottlenecks** and **strategic locations**.",
        "We use degree centrality in pure Cypher (no GDS plugin required for this course).",
    )
)

cells.append(
    md(
        "### Step 9.1 — Port degree (number of trade-lane neighbors)",
    )
)

cells.append(
    code(
        "# Step 9.1 — Port connectivity rank",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (p:Port:{LAB_LABEL})",
        "    OPTIONAL MATCH (p)-[:CONNECTED_TO]-(neighbor:Port:{LAB_LABEL})",
        "    RETURN p.name AS port, count(DISTINCT neighbor) AS lane_degree, p.throughput_rank AS throughput_rank",
        "    ORDER BY lane_degree DESC, throughput_rank",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['port']}: {r['lane_degree']} neighbors (throughput rank {r['throughput_rank']})\")",
    )
)

cells.append(
    md(
        "### Step 9.2 — Carrier footprint (operating degree)",
    )
)

cells.append(
    code(
        "# Step 9.2 — Organizations by number of ports served",
        "rows = run_cypher(",
        "    f'''",
        "    MATCH (o:Organization:{LAB_LABEL})-[:OPERATES_IN]->(p:Port:{LAB_LABEL})",
        "    RETURN o.name AS carrier, count(p) AS ports_served",
        "    ORDER BY ports_served DESC",
        "    '''",
        ")",
        "for r in rows:",
        "    print(f\"{r['carrier']}: {r['ports_served']} port(s)\")",
    )
)

cells.append(
    md(
        "### Step 9.3 — Optional: Neo4j Graph Data Science (GDS)",
        "",
        "For production analytics, install the **Graph Data Science** library in Neo4j Desktop or AuraDS.",
        "Algorithms like **PageRank**, **Louvain community detection**, and **betweenness centrality**",
        "run on projected graphs. The Cypher patterns in 9.1–9.2 teach the same intuition without extra plugins.",
    )
)

# =============================================================================
# Part 10 — Wrap up
# =============================================================================
cells.append(
    md(
        "---",
        "",
        "# Part 10 — Wrap-up & next steps",
        "",
        "## What you practiced",
        "",
        "| Part | Application | Key Cypher idea |",
        "|------|-------------|-----------------|",
        "| 3 | Network discovery | Multi-hop `MATCH` |",
        "| 4 | Impact analysis | Path queries, `shortestPath` |",
        "| 5 | Entity resolution | `MERGE`, deduplicate nodes |",
        "| 6 | Recommendations | Shared-neighbor pattern |",
        "| 7 | Compliance | Policy → entity traversal |",
        "| 8 | Business Q&A | LLM + `GraphCypherQAChain` |",
        "| 9 | Analytics | Degree / ranking |",
        "",
        "## Map to your domain",
        "",
        "Replace `Port` / `Organization` with entities in **your** industry:",
        "",
        "| Domain | Node examples | Relationship examples |",
        "|--------|---------------|----------------------|",
        "| Healthcare | Patient, Treatment, Diagnosis | `RECEIVED`, `INDICATED_FOR` |",
        "| Finance | Account, Transaction, Company | `TRANSFERRED_TO`, `OWNS` |",
        "| Cybersecurity | IP, Domain, Malware | `RESOLVES_TO`, `COMMUNICATES_WITH` |",
        "| HR | Employee, Skill, Project | `HAS_SKILL`, `WORKED_ON` |",
        "",
        "## Continue learning",
        "",
        "1. **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** — populate graphs from documents.",
        "2. **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** — RAG, GraphRAG, agents.",
        "3. **`Module_8_Evaluating_GraphRAG_with_RAGAS.ipynb`** — measure answer quality.",
        "",
        "## Clean up (optional)",
        "",
        "```cypher",
        "MATCH (n:KGApplicationsLab) DETACH DELETE n;",
        "```",
        "",
        "---",
        "",
        "*End of course — Practical Knowledge Graph Applications for Real-World Problems*",
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

out_path = Path(__file__).resolve().parent.parent / "Module_8_Practical_Knowledge_Graph_Applications.ipynb"
out_path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {out_path} ({len(cells)} cells)")
