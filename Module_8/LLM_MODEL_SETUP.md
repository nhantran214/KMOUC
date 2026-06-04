# LLM Model Setup Guide — Module 8 (Neo4j + LLMs)

This guide configures the **LLM** used in Module 8 notebooks (graph extraction, RAG answers, text-to-Cypher, agents).

Use together with:

- `NEO4J_SETUP.md` — Neo4j database
- `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb` — build graphs from text with LLMs
- `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb` — LangChain + Neo4j integration
- `Module_8_Using_Knowledge_Graph_with_LlamaIndex.ipynb` — LlamaIndex + Neo4j integration (via `langchain-neo4j` bridge)

---

## Overview

The course converts unstructured text into graph nodes and relationships using an LLM.

| Path | `LLM_BACKEND` | How the notebook calls the model |
|------|---------------|----------------------------------|
| **Ollama + runner (recommended)** | `ollama` | Subprocess → `ollama_model_runner.py` → Ollama HTTP API |
| **OpenAI (cloud)** | `openai` | `langchain-openai` (`ChatOpenAI`) |

The **Ollama + runner** path matches **Module 4 / Module 5**: the Jupyter kernel does not host the model; a small script calls `http://localhost:11434/api/generate`. That is more stable for long extractions.

---

## Prerequisites

1. Python packages from `NEO4J_SETUP.md` (notebook Step 0a).
2. Neo4j variables in `Module_8/.env`.
3. File present: `Module_8/ollama_model_runner.py` (shipped with this module).

---

## Option 1 — Ollama + `ollama_model_runner.py` (recommended)

### Step 1 — Install Ollama

Download from [https://ollama.com](https://ollama.com).

### Step 2 — Start the service

```bash
ollama serve
```

Keep this running while you use the notebook.

### Step 3 — Pull a model

```bash
ollama pull llama3.2:3b
```

Stronger option for better extraction:

```bash
ollama pull llama3.1:8b
```

Verify:

```bash
ollama list
```

### Step 4 — Set environment variables

Create `Module_8/.env` (copy from `.env.example`):

```dotenv
LLM_BACKEND=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TEMPERATURE=0
OLLAMA_MAX_TOKENS=2048
```

Shell export (optional):

```bash
export LLM_BACKEND=ollama
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2:3b
export OLLAMA_MAX_TOKENS=2048
```

> **Graph extraction** needs more tokens than short chat demos. Use `OLLAMA_MAX_TOKENS=2048` (or higher if your machine allows).

### Step 5 — Smoke test the runner (terminal)

From `Module_8`:

```bash
cd /path/to/KMOU_Course/Module_8

python ollama_model_runner.py \
  --host http://localhost:11434 \
  --models llama3.2:3b \
  --prompt "Reply with exactly: Ollama OK" \
  --temperature 0 \
  --max-tokens 32
```

Expect JSON with `"status": "ok"` and a short response in `outputs[0].response`.

### Step 6 — Verify in the notebook

Run **Step 0b → 0d → 0e** in `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`.

You should see:

- `OLLAMA_RUNNER: .../Module_8/ollama_model_runner.py`
- `Ollama runner smoke test: OK`
- `LLM ready for LLMGraphTransformer (backend=ollama)`

---

## Option 2 — OpenAI (cloud)

### Step 1 — API key

Create a key at [https://platform.openai.com](https://platform.openai.com).

### Step 2 — Environment variables

```dotenv
LLM_BACKEND=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
```

Install (if needed):

```bash
python -m pip install langchain-openai
```

The notebook uses `ChatOpenAI` directly for this path (no `ollama_model_runner.py`).

---

## How `ollama_model_runner.py` works

| Argument | Purpose |
|----------|---------|
| `--host` | Ollama base URL (default `http://localhost:11434`) |
| `--models` | One or comma-separated models, e.g. `llama3.2:3b` or `llama3.1:8b,mistral:7b` |
| `--prompt` / `--prompt-file` | Input text |
| `--temperature` | Sampling temperature (course default `0`) |
| `--max-tokens` | `num_predict` limit (course default `2048` for KG extraction) |

The script prints **one JSON object** to stdout. The notebook parses `outputs[0].response` and passes it to LangChain's `LLMGraphTransformer` via a thin `OllamaRunnerLLM` wrapper.

---

## Troubleshooting

### `ollama_model_runner.py not found`

Run the notebook with working directory `Module_8`, or keep the file in that folder. The notebook resolves:

1. `Module_8/ollama_model_runner.py`
2. `Module_4/ollama_model_runner.py` (fallback)

### Connection refused to `localhost:11434`

- Start `ollama serve`
- Confirm `OLLAMA_HOST` matches your Ollama URL

### Model not found

```bash
ollama pull <model-from-OLLAMA_MODEL>
ollama list
```

### Runner exits with error in notebook

Read the raised `RuntimeError` — it includes stderr from the subprocess. Common causes:

- Ollama not running
- Wrong model name
- Out of memory (try `llama3.2:3b`)

### Extraction is slow or times out

- Use a smaller model for testing
- Increase `OLLAMA_MAX_TOKENS` only if responses are cut off
- First extraction after `ollama pull` can be slow (model load)

### OpenAI authentication error

- Set `OPENAI_API_KEY` in `Module_8/.env`
- Set `LLM_BACKEND=openai`

### Weak graph extraction

- Prefer `llama3.1:8b` or `gpt-4o-mini`
- Use schema-guided extraction (notebook Section 2.3)

---

## Security notes

- Do not commit `Module_8/.env` with API keys.
- Ollama runs locally — no cloud API key required for the default path.

When setup is complete, continue in your Module 8 notebook from **Step 0**:

- `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`
- `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`
