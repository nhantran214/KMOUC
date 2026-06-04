# Neo4j Setup Guide — Building Knowledge Graphs with LLMs

This guide helps you install and configure **Neo4j** and related tools on your machine so you can complete the Module 8 hands-on notebooks:

| Notebook | Topic |
|----------|--------|
| `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb` | Build knowledge graphs with LLMs |
| `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb` | Neo4j + LangChain (RAG, GraphRAG, text-to-Cypher, agents) |
| `Module_8_Using_Knowledge_Graph_with_LlamaIndex.ipynb` | Neo4j + LlamaIndex (RAG, GraphRAG, text-to-Cypher, agents) |

These notebooks **do not** repeat full installation steps. Complete this document first, then open the notebook you are taking.

---

## What you need


| Component               | Purpose                                                     | Minimum version                                                                    |
| ----------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Neo4j Database**      | Store nodes, relationships, and (optionally) vector indexes | **5.15+** (required for LLM Knowledge Graph Builder)                               |
| **APOC**                | Utility procedures used by graph import tools               | Bundled with Neo4j Desktop / Aura; install plugin on self-hosted                   |
| **Python 3.10+**        | Run the Jupyter notebook                                    | Same as your other course modules                                                  |
| **LLM access** (one of) | Extract entities from text                                  | OpenAI API key, or **Ollama** locally, or Gemini/Anthropic in LLM Graph Builder UI |
| **(Optional) Docker**   | Run Neo4j or LLM Graph Builder locally                      | Docker Desktop or Docker Engine                                                    |


---

## Choose your Neo4j deployment

Pick **one** path below. Beginners often start with **Option A (Aura Free)** because there is nothing to install on disk except the browser.


| Option                          | Best for                                                | Internet required |
| ------------------------------- | ------------------------------------------------------- | ----------------- |
| **A — Neo4j Aura (Free)**       | Quickest start, works with LLM Graph Builder hosted app | Yes               |
| **B — Neo4j Desktop**           | Local development with GUI, Bloom, plugins              | For download      |
| **C — Docker**                  | Reproducible local server, CI-like environments         | For image pull    |
| **D — Linux package / tarball** | Servers without Desktop                                 | For download      |


After setup, you will have:

- **URI** — e.g. `neo4j+s://xxxx.databases.neo4j.io` (Aura) or `neo4j://localhost:7687` (local)
- **Username** — usually `neo4j`
- **Password** — you set this at creation time
- **Database name** — usually `neo4j` (Aura) or `neo4j` (default)

Keep these in a password manager. **Do not commit passwords to Git.**

---

## Option A — Neo4j Aura (Free tier)

Aura is Neo4j’s managed cloud database. The free tier is enough for this course.

### Step A1 — Create an account

1. Open [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/)
2. Sign up or log in.
3. Create a new **AuraDB Free** instance (not AuraDS unless you specifically need Graph Data Science features).

### Step A2 — Save connection details

When the instance is ready:

1. Click **Download credentials** or copy the connection details.
2. Note:
  - **Connection URI** (starts with `neo4j+s://`)
  - **Username** (`neo4j`)
  - **Password** (shown once — save it now)

### Step A3 — Open Neo4j Browser

1. In the Aura console, click **Open** / **Query** for your instance.
2. Run a smoke test:

```cypher
RETURN "Aura connection OK" AS message;
```

### Step A4 — Use with the LLM Knowledge Graph Builder (web app)

