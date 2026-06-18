#!/usr/bin/env python3
"""Build Korean Module_4 LlamaIndex notebook from the English source."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Module_4_Using_Knowledge_Graph_with_LlamaIndex.ipynb"
DST = ROOT / "Module_4_Using_Knowledge_Graph_with_LlamaIndex_KO.ipynb"

MARKDOWN_KO: dict[int, str] = {
    0: """# LlamaIndex로 지식 그래프(Knowledge Graph) 활용

**코스 모듈:** Module 8
**대상:** 그래프/Neo4j 기초, Python, LlamaIndex 입문 경험이 있는 초급 학습자

## 코스 설명

이 코스에서는 **Neo4j**를 **LlamaIndex** 애플리케이션에 통합하여
생성형 AI(Generative AI) 워크플로에서 그래프 데이터베이스를 활용하는 방법을 배웁니다.

**학습 내용:**

- **`Neo4jPropertyGraphStore`**와 **`Neo4jVectorStore`**로 LlamaIndex를 Neo4j에 연결하기
- **RAG** 및 **GraphRAG** retriever 만들기
- **text-to-Cypher** retriever 구현 및 맞춤 설정
- Neo4j와 상호작용하는 간단한 **LlamaIndex agent** 만들기

> **언어:** 이 노트북의 안내 텍스트는 **한국어**입니다. 기술 용어는 필요 시 영어를 병기합니다.

> **설정(코드 실행 전 필수):** **`NEO4J_SETUP.md`**와 **`LLM_MODEL_SETUP.md`**를 완료하세요.
> 로컬 LLM의 경우 `ollama serve`를 실행하고 LLM 가이드에 설명된 **`ollama_model_runner.py`**를 사용하세요.

### 이 노트북 사용법

1. 각 **코드** 셀을 실행하기 전에 위 **마크다운** 셀을 읽으세요.
2. Step 0부터 **순서대로** 셀을 실행하세요(이후 셀은 이전 변수에 의존합니다).
3. 셀이 실패하면 위 마크다운의 문제 해결 안내를 확인하세요.
4. 노트북을 다시 실행해도 안전합니다: 랩 데이터는 `LlamaIndexLab` 레이블을 사용하며 다시 시드할 수 있습니다.
""",
    1: """## 사전 요구 사항

이 코스를 수강하기 전에 다음을 갖추어야 합니다:

- **그래프 데이터베이스**와 **Neo4j**에 대한 기초 이해(노드, 관계, Cypher `MATCH`)
- **Python** 지식 및 **LlamaIndex** 기초(index, query engine, agent)
- 실행 중인 Neo4j **5.15+** 인스턴스(`NEO4J_SETUP.md` 참고)

### 이 코스에서 사용하는 개념

| 개념 | 이 코스에서의 의미 |
|---------|------------------------|
| **RAG** | 관련 텍스트를 검색한 뒤 해당 컨텍스트와 함께 LLM에 질문 |
| **GraphRAG** | 구조화된 사실을 위해 그래프 탐색을 더한 RAG |
| **Text-to-Cypher** | 자연어에서 LLM이 Cypher 쿼리 작성 |
| **Retriever** | 쿼리에 대해 `NodeWithScore` 항목을 반환하는 LlamaIndex 객체 |
| **Agent** | 도구(Cypher, QA chain)를 단계별로 선택하는 LLM 루프 |

## 코스 개요

| 파트 | 주제 |
|------|--------|
| **3.1** | Neo4j와 LlamaIndex |
| **3.2** | 벡터(Vectors) |
| **3.3** | Text to Cypher |

### 3.1 Neo4j와 LlamaIndex

| 섹션 | 주제 |
|---------|--------|
| 0 | 개발 환경 및 연결 |
| 3.1.1 | Neo4j 통합 (`Neo4jPropertyGraphStore`) |
| 3.1.2 | 스키마 인트로스펙션 및 Cypher 헬퍼 |
| 3.1.3 | LlamaIndex 랩 그래프 시드 |
| 3.1.4 | 간단한 LlamaIndex agent |

### 3.2 벡터

| 섹션 | 주제 |
|---------|--------|
| 3.2.1 | 벡터 검색 (`Neo4jVectorStore`) |
| 3.2.2 | 벡터 retriever (RAG) |
| 3.2.3 | 그래프 검색 (GraphRAG) |
| 3.2.4 | 추가 데이터(선택) |

### 3.3 Text to Cypher

| 섹션 | 주제 |
|---------|--------|
| 3.3.1 | 스키마 인트로스펙션 |
| 3.3.2 | Cypher 생성 (`TextToCypherRetriever`) |
| 3.3.3 | retriever 맞춤 설정 |
| 3.3.4 | retriever로서의 text-to-Cypher |
""",
    2: """---

# Step 0 — 개발 환경

이 섹션은 Python 환경을 준비하고 `.env`에서 비밀 값을 로드한 뒤,
LlamaIndex 구성 요소를 만들기 전에 **Neo4j**와 **LLM**에 연결할 수 있는지 확인합니다.

### 코드 실행 전

1. **`NEO4J_SETUP.md`** 완료 — Aura, Desktop 또는 Docker; URI, 사용자명, 비밀번호 확인
2. **`LLM_MODEL_SETUP.md`** 완료 — Ollama + `ollama_model_runner.py`(권장) 또는 OpenAI
3. `Module_8/.env.example` → `Module_8/.env` 복사 후 자격 증명 입력
4. Neo4j 시작(인스턴스 **Running**) 및 Ollama 사용 시 터미널에서 `ollama serve` 실행

### Step 0에서 하는 일

| Step | 목적 |
|------|---------|
| 0a | Python 패키지 설치 |
| 0b | 경로 및 환경 변수 로드 |
| 0c | Neo4j Bolt 연결 확인 |
| 0d | Ollama runner → LlamaIndex `Settings.llm` 연결 |
| 0e | runner 스모크 테스트(Ollama만) |
""",
    3: """### Step 0a — Python 패키지 설치

**Neo4j driver**, **LlamaIndex** graph/vector 통합 패키지, 그리고 로컬 임베딩용 **sentence-transformers**(섹션 3.2)를 설치합니다.

| 패키지 | 역할 |
|---------|------|
| `neo4j` | 공식 데이터베이스 driver(Bolt 프로토콜) |
| `llama-index-core` | index, retriever, query engine, agent |
| `llama-index-graph-stores-neo4j` | `Neo4jPropertyGraphStore`, `TextToCypherRetriever` |
| `llama-index-vector-stores-neo4jvector` | 벡터 RAG용 `Neo4jVectorStore` |
| `llama-index-embeddings-huggingface` | 로컬 `HuggingFaceEmbedding` |
| `llama-index-llms-openai` | OpenAI LLM(선택적 클라우드 경로) |
| `python-dotenv` | 수동 export 없이 `Module_8/.env` 로드 |
| `sentence-transformers` | HuggingFace 임베딩 백엔드 |

**참고:** 가상 환경당 이 셀을 한 번 실행하세요. 버전 충돌 시 설치 후 커널을 재시작하세요.
""",
    5: """### Step 0b.1 — `Module_8` 디렉터리 확인

Jupyter의 작업 디렉터리는 노트북 실행 방식에 따라 달라집니다:

- 저장소 루트에서 실행 → `Module_8/` 하위 폴더를 감지합니다.
- `Module_8/`에서 실행 → 현재 폴더를 사용합니다.

이후 `load_dotenv(MODULE_DIR / '.env')`를 호출하여 `NEO4J_*`, `LLM_*` 변수를
노트북에 하드코딩하지 않고 모든 셀에서 사용할 수 있게 합니다.
""",
    7: """**예상 출력:** `.../Module_8`로 끝나는 경로.

경로가 잘못되면 `Module_8/` 안에서 **File → Open**을 사용하거나 Jupyter 루트를 조정하세요.
""",
    8: """### Step 0b.2 — Neo4j 연결 설정

이 변수들은 배포 환경과 일치해야 합니다(`NEO4J_SETUP.md` 참고):

| 변수 | 일반적인 로컬(Docker/Desktop) | Aura 클라우드 |
|----------|-------------------------------|------------|
| `NEO4J_URI` | `neo4j://localhost:7687` | `neo4j+s://....databases.neo4j.io` |
| `NEO4J_USERNAME` | `neo4j` | `neo4j` |
| `NEO4J_PASSWORD` | 인스턴스 비밀번호 | Aura 자격 증명 파일에서 확인 |
| `NEO4J_DATABASE` | `neo4j` | `neo4j` |

**보안:** 실제 비밀번호를 Git에 커밋하지 마세요. `.env`만 사용하세요(gitignore 대상).
""",
    10: """### Step 0b.3 — LLM 백엔드 및 선택적 코퍼스 경로

이 노트북은 LLM을 세 가지 방식으로 사용합니다:

1. **Text-to-Cypher** (`TextToCypherRetriever`) — 강한 instruction-following 필요
2. **RAG / GraphRAG 답변** — query engine 및 `Settings.llm`
3. **ReAct agent** — 도구를 사용한 다단계 추론

| `LLM_BACKEND` | 노트북에서 모델을 호출하는 방법 |
|---------------|-----------------------------------|
| `ollama` (기본) | subprocess → `ollama_model_runner.py` → LlamaIndex `CustomLLM` |
| `openai` | `OPENAI_API_KEY`와 함께 `llama_index.llms.openai.OpenAI` |

**Ollama + runner** 경로는 다른 KMOU 모듈과 동일합니다: Jupyter 커널은 가볍게 유지하고
긴 프롬프트는 별도 프로세스에서 실행합니다(`LLM_MODEL_SETUP.md` 참고).

`CORPUS_PATH`는 섹션 3.2.4의 선택적 추가 텍스트를 가리킵니다 — 핵심 랩에는 필요하지 않습니다.
""",
    12: """### Step 0c — Neo4j 연결 확인

공식 `neo4j` driver로 짧은 **Bolt** 세션을 엽니다.
이는 `Neo4jPropertyGraphStore`와 `Neo4jVectorStore`가 사용하는 동일한 Bolt 프로토콜입니다.

**이 셀이 실패하면:**

- `NEO4J_PASSWORD is empty` → `Module_8/.env`를 채우세요.
- `ServiceUnavailable` → 데이터베이스가 실행 중이 아니거나 URI scheme이 잘못됨.
- `Authentication failed` → 비밀번호 불일치(Docker `NEO4J_AUTH`가 `.env`와 일치해야 함).
""",
    14: """**예상 출력:** `Neo4j connection OK` 다음 `연결 확인 완료.`