1. Open [https://llm-graph-builder.neo4jlabs.com/](https://llm-graph-builder.neo4jlabs.com/) (or the link from [Neo4j Labs — LLM Graph Builder](https://neo4j.com/labs/genai-ecosystem/llm-graph-builder/)).
2. Paste your Aura URI, username, and password (or drag the downloaded credentials file).
3. Upload a sample document and run **Generate Graph**.

### Step A5 — Use with the Jupyter notebook

Set environment variables before running connection cells (replace placeholders):

```bash
export NEO4J_URI="neo4j+s://YOUR_INSTANCE.databases.neo4j.io"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your-password-here"
export NEO4J_DATABASE="neo4j"
```

On Windows (PowerShell):

```powershell
$env:NEO4J_URI="neo4j+s://YOUR_INSTANCE.databases.neo4j.io"
$env:NEO4J_USERNAME="neo4j"
$env:NEO4J_PASSWORD="your-password-here"
$env:NEO4J_DATABASE="neo4j"
```

---

## Option B — Neo4j Desktop (Windows, macOS, Linux)

Neo4j Desktop is a free application that manages local databases, plugins, and Neo4j Browser.

### Step B1 — Download and install

1. Download from [https://neo4j.com/download/](https://neo4j.com/download/)
2. Install Neo4j Desktop for your operating system.
3. Launch Desktop and sign in (free account).

### Step B2 — Create a local database

1. Click **Create instance** (or **New** → **Instance**).
2. Choose a name, e.g. `kg-llm-course`.
3. Set a **password** you will remember.
4. Select Neo4j version **5.15 or later**.
5. Start the instance (status should become **Running**).

### Step B3 — Enable APOC (if not already enabled)

1. Open the instance → **Plugins** → install **APOC** if available.
2. Or add to instance settings / `apoc.conf` as documented in Desktop.

### Step B4 — Connection details for the notebook


| Setting  | Typical value            |
| -------- | ------------------------ |
| URI      | `neo4j://localhost:7687` |
| Username | `neo4j`                  |
| Password | (your instance password) |
| Database | `neo4j`                  |


Test in **Open** → Neo4j Browser:

```cypher
RETURN "Desktop connection OK" AS message;
```

### Step B5 — LLM Graph Builder with Desktop

The hosted LLM Graph Builder can connect to a **publicly reachable** database. A default Desktop instance is usually **localhost only**, so:

- Use the **notebook’s programmatic extraction** (LangChain + Neo4j), **or**
- Deploy [llm-graph-builder](https://github.com/neo4j-labs/llm-graph-builder) locally with Docker (see Option C + LLM Graph Builder section below).

---

## Option C — Neo4j with Docker

Use Docker when you want a clean, repeatable Neo4j server without Desktop.

### Step C1 — Install Docker

- **Windows / macOS**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: Docker Engine + Docker Compose plugin

Verify:

```bash
docker --version
docker compose version
```

### Step C2 — Run Neo4j 5.x (verified on Linux + Docker)

Run all commands from the **KMOU_Course** repo root.

#### C2a — Prepare the data folder

```bash
cd /path/to/KMOU_Course

mkdir -p Module_8/neo4j-course-data
sudo chown -R 7474:7474 Module_8/neo4j-course-data
```

On Linux, Neo4j in Docker runs as user `7474`. Without `chown`, the container may exit with code **1** or **70**.

#### C2b — Start the container (course default)

Use a **strong password** (do not use `neo4j/neo4j` — Neo4j 5.x often fails to start with a weak password).

```bash
sudo docker rm -f neo4j-kg-course 2>/dev/null

sudo docker run -d \
  --name neo4j-kg-course \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/CourseNeo4j2026! \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_server_memory_heap_initial__size=512m \
  -e NEO4J_server_memory_heap_max__size=1G \
  -v "$(pwd)/Module_8/neo4j-course-data:/data" \
  neo4j:5.26-community
```

Follow startup logs until ready:

```bash
sudo docker logs -f neo4j-kg-course
```

Stop following when you see **`Started.`** (first run may take **1–3 minutes** while APOC downloads).

Verify the container is up:

```bash
sudo docker ps --filter name=neo4j-kg-course
curl -I http://127.0.0.1:7474
```

| Port | Service                           |
| ---- | --------------------------------- |
| 7474 | Neo4j Browser (HTTP)              |
| 7687 | Bolt protocol (drivers, notebook) |

Open Browser: [http://127.0.0.1:7474](http://127.0.0.1:7474) (or [http://localhost:7474](http://localhost:7474)).

**Login**

- Connect URL: `neo4j://localhost:7687`
- Username: `neo4j`
- Password: `CourseNeo4j2026!` (must match `NEO4J_AUTH`)

> Change the password in `NEO4J_AUTH` and in `Module_8/.env` if you use a different value — they must match.

### Step C3 — Environment variables

Copy `Module_8/.env.example` to `Module_8/.env` and set:

```bash
export NEO4J_URI="neo4j://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="CourseNeo4j2026!"
export NEO4J_DATABASE="neo4j"
```

### Step C4 — Stop and remove (when finished)

```bash
docker stop neo4j-kg-course
docker rm neo4j-kg-course
```

Data persists in the mounted volume unless you delete that folder.

---

## Option D — Linux (without Desktop)

### Ubuntu / Debian (example)

```bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/neo4j.gpg
echo "deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest" | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j
```

Enable and start:

```bash
sudo systemctl enable neo4j
sudo systemctl start neo4j
```

Set initial password (first login via Browser at `http://localhost:7474`).

Install APOC per [Neo4j APOC documentation](https://neo4j.com/docs/apoc/current/installation/).

---

## Python environment for the notebook

From the `Module_8` folder (use the same virtual environment / conda env as your other modules):

```bash
cd /path/to/KMOU_Course/Module_8
python -m pip install --upgrade pip
python -m pip install neo4j jupyter python-dotenv requests \
  langchain langchain-community langchain-classic langchain-experimental langchain-neo4j \
  langchain-openai sentence-transformers
```

Optional (OpenAI path in notebook):

```bash
python -m pip install langchain-openai neo4j-graphrag
```

Optional (full GraphRAG pipeline):

```bash
python -m pip install neo4j-graphrag
```

Start Jupyter:

```bash
jupyter notebook Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb
# or
jupyter notebook Module_8_Using_Knowledge_Graph_with_LangChain.ipynb
```

---

## LLM provider and model setup

LLM provider setup has been moved to a dedicated guide:

- `**LLM_MODEL_SETUP.md**` — complete setup for Ollama/OpenAI models, environment variables, and LLM-specific troubleshooting.

Complete that file before running the notebook extraction steps.

---

## Neo4j LLM Knowledge Graph Builder (web application)

The official tool mirrors what you will build in code:


| Resource              | URL                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------- |
| Hosted app            | [https://llm-graph-builder.neo4jlabs.com/](https://llm-graph-builder.neo4jlabs.com/)        |
| Documentation         | [Neo4j Labs — LLM Graph Builder](https://neo4j.com/labs/genai-ecosystem/llm-graph-builder/) |
| Source (local deploy) | [github.com/neo4j-labs/llm-graph-builder](https://github.com/neo4j-labs/llm-graph-builder)  |


### Requirements for the web app

- Neo4j **5.15+** with **APOC**
- Aura Free/Professional **or** self-hosted instance the app can reach
- An LLM API key configured in the app (OpenAI, Gemini, etc.) **or** Ollama for local models (see project README)

### Local deploy (advanced)

```bash
git clone https://github.com/neo4j-labs/llm-graph-builder.git
cd llm-graph-builder
# Follow README: docker-compose up, configure .env with Neo4j + LLM keys
```

This is optional; the notebook covers the same concepts programmatically.

---

## Troubleshooting

### Docker (Option C): `http://localhost:7474` is blank or does not load

Work through these checks **in order** on your machine:

#### 1) Is the container running?

```bash
sudo docker ps -a --filter name=neo4j-kg-course
```

You want **STATUS** like `Up X minutes`, and ports `0.0.0.0:7474->7474/tcp`.

If status is `Exited` or `Restarting`, read logs:

```bash
sudo docker logs neo4j-kg-course --tail 80
```

#### 2) Common fix — volume permissions (Linux)

If logs mention `Permission denied` on `/data`, the bind mount folder is owned by root but Neo4j runs as user `7474` inside the container.

From the **KMOU_Course** repo root:

```bash
mkdir -p Module_8/neo4j-course-data
sudo chown -R 7474:7474 Module_8/neo4j-course-data
sudo docker restart neo4j-kg-course
```

Wait 1–2 minutes, then open [http://127.0.0.1:7474](http://127.0.0.1:7474).

#### 3) Port already in use

If `docker run` failed with “port is already allocated”, another process uses 7474/7687:

```bash
sudo docker stop neo4j-kg-course
sudo docker rm neo4j-kg-course
# Or change host ports: -p 7475:7474 -p 7688:7687 and use http://localhost:7475
```

#### 4) Container `Exited (1)` or `Exited (70)`

| Exit code | Common cause |
|-----------|----------------|
| **1** | Volume not writable (fix with `chown -R 7474:7474`) |
| **70** | Weak password (`neo4j/neo4j`) or corrupt/partial data in volume |

**Recreate container cleanly** (verified working command):

```bash
cd /path/to/KMOU_Course

sudo docker rm -f neo4j-kg-course 2>/dev/null
sudo rm -rf Module_8/neo4j-course-data
mkdir -p Module_8/neo4j-course-data
sudo chown -R 7474:7474 Module_8/neo4j-course-data

sudo docker run -d \
  --name neo4j-kg-course \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/CourseNeo4j2026! \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_server_memory_heap_initial__size=512m \
  -e NEO4J_server_memory_heap_max__size=1G \
  -v "$(pwd)/Module_8/neo4j-course-data:/data" \
  neo4j:5.26-community

sudo docker logs -f neo4j-kg-course
```

Stop following logs when you see **`Started.`**, then open the Browser.

#### 5) Login in Neo4j Browser

- Connect URL: `neo4j://localhost:7687` (or `bolt://localhost:7687`)
- Username: `neo4j`
- Password: same as in `NEO4J_AUTH` (course default: `CourseNeo4j2026!`)

#### 6) Quick HTTP test

```bash
curl -I http://127.0.0.1:7474
```

Expect HTTP `200` or `302` when the service is up. If `connection refused`, the container is not listening yet or not running.

#### 7) APOC slows first boot

If APOC download fails in logs, temporarily start **without** `NEO4J_PLUGINS` to verify the base image works (keep the same password and memory settings as Step C2b). Add `NEO4J_PLUGINS='["apoc"]'` again after Browser login works.

---

### `Unable to connect` / `ServiceUnavailable`

- Check the instance is **Running** (Desktop / Aura / Docker).
- Verify **URI** scheme: Aura uses `neo4j+s://`; local Docker/Desktop often uses `neo4j://`.
- Firewall: port **7687** must be open for local Bolt.

### `Authentication failed`

- Reset password in Aura console or Desktop instance settings.
- Username is almost always `neo4j`.

### `Unknown database`

- Aura Free typically uses database name `neo4j`.
- Do not set a custom database name unless you created one.

### APOC procedures missing

- Install APOC plugin (Desktop Plugins tab or Docker `NEO4J_PLUGINS`).
- Restart the database after installing.

### LLM extraction returns empty graph

- Model too small for structured JSON — try a larger Ollama model or OpenAI `gpt-4o-mini`.
- Text too short — use the sample file in `Module_8/data/`.
- Check notebook cell output for JSON parse errors.

### SSL certificate errors (Aura)

- Use the exact URI from Aura (`neo4j+s://...`).
- Update the `neo4j` Python driver: `pip install -U neo4j`.

---

## Security checklist

- Passwords and API keys only in environment variables or `.env` (gitignored)
- `.env` listed in `.gitignore`
- Aura instance not shared publicly without intent
- Stop Docker/local instances when not in use on shared machines

---

## Quick reference — notebook environment variables


| Variable         | Example                                                        |
| ---------------- | -------------------------------------------------------------- |
| `NEO4J_URI`      | `neo4j://localhost:7687` or `neo4j+s://....databases.neo4j.io` |
| `NEO4J_USERNAME` | `neo4j`                                                        |
| `NEO4J_PASSWORD` | (your password)                                                |
| `NEO4J_DATABASE` | `neo4j`                                                        |
| `LLM_BACKEND`    | See `LLM_MODEL_SETUP.md`                                       |
| `OLLAMA_MODEL`   | See `LLM_MODEL_SETUP.md`                                       |
| `OPENAI_API_KEY` | See `LLM_MODEL_SETUP.md`                                       |


When setup is complete, open your course notebook and start from **Step 0**:

- `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`
- `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`