**Neo4j Browser**에서도 다음으로 확인할 수 있습니다:

```cypher
RETURN "Neo4j connection OK" AS message;
```
""",
    15: """### Step 0d — Ollama runner 헬퍼

LlamaIndex는 `Settings.llm`에 **`LLM`** 객체가 필요합니다. 이 코스의 runner는 stdout에 JSON을 반환하는 **CLI 스크립트**입니다. 다음으로 연결합니다:

1. **`call_ollama_runner()`** — 프롬프트를 임시 파일에 쓰고, subprocess 실행, JSON 파싱.
2. **`OllamaRunnerLLM`** — query engine, retriever, agent에서 사용하는 LlamaIndex **`CustomLLM`**.

이는 **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** 및 **`LLM_MODEL_SETUP.md`**와 동일한 패턴입니다.
""",
    16: """#### Step 0d.1 — `ollama_model_runner.py` 위치 찾기

검색 순서: `Module_8/` → `Module_4/`(fallback) → 현재 디렉터리.
""",
    18: """#### Step 0d.2 — `call_ollama_runner()`

스크립트에 전달되는 매개변수:

| 플래그 | 출처 |
|------|--------|
| `--host` | `OLLAMA_HOST` |
| `--models` | `OLLAMA_MODEL` |
| `--prompt-file` | 전체 프롬프트가 담긴 임시 파일 |
| `--temperature` | `OLLAMA_TEMPERATURE` (결정적 랩을 위해 0) |
| `--max-tokens` | `OLLAMA_MAX_TOKENS` (답변이 잘리면 값을 늘리세요) |

이 함수는 runner가 출력한 JSON에서 `outputs[0].response`를 반환합니다.
""",
    20: """#### Step 0d.3 — LlamaIndex `CustomLLM` 어댑터

- **`OllamaRunnerLLM`**은 **`CustomLLM`**을 상속하고 `complete()`와 `stream_complete()`를 구현합니다.
- 이후 모든 섹션은 **`Settings.llm`**을 사용합니다(query engine, `TextToCypherRetriever`, `ReActAgent`).
""",
    22: """### Step 0d.4 — `Settings.llm` 구성

`Settings.llm`은 다음의 전역 기본값입니다:

- `TextToCypherRetriever`
- `VectorStoreIndex.as_query_engine()`
- `ReActAgent`
""",
    24: """### Step 0e — `ollama_model_runner.py` 스모크 테스트

runner, 모델 이름, Ollama 서비스가 함께 동작하는지 빠르게 확인합니다.
터미널에서 동일한 명령(`Module_8/`에서):

```bash
python ollama_model_runner.py --host http://localhost:11434 \\
  --models llama3.2:3b --prompt "Reply with exactly: Ollama OK" --max-tokens 32
```
""",
    26: """**예상 출력(Ollama):** `Ollama OK`(또는 유사)가 포함된 줄과 `이후 섹션에서 LLM 사용 준비 완료.`

실패하면 섹션 3.3 전에 Ollama를 수정하세요 — text-to-Cypher가 LLM에 가장 민감한 단계입니다.
""",
    27: """---

# 3.1 Neo4j와 LlamaIndex

### 전체 그림

```text
Your app (LlamaIndex)
    │
    ├── Neo4jPropertyGraphStore → schema, text-to-Cypher, graph queries
    ├── Neo4jVectorStore        → embeddings + similarity search
    ├── TextToCypherRetriever   → natural language → Cypher → context
    └── ReActAgent + FunctionTools → agent over the graph
            │
            ▼
      Neo4j Database (Bolt)
```

LlamaIndex Neo4j 통합은 **`llama-index-graph-stores-neo4j`**와
**`llama-index-vector-stores-neo4jvector`**에 있습니다([Neo4j Labs — LlamaIndex](https://neo4j.com/labs/genai-ecosystem/llamaindex/) 참고).
""",
    28: """## 3.1.1 Neo4j 통합 — `Neo4jPropertyGraphStore`

`Neo4jPropertyGraphStore`는 Neo4j용 LlamaIndex property-graph 어댑터입니다:

- **`get_schema_str()`** — `TextToCypherRetriever`용 텍스트 스키마.
- **`structured_query(cypher, params)`** — 지원되는 경우 Cypher 실행.
- **`PropertyGraphIndex`**, retriever, query engine과 함께 사용.

랩 시드용으로 공식 `neo4j` driver의 얇은 **`run_cypher()`** 헬퍼도 유지합니다
(동일 Bolt 연결, 교육 셀에서 명시적 `CREATE` / `MERGE`).
""",
    30: """**예상 출력:** `Neo4jPropertyGraphStore 연결 완료.`

아직 랩 데이터는 생성되지 않습니다 — graph store와 driver만 엽니다.
""",
    31: """### 3.1.1b — `run_cypher()`로 첫 쿼리

Browser의 `RETURN`과 동일하지만, 결과는 Python에서 **딕셔너리 리스트**로 반환됩니다.
agent 도구와 시드 셀 전체에서 이 헬퍼를 사용합니다.
""",
    33: """## 3.1.2 `get_schema_str()`로 스키마 인트로스펙션

Text-to-Cypher(섹션 3.3)는 LLM에 **스키마 텍스트**를 보내 어떤 레이블이 있는지 알려줍니다.

- **`graph_store.get_schema_str()`** — 레이블, 관계, 속성을 인트로스펙션.
- 데이터를 **시드**하거나 **변경**한 뒤 text-to-Cypher 데모 전에 다시 호출하세요.

Neo4j의 스키마가 더 명확할수록(일관된 레이블, 문서화된 속성) 생성 Cypher 품질이 좋아집니다.
""",
    35: """데이터베이스가 비어 있으면 섹션 3.1.3 전까지 스키마 출력이 최소일 수 있습니다.
""",
    36: """## 3.1.3 LlamaIndex 랩 그래프 시드

벡터 검색용 **텍스트 청크**와 함께 **소규모 해운 지식 그래프**를 구축합니다.
모든 랩 노드에는 **`LlamaIndexLab`** 레이블이 있어 안전하게 삭제하거나 필터링할 수 있습니다.

### 데이터 모델(이 랩)

```text
(Document)-[:HAS_CHUNK]->(Chunk)-[:MENTIONS]->(Port|Organization|Canal|...)
   (Port)-[:LOCATED_IN]->(Country)
   (Organization)-[:OPERATES_IN]->(Port)
   (Organization)-[:USES_ROUTE]->(Canal)
```

| 노드 레이블 | 역할 |
|------------|------|
| `Port`, `Organization`, `Canal`, `Country` | Cypher QA용 구조화 엔티티 |
| `Document`, `Chunk` | RAG용 비구조화 텍스트 + 임베딩 |
| `LlamaIndexLab` | 모든 코스 노드의 마커 레이블 |
""",
    37: """### 3.1.3a — 이전 랩 데이터 삭제

노트북을 다시 실행해도 노드가 중복되지 않도록, 새 데이터 삽입 전 `LlamaIndexLab` 노드를 모두 삭제합니다.
**같은 데이터베이스의 다른 그래프는 건드리지 않습니다.**
""",
    39: """### 3.1.3b — 구조화 엔티티

이 Cypher는 항구, Maersk, Panama Canal, 국가 및 관계를 **CREATE**합니다.
속성 `id`는 쿼리와 이후 `MENTIONS` 링크를 위한 안정적인 식별자를 제공합니다.
""",
    41: """**Neo4j Browser에서 확인:**

```cypher
MATCH (o:Organization:LlamaIndexLab)-[r]->(x)
RETURN o.id, type(r), x.id;
```
""",
    42: """### 3.1.3c — 문서 청크

RAG는 노드로 저장된 **짧은 구절**이 필요합니다. 각 청크에는:

- `text` — 섹션 3.2에서 임베딩 및 검색.
- `source` — 출처(여기서는 `course_seed`).
- `id` — 벡터 메타데이터 및 GraphRAG 확장에 연결.

청크 ID는 `llamaindex_` 접두사를 사용합니다. 다른 코스 랩(예: Module 3의 `LangChainLab` 청크)과 Neo4j 데이터베이스를 공유할 때 `:Chunk` 레이블의 `id` 고유 제약을 피하기 위함입니다.
""",
    44: """### 3.1.3d — 청크와 엔티티 연결 (GraphRAG 브리지)

`(Chunk)-[:MENTIONS]->(Entity)`는 **비구조화** 텍스트를 **구조화** 그래프 노드에 연결합니다.
섹션 3.2.3은 벡터 검색 후 이 엣지를 탐색하여 LLM 컨텍스트를 풍부하게 합니다.
""",
    46: """**체크포인트:** **3.1.2**를 다시 실행 — `get_schema_str()`에 `Port`, `Chunk`, `MENTIONS` 등이 보여야 합니다.
""",
    47: """## 3.1.4 간단한 LlamaIndex agent

**agent**는 생각 → **도구** 선택 → 결과 관찰 → 완료까지 반복하는 루프입니다.

두 가지 도구를 등록합니다:

| 도구 | 사용 시점 |
|------|-------------|
| `run_read_cypher` | 사용자가 Cypher를 주거나 원시 행을 원할 때 |
| `ask_graph_in_natural_language` | 열린 질문 → `TextToCypherRetriever`(섹션 3.3) |

> **순서 참고:** 자연어 도구는 섹션 3.3의 `CYPHER_QUERY_ENGINE`이 필요합니다.
> 여기서 agent를 정의할 수 있지만, 데모 셀은 **3.3 이후**에 실행하세요.

> **프로덕션:** 읽기 전용 DB 역할, 쿼리 허용 목록, 생성 Cypher에 대한 사람 검토를 사용하세요.
""",
    48: """### 3.1.4a — 도구 정의

`FunctionTool.from_defaults()`는 Python 함수를 LlamaIndex 도구로 래핑합니다.
ReAct agent는 도구 이름과 설명을 읽고 어떤 도구를 호출할지 결정합니다.
""",
    50: """### 3.1.4b — ReAct agent

**ReAct**(Reason + Act)는 모델을 일반 텍스트로 프롬프트합니다:
`Thought` → `Action` → `Action Input` → `Observation` → … → `Final Answer`.

LlamaIndex **`ReActAgent`**도 동일한 텍스트 기반 ReAct 루프를 사용하며,
`ollama_model_runner.py`(자유 텍스트 응답, 구조화된 tool JSON 아님)와 잘 맞습니다.

| 매개변수 | 값 | 이유 |
|-----------|-------|-----|
| `max_iterations` | 5 (`.run()`에 전달) | 무한 도구 루프 방지 |
| `verbose` | True | 노트북 출력에 추론 과정 표시 |
""",
    52: """### 3.1.4c — agent 미리보기

`CYPHER_QUERY_ENGINE`이 있을 때까지 이 셀은 **건너뜁니다**. 섹션 3.3 이후 **3.3.4b**를 다시 실행하면 전체 데모를 볼 수 있습니다.
""",
    54: """---

# 3.2 벡터(Vectors)

### 그래프 코스에서 벡터를 쓰는 이유?

많은 GenAI 앱은 다음을 결합합니다:

- **벡터 검색** — 의미적 유사도로 관련 *텍스트* 찾기.
- **그래프 탐색** — 관계로 관련 *엔티티*와 *사실* 찾기.

Neo4j 5.x는 노드에 임베딩을 저장하고 **vector index**로 쿼리할 수 있습니다.
**`Neo4jVectorStore`**(LlamaIndex)는 인덱스를 만들고 **`VectorStoreIndex`** retriever를 구동합니다.

```text
User question
    → embed question
    → vector index (top-k Chunk nodes)
    → optional graph expansion (MENTIONS, OPERATES_IN, ...)
    → LLM answer
```
""",
    55: """## 3.2.1 `Neo4jVectorStore`로 벡터 검색

### 임베딩 모델

Hugging Face를 통해 **`sentence-transformers/all-MiniLM-L6-v2`**(384차원)를 사용합니다.

- **장점:** API 키 불필요; 로컬 실행.
- **단점:** 첫 실행 시 모델 가중치 다운로드(**최초 1회 인터넷 필요**).

프로덕션 대안: OpenAI `text-embedding-3-small`, Cohere 등.
""",
    57: """**예상 출력:** `임베딩 차원: 384`

다운로드가 실패하면 네트워크/방화벽을 확인하거나 `huggingface-cli`로 모델을 미리 받으세요.
""",
    58: """### 3.2.1b — LlamaIndex `TextNode`로 청크 로드

Neo4j에서 `Chunk` 노드를 읽어 **`TextNode(text=..., metadata=...)`**로 매핑합니다.
메타데이터 `chunk_id`는 이후 GraphRAG 확장에 필요합니다.
""",
    60: """### 3.2.1c — `Neo4jVectorStore`로 `VectorStoreIndex` 생성

| 구성 요소 | 이 랩 |
|-----------|----------|
| Vector store | `Neo4jVectorStore` |
| Index | `VectorStoreIndex` |
| Embedding dim | `384` (MiniLM-L6-v2) |

`VectorStoreIndex`는 각 `TextNode`를 **임베딩**하고 `Neo4jVectorStore`를 통해 벡터를 저장합니다.
이 셀을 다시 실행하면 벡터 항목이 중복될 수 있습니다 — 새 랩 DB를 사용하거나 vector index를 삭제하세요.
""",
    62: """### 3.2.1d — 유사도 검색

`as_retriever(similarity_top_k=2).retrieve(query)`는 질의를 임베딩하고 top-k `NodeWithScore`를 반환합니다.
Rotterdam / Europe 질문과 결과를 비교 — Rotterdam 청크가 상위에 있어야 합니다.
""",
    64: """## 3.2.2 벡터 retriever (RAG)

### retriever란?

LlamaIndex에서 **retriever**는 `NodeWithScore` 객체를 반환합니다.
**`RetrieverQueryEngine`**은 하나의 `query()` 호출에서 검색 + 합성을 결합합니다.

### 최소 RAG 파이프라인

1. **검색** — 사용자 질문과 유사한 청크 노드(`VectorStoreIndex` retriever).
2. **합성** — 검색된 노드를 근거로 `Settings.llm`으로 답변 생성.
""",
    65: """### 3.2.2a — `as_retriever()`

`similarity_top_k=3`은 질의당 세 개 청크를 반환합니다. `k`를 늘리면 컨텍스트가 넓어집니다
(토큰 증가, 비용/지연 증가).
""",
    67: """### 3.2.2b — `as_query_engine()`로 RAG

`VectorStoreIndex.as_query_engine()`은 **`Settings.llm`**을 사용해 검색 + 합성을 결합합니다.
이는 **`Neo4jVectorStore`** 위의 관용적인 LlamaIndex RAG 패턴입니다.
""",
    69: """**팁:** 답변이 컨텍스트를 무시하면 temperature를 낮추거나, `k`를 늘리거나, 더 큰 Ollama 모델(`llama3.1:8b`)을 사용하세요.
""",
    70: """## 3.2.3 그래프 검색 (GraphRAG)

### 벡터 전용 RAG의 한계

유사도 검색은 **올바른 텍스트**를 반환할 수 있지만, 청크에 그 사실이 문자 그대로 없으면
**명시적 엣지**(예: `Maersk -[:USES_ROUTE]-> Panama_Canal`)를 놓칠 수 있습니다.

### GraphRAG 패턴(이 랩)

1. top-k `Chunk` 노드를 벡터 검색.
2. 각 검색 노드에서 `chunk_id` 메타데이터 읽기.
3. Cypher 실행: `Chunk -[:MENTIONS]-> Entity` 및 엔티티 관계 1-hop.
4. **청크 텍스트 + 그래프 사실**을 LLM에 전달.
""",
    71: """### 3.2.3a — `graph_context_for_chunks()` 및 `graphrag_retrieve()`

이 함수들은 **교육용 헬퍼**입니다 — 프로덕션에서는 `neo4j-graphrag`나
Neo4j Labs의 패키지 retriever를 사용할 수 있습니다.
""",
    73: """### 3.2.3b — `Settings.llm`으로 GraphRAG 답변

청크 텍스트와 그래프 사실을 하나의 프롬프트로 결합한 뒤 **`Settings.llm.complete()`**를 호출합니다.
""",
    75: """**비교:** 동일 질문을 **3.2.2b**(벡터 전용 RAG)와 이 셀에서 실행해 보세요.
GraphRAG는 표현이 달라도 `USES_ROUTE` 경로를 드러내야 합니다.
""",
    76: """## 3.2.4 추가 데이터(선택)

네 개 시드 청크를 넘어 확장하려면:

1. **`data/dbpedia_maritime_corpus.txt`**(또는 `dbpedia_course_corpus.txt`) 파싱.
2. 새 `Chunk` 노드와 선택적 `MENTIONS` 엣지를 `MERGE`.
3. 새 `TextNode`로 `VectorStoreIndex` 재구축.

라이선스 및 재구축 스크립트는 **`data/DATASETS.md`**를 참고하세요.

아래 셀은 두 기사만 **미리보기** — 인덱스를 재구축하지 않습니다.
""",
    78: """---

# 3.3 Text to Cypher

### `TextToCypherRetriever` 동작 방식

```text
User question
    → LLM + graph_store schema → Cypher query
    → Execute on Neo4j → result rows
    → Format rows into retrieved TextNode context
```

retriever를 **`RetrieverQueryEngine`**으로 감싸면 최종 자연어 답변 단계가 추가됩니다.
품질은 스키마 명확성, 모델 크기, 질문 표현에 따라 달라집니다.
""",
    79: """## 3.3.1 Cypher 생성용 스키마

chain을 만들기 전에:

1. **`get_schema_str()`** — LLM에 보낼 스키마 텍스트 미리보기.
2. 레이블별 **노드 수** — `LlamaIndexLab` 데이터 존재 확인.

개수가 0이면 섹션 **3.1.3**을 다시 실행하세요.
""",
    81: """## 3.3.2 Text-to-Cypher retriever + query engine

### 안전 참고

생성된 Cypher가 이론상 데이터를 **쓸** 수 있습니다. 이 코스는 **일회용 랩 그래프**만 사용합니다.
프로덕션: 읽기 전용 DB 역할, `cypher_validator`, 쿼리 허용 목록.

### 구성 요소

| 구성 요소 | 역할 |
|-----------|------|
| `TextToCypherRetriever` | NL → Cypher → 그래프 행을 노드로 |
| `RetrieverQueryEngine` | retriever + `Settings.llm` → 최종 답변 |
""",
    83: """### 3.3.2b — 예제 질문

응답에 **Netherlands**와 **Singapore**의 항구가 언급되어야 합니다.
Cypher가 실패하면 검색된 노드 텍스트(생성된 쿼리 포함)를 확인하고 Browser와 비교하세요.
""",
    85: """## 3.3.3 Cypher 생성 맞춤 설정

**`TextToCypherRetriever`**의 주요 옵션:

| 옵션 | 효과 |
|--------|--------|
| `llm` | Cypher 생성 모델(기본값 `Settings.llm`) |
| `text_to_cypher_template` | `{schema}`와 `{question}`이 있는 프롬프트 |
| `response_template` | Cypher 결과가 노드 텍스트로 변환되는 방식 |
| `cypher_validator` | 안전하지 않거나 잘못된 Cypher를 거부하는 callable |

아래에서는 LLM이 **`LlamaIndexLab`** 노드를 선호하도록 랩 힌트를 추가합니다.
""",
    87: """## 3.3.4 retriever로서의 text-to-Cypher

일부 아키텍처는 **그래프 QA를 검색**으로 취급합니다:

- 하류 RAG는 **벡터 청크** + **Cypher 결과 텍스트**를 병합.
- agent는 **컨텍스트**만 필요할 때 전체 QA chain 대신 retriever를 호출.

`TextToCypherRetriever.retrieve()`는 이미 **`NodeWithScore`** 객체를 반환합니다.
하류 RAG는 합성 전에 이 노드를 벡터 청크와 병합할 수 있습니다.
""",
    89: """### 3.3.4b — live `CYPHER_QUERY_ENGINE`으로 agent 재실행

이제 `ask_graph_in_natural_language`가 query engine을 호출할 수 있습니다. verbose ReAct 단계와
**Maersk** 및 **Rotterdam**을 언급하는 최종 답변을 기대하세요.

**참고:** 로컬 Ollama에서는 30–90초 걸릴 수 있습니다 — 다단계 LLM 호출에서는 정상입니다.
""",
    91: """---

## 요약

| 주제 | 핵심 API | 연습 내용 |
|-------|---------|-------------------|
| Neo4j + LlamaIndex | `Neo4jPropertyGraphStore` | 연결, 스키마, 그래프 쿼리 |
| 랩 데이터 | Cypher `CREATE` / `MERGE` | 해운 그래프 + 청크 + `MENTIONS` |
| Vector RAG | `Neo4jVectorStore` + `VectorStoreIndex` | 임베딩, 인덱싱, 검색, 답변 |
| GraphRAG | 맞춤 확장 + `Settings.llm` | 벡터 + 관계 컨텍스트 |
| Text to Cypher | `TextToCypherRetriever` | NL → Cypher → context → answer |
| Agent | `ReActAgent` + `FunctionTool` | 그래프 위 도구 선택 |

### 문제 해결 빠른 참조

| 증상 | 확인 사항 |
|---------|-------|
| Neo4j 연결 오류 | `NEO4J_SETUP.md`, 인스턴스 실행, `.env` 비밀번호 |
| Ollama runner 오류 | `ollama serve`, `ollama pull`, `LLM_MODEL_SETUP.md` |
| 빈 벡터 검색 결과 | 3.1.3c 및 3.2.1c 재실행 |
| 잘못된/유효하지 않은 Cypher | `get_schema_str()`, 더 큰 모델, 맞춤 template |
| Agent 파싱 오류 | `verbose=True`로 재실행; `llama3.1:8b` 시도 |

### 다음 단계

- **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** — LLM으로 비구조화 텍스트에서 그래프 구축.
- **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** — LangChain 오케스트레이션으로 동일 랩 주제.
- **`VectorContextRetriever`** + **`TextToCypherRetriever`**를 결합한 전체 GraphRAG([Neo4j Labs](https://neo4j.com/labs/genai-ecosystem/genai-frameworks/llamaindex-agents/) 참고).
- 코퍼스 청크 추가(섹션 3.2.4) 및 `similarity_top_k`, 임베딩, 프롬프트 튜닝.
- 프로덕션 강화: 읽기 전용 DB 사용자, `cypher_validator`, 생성 Cypher 관측 가능성.

### 참고 자료

- [Property Graph Index guide](https://developers.llamaindex.ai/python/framework/module_guides/indexing/lpg_index_guide/)
- [Neo4j vector store (LlamaIndex)](https://developers.llamaindex.ai/python/framework/integrations/vector_stores/neo4jvectordemo/)
- [Neo4j GenAI — LlamaIndex](https://neo4j.com/labs/genai-ecosystem/genai-frameworks/llamaindex-agents/)
""",
}

# Per-cell print-only replacements (old line fragment -> new line fragment)
PRINT_REPLACEMENTS: dict[int, list[tuple[str, str]]] = {
    6: [("print('Module directory:', MODULE_DIR)", "print('모듈 디렉터리:', MODULE_DIR)")],
    9: [
        ("print('Neo4j database:', NEO4J_DATABASE)", "print('Neo4j 데이터베이스:', NEO4J_DATABASE)"),
    ],
    11: [
        ("print('LLM backend:', LLM_BACKEND)", "print('LLM 백엔드:', LLM_BACKEND)"),
        (
            "print('Corpus for vectors:', CORPUS_PATH.name, '| exists:', CORPUS_PATH.is_file())",
            "print('벡터용 코퍼스:', CORPUS_PATH.name, '| 존재:', CORPUS_PATH.is_file())",
        ),
        ("print('Ollama host:', OLLAMA_HOST)", "print('Ollama 호스트:', OLLAMA_HOST)"),
        ("print('Ollama model:', OLLAMA_MODEL)", "print('Ollama 모델:', OLLAMA_MODEL)"),
    ],
    13: [
        ("print('Connectivity check passed.')", "print('연결 확인 완료.')"),
    ],
    23: [
        ("print(f'Using OpenAI: {OPENAI_MODEL}')", "print(f'OpenAI 사용: {OPENAI_MODEL}')"),
        (
            "print(f'Using Ollama runner: {OLLAMA_MODEL} @ {OLLAMA_HOST}')",
            "print(f'Ollama runner 사용: {OLLAMA_MODEL} @ {OLLAMA_HOST}')",
        ),
        (
            "print('Ensure Ollama is running: ollama serve')",
            "print('Ollama가 실행 중인지 확인하세요: ollama serve')",
        ),
    ],
    25: [
        (
            "print('Ollama runner smoke test:', smoke[:120])",
            "print('Ollama runner 스모크 테스트:', smoke[:120])",
        ),
        (
            "print('Warning: unexpected reply — verify model and OLLAMA_HOST')",
            "print('경고: 예상과 다른 응답 — 모델과 OLLAMA_HOST를 확인하세요')",
        ),
        (
            "print('LLM ready for later sections.')",
            "print('이후 섹션에서 LLM 사용 준비 완료.')",
        ),
        ("print('Skipped — OpenAI backend')", "print('건너뜀 — OpenAI 백엔드')"),
    ],
    29: [
        (
            "print('Neo4jPropertyGraphStore connected.')",
            "print('Neo4jPropertyGraphStore 연결 완료.')",
        ),
    ],
    34: [
        (
            "print('... [truncated for display]')",
            "print('... [표시용으로 잘림]')",
        ),
    ],
    38: [
        (
            "print('Cleared prior LlamaIndexLab subgraph.')",
            "print('기존 LlamaIndexLab 서브그래프 삭제 완료.')",
        ),
    ],
    40: [
        ("print('Structured graph seeded.')", "print('구조화 그래프 시드 완료.')"),
    ],
    43: [
        ("print(f'Seeded {len(chunks)} chunks.')", "print(f'{len(chunks)}개 청크 시드 완료.')"),
    ],
    45: [
        (
            "print('Chunk–entity links created.')",
            "print('청크-엔티티 링크 생성 완료.')",
        ),
    ],
    49: [
        ("print('Tools:', [t.metadata.name for t in agent_tools])", "print('도구:', [t.metadata.name for t in agent_tools])"),
    ],
    51: [
        (
            "print('ReActAgent ready (run Section 3.3 before natural-language tool works).')",
            "print('ReActAgent 준비 완료(자연어 도구는 섹션 3.3 실행 후 동작).')",
        ),
    ],
    53: [
        (
            "print('Skip until CYPHER_QUERY_ENGINE is defined in Section 3.3 (then run cell 3.3.4b).')",
            "print('CYPHER_QUERY_ENGINE이 섹션 3.3에서 정의될 때까지 건너뜁니다(이후 셀 3.3.4b 실행).')",
        ),
    ],
    56: [
        (
            "print('Embedding dimension:', len(sample_vec))",
            "print('임베딩 차원:', len(sample_vec))",
        ),
    ],
    59: [
        (
            "print('TextNodes for indexing:', len(chunk_nodes))",
            "print('인덱싱용 TextNode:', len(chunk_nodes))",
        ),
    ],
    61: [
        (
            "print('VectorStoreIndex ready (Neo4jVectorStore).')",
            "print('VectorStoreIndex 준비 완료 (Neo4jVectorStore).')",
        ),
    ],
    63: [
        ("print('Query:', query)", "print('질의:', query)"),
    ],
    66: [
        (
            "print('Retrieved', len(retrieved), 'chunks')",
            "print('검색됨', len(retrieved), '개 청크')",
        ),
    ],
    72: [
        (
            "print('Graph context preview:\\n', sample['graph_context'][:500])",
            "print('그래프 컨텍스트 미리보기:\\n', sample['graph_context'][:500])",
        ),
    ],
    77: [
        (
            "print('Optional corpus sample:', [a['title'] for a in extra])",
            "print('선택 코퍼스 샘플:', [a['title'] for a in extra])",
        ),
        (
            "print('Optional corpus not found:', CORPUS_PATH)",
            "print('선택 코퍼스를 찾을 수 없음:', CORPUS_PATH)",
        ),
    ],
    80: [
        (
            "print('Schema preview:', graph_store.get_schema_str()[:600], '...')",
            "print('스키마 미리보기:', graph_store.get_schema_str()[:600], '...')",
        ),
        (
            "print('LlamaIndexLab nodes by label combination:')",
            "print('레이블 조합별 LlamaIndexLab 노드:')",
        ),
    ],
    82: [
        (
            "print('TextToCypherRetriever + query engine ready.')",
            "print('TextToCypherRetriever + query engine 준비 완료.')",
        ),
    ],
    84: [
        ("print('Answer:', qa_response)", "print('답변:', qa_response)"),
        (
            "print('Retriever context preview:', retrieved_ctx[0].text[:500] if retrieved_ctx else '(empty)')",
            "print('Retriever 컨텍스트 미리보기:', retrieved_ctx[0].text[:500] if retrieved_ctx else '(비어 있음)')",
        ),
    ],
    88: [
        (
            "print('Retrieved nodes:', len(cypher_nodes))",
            "print('검색된 노드:', len(cypher_nodes))",
        ),
    ],
}


def _to_source(text: str) -> list[str]:
    if not text:
        return []
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] = lines[-1] + "\n"
    return lines


def build() -> None:
    with SRC.open(encoding="utf-8") as f:
        nb = json.load(f)

    ko_nb = copy.deepcopy(nb)

    for idx, text in MARKDOWN_KO.items():
        cell = ko_nb["cells"][idx]
        if cell["cell_type"] != "markdown":
            raise ValueError(f"Cell {idx} is not markdown")
        cell["source"] = _to_source(text)
        cell["outputs"] = []
        cell["execution_count"] = None

    for idx, replacements in PRINT_REPLACEMENTS.items():
        cell = ko_nb["cells"][idx]
        if cell["cell_type"] != "code":
            raise ValueError(f"Cell {idx} is not code")
        src = "".join(cell["source"])
        for old, new in replacements:
            if old not in src:
                raise ValueError(f"Cell {idx}: missing print fragment:\n{old}")
            src = src.replace(old, new, 1)
        cell["source"] = _to_source(src.rstrip("\n"))
        cell["outputs"] = []
        cell["execution_count"] = None

    # Clear outputs from all other code cells for a clean KO notebook
    for cell in ko_nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None

    with DST.open("w", encoding="utf-8") as f:
        json.dump(ko_nb, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print(f"Wrote {DST}")


if __name__ == "__main__":
    build()
