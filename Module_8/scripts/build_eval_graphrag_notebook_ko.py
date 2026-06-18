#!/usr/bin/env python3
"""Build Korean Module_5 GraphRAG evaluation notebook from the English source."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Module_5_Evaluating_GraphRAG_with_RAGAS.ipynb"
DST = ROOT / "Module_5_Evaluating_GraphRAG_with_RAGAS_KO.ipynb"

MARKDOWN_KO: dict[int, str] = {
    0: """# RAGAS로 GraphRAG 평가



**코스 모듈:** Module 8

**대상:** `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`를 완료했거나(또는 병행 실행 중인) 초급 학습자



## 코스 설명



**Neo4j** 위에 구축한 **GraphRAG** 애플리케이션의 출력을 평가하고 **벡터 전용 RAG** baseline과 비교합니다



**학습 내용:**



1. 평가용 **Neo4j vector RAG** 및 **GraphRAG** 답변 파이프라인 연결

2. 해운 랩 그래프용 **ground-truth 질문 세트** 구축

3. **RAGAS**로 **정확도** 측정 (`faithfulness`, `answer_relevancy`)

4. RAG와 GraphRAG 간 **지연 시간(latency)** 및 **토큰 비용** 비교

5. 낮은 점수 샘플 검토 및 retrieval 설정 반복 개선



> **언어:** 이 노트북의 안내 텍스트는 **한국어**입니다. 기술 용어는 필요 시 영어를 병기합니다.



> **설정(코드 실행 전 필수):** **`NEO4J_SETUP.md`**와 **`LLM_MODEL_SETUP.md`**를 완료하세요.

> 로컬 LLM의 경우 `ollama serve`를 실행하고 LLM 가이드에 설명된 **`ollama_model_runner.py`**를 사용하세요.



### 이 노트북 사용법



1. 각 **코드** 셀을 실행하기 전에 위 **마크다운** 셀을 읽으세요.

2. Step 0부터 **순서대로** 셀을 실행하세요.

3. **사전 조건:** LangChain 랩 그래프가 Neo4j에 존재해야 합니다(동반 노트북 섹션 3.1.3 및 3.2). Step 1에서 이를 확인합니다.

4. 노트북을 다시 실행해도 안전합니다: 평가 출력은 `Module_8/outputs/eval_graphrag/`에 저장됩니다.
""",
    1: """## 사전 요구 사항



이 코스를 수강하기 전에 다음을 갖추어야 합니다:



- **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** 완료(또는 실행 준비) — 특히:

  - `LangChainLab` 노드 시드(항구, Maersk, Panama Canal, 청크)

  - Neo4j 벡터 인덱스 `langchain_lab_chunk_index` 구축

- **RAG**, **GraphRAG**, **평가 지표(evaluation metrics)**에 대한 기초 이해

- Python, Jupyter, 실행 중인 **Neo4j 5.15+** 인스턴스



### 이 코스에서 사용하는 개념



| 개념 | 이 코스에서의 의미 |

|---------|------------------------|

| **Vector RAG** | 임베딩 유사도로 top-k 텍스트 청크를 검색한 뒤 답변 생성 |

| **GraphRAG** | 생성 전 벡터 검색 + 그래프 확장(`MENTIONS`, `USES_ROUTE`, …) |

| **Ground truth** | 각 평가 질문에 대한 참조 답변 |

| **Faithfulness** | RAGAS 지표: 답변이 검색된 컨텍스트로 뒷받침되는가? |

| **Answer relevancy** | RAGAS 지표: 답변이 질문에 부합하는가? |

| **Latency** | 질문당 실제 경과 시간(검색 + 생성) |

| **Cost proxy** | Ollama의 토큰 수(`eval_count`) 또는 호스팅 모델의 API 사용량 |



## 코스 개요



| Step | 주제 |

|------|--------|

| **0** | 환경, Neo4j, LLM, RAGAS 의존성 |

| **1** | 랩 그래프 확인 및 벡터 인덱스 재연결 |

| **2** | vector RAG 및 GraphRAG 답변 함수 구축 |

| **3** | 해운 랩용 ground-truth 데이터셋 |

| **4** | 두 파이프라인 실행 및 시간/토큰 통계 수집 |

| **5** | RAGAS로 채점 |

| **6** | 시간, 비용, 정확도 비교 |

| **7** | 실패 사례 검토 및 반복 개선 |

| **8** | 아티팩트 저장 및 체크리스트 |
""",
    2: """---



# Step 0 — 개발 환경



이 섹션은 Python 패키지를 준비하고 `.env`를 로드한 뒤 **Neo4j**와 **LLM**에 연결할 수 있는지 확인합니다.



### 코드 실행 전



1. **`NEO4J_SETUP.md`** 완료 — Aura, Desktop 또는 Docker; URI, 사용자명, 비밀번호 확인

2. **`LLM_MODEL_SETUP.md`** 완료 — Ollama + `ollama_model_runner.py`(권장) 또는 OpenAI

3. `Module_8/.env.example` → `Module_8/.env` 복사 후 자격 증명 입력

4. Neo4j 시작 및(Ollama 사용 시) 터미널에서 `ollama serve` 실행

5. 랩 그래프와 벡터 인덱스가 존재하도록 **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** 섹션 **3.2.3**까지 실행
""",
    3: """### Step 0a — Python 패키지 설치



평가용 **RAGAS**와 **datasets**를 추가하고, 동반 노트북과 동일한 Neo4j / LangChain 스택을 사용합니다.



| 패키지 | 역할 |

|---------|------|

| `ragas` | Faithfulness, answer relevancy 및 기타 RAG 지표 |

| `datasets` | RAGAS용 Hugging Face `Dataset` 형식 |

| `langchain-neo4j` | `Neo4jGraph`, `Neo4jVector` |

| `pandas`, `tqdm` | 배치 평가 중 테이블 및 진행 표시줄 |



**버전 참고(중요):**

- **`langchain-community>=0.4.2`** 유지 — `langchain-experimental` 및 다른 Module 8 노트북에 필요합니다.
- RAGAS 수정을 위해 `langchain-community`를 **다운그레이드하지 마세요**(pip 충돌이 발생할 수 있음).
- `ragas` 0.4.x는 제거된 VertexAI 경로를 import합니다; 이 노트북은 RAGAS import 전 **Step 5a.0에서 shim**을 적용합니다.
- Ollama 랩에는 `langchain-google-vertexai`가 **필요하지 않습니다**.
""",
    5: """**예상 출력(Step 0a):** 빨간 ERROR 줄 **없이** `Note: you may need to restart the kernel...` 메시지.



`langchain-community 0.3.x` 충돌이 계속되면 이 셀을 한 번 더 실행하세요(`langchain-community`를 `>=0.4.2`로 업그레이드), 그다음 **커널을 재시작**하고 Step 0b부터 계속하세요.
""",
    6: """**참고:** 가상 환경당 이 셀을 한 번 실행하세요. 버전 충돌 시 설치 후 커널을 재시작하세요.



**예상 출력:** 패키지 설치 메시지(또는 `Requirement already satisfied`). 오류 없음.
""",
    7: """### Step 0b.1 — `Module_8` 디렉터리 확인 및 `.env` 로드



Jupyter의 작업 디렉터리는 노트북 실행 방식에 따라 달라집니다:



- 저장소 루트에서 실행 → `Module_8/` 하위 폴더를 감지합니다.

- `Module_8/`에서 실행 → 현재 폴더를 사용합니다.



이후 `load_dotenv(MODULE_DIR / '.env')`를 호출하여 `NEO4J_*`와 `LLM_*` 변수를 노트북에 하드코딩하지 않고 모든 셀에서 사용할 수 있게 합니다.



모든 저장 단계에 알려진 폴더가 있도록 **`outputs/eval_graphrag/`**를 미리 생성합니다.
""",
    9: """**예상 출력:** `.../Module_8`로 끝나는 경로와 그 아래 평가 출력 디렉터리.



경로가 잘못되면 `Module_8/` 안에서 **File → Open**을 사용하거나 Jupyter 루트를 조정하세요.
""",
    10: """### Step 0b.2 — Neo4j 연결 설정



이 변수들은 배포 환경과 일치해야 합니다(`NEO4J_SETUP.md` 참고):



| 변수 | 일반적인 로컬(Docker/Desktop) | Aura 클라우드 |

|----------|-------------------------------|------------|

| `NEO4J_URI` | `neo4j://localhost:7687` | `neo4j+s://....databases.neo4j.io` |

| `NEO4J_USERNAME` | `neo4j` | `neo4j` |

| `NEO4J_PASSWORD` | 인스턴스 비밀번호 | Aura 자격 증명 파일에서 확인 |

| `NEO4J_DATABASE` | `neo4j` | `neo4j` |



**보안:** 실제 비밀번호를 Git에 커밋하지 마세요. `.env`만 사용하세요(gitignore 대상).



**문제 해결:**



- `NEO4J_PASSWORD is empty` → `Module_8/.env.example`을 `.env`로 복사하고 값을 입력하세요.

- Docker 사용자: `.env`의 비밀번호가 `NEO4J_AUTH`와 일치해야 합니다(`NEO4J_SETUP.md` 옵션 C 참고).
""",
    12: """### Step 0b.3 — LLM 백엔드 및 평가 설정



이 노트북은 **세 곳**에서 LLM을 사용합니다:



| 사용 사례 | 객체 | 이유 |

|----------|--------|-----|

| RAG / GraphRAG 답변 | `chat_llm` 또는 `call_ollama_runner()` | 평가 대상 최종 답변 생성 |

| RAGAS 채점 | `ragas_llm` | faithfulness 및 relevancy 판정 |

| 벡터 검색 | `embeddings` | LangChain 랩 인덱스와 동일한 모델 |



| `LLM_BACKEND` | 노트북에서 모델을 호출하는 방법 |

|---------------|-----------------------------------|

| `ollama` (기본) | subprocess → `ollama_model_runner.py` → Ollama HTTP API |

| `openai` | `OPENAI_API_KEY`와 함께 `ChatOpenAI` |



**평가 전용 설정:**



- **`EVAL_RETRIEVAL_K`**(기본값 `3`) — 각 retriever가 반환하는 청크 수. `k`가 높을수록 컨텍스트 증가, 프롬프트 길어짐, 실행 느려짐. 공정한 벤치마크를 위해 **동일한** `k`로 파이프라인을 비교합니다.
""",
    14: """### Step 0c — Neo4j 연결 확인



공식 `neo4j` driver로 짧은 **Bolt** 세션을 엽니다. LangChain의 `Neo4jGraph`가 내부적으로 사용하는 동일한 프로토콜입니다.



**이 셀이 실패하면:**



| 오류 | 해결 |

|-------|-----|

| `NEO4J_PASSWORD is empty` | `Module_8/.env` 입력 |

| `ServiceUnavailable` | 데이터베이스 미실행 또는 잘못된 URI scheme |

| `Authentication failed` | 비밀번호 불일치(Docker `NEO4J_AUTH`가 `.env`와 일치해야 함) |
""",
    16: """**예상 출력:** `Neo4j connection OK` 다음 `연결 확인 완료.`



**Neo4j Browser**에서도 확인할 수 있습니다(Desktop/Docker의 경우 `http://localhost:7474`):



```cypher

RETURN "Neo4j connection OK" AS message;

```
""",
    17: """### Step 0d — Ollama runner 헬퍼



LangChain은 모델 객체(`LLM`, `BaseChatModel`)를 기대합니다. 이 코스의 runner는 stdout에 JSON을 반환하는 **CLI 스크립트**입니다. 다음으로 연결합니다:



1. **`call_ollama_runner()`** — 프롬프트를 임시 파일에 쓰고, subprocess 실행, JSON 파싱.

2. **`OllamaRunnerLLM`** — 클래식 LLM 인터페이스(여기서는 많이 쓰이지 않음, 일관성 유지).

3. **`OllamaRunnerChatModel`** — chat 메시지를 기대하는 RAG 스타일 chain에서 사용.



이 평가 노트북은 runner 래퍼를 **확장**하여 운영 지표를 캡처합니다:



| 필드 | 의미 |

|-------|---------|

| `latency_sec` | subprocess 호출의 실제 경과 시간 |

| `eval_count` | Ollama 출력 토큰 — 로컬 모델의 **비용 proxy** |



Ollama 설치, 모델 pull, 터미널에서 runner 실행은 **`LLM_MODEL_SETUP.md`**를 참고하세요.
""",
    18: """#### Step 0d.1 — import 및 `ollama_model_runner.py` 위치 찾기



검색 순서: `Module_8/` → `Module_4/`(fallback) → 현재 디렉터리.



이후 단계에서 평가 테이블을 만들고 배치 실행 중 진행 표시줄을 표시하므로 여기서 **`pandas`**와 **`tqdm`**을 import합니다.
""",
    20: """#### Step 0d.2 — 시간 및 토큰 통계가 포함된 `call_ollama_runner()`



스크립트에 전달되는 매개변수:



| 플래그 | 출처 |

|------|--------|

| `--host` | `OLLAMA_HOST` |

| `--models` | `OLLAMA_MODEL` |

| `--prompt-file` | 전체 프롬프트가 담긴 임시 파일 |

| `--temperature` | `OLLAMA_TEMPERATURE` (결정적 랩을 위해 0) |

| `--max-tokens` | `OLLAMA_MAX_TOKENS` (답변이 잘리면 값을 늘리세요) |



LangChain 랩 노트북과 달리 이 함수는 Step 4와 6에서 질문별 지연 시간 및 토큰 사용량을 집계할 수 있도록 **딕셔너리**를 반환합니다(문자열만 반환하지 않음).



**왜 subprocess인가?** Jupyter 커널을 가볍게 유지합니다; 긴 프롬프트는 별도 프로세스에서 실행됩니다(다른 KMOU 모듈과 동일한 패턴).
""",
    22: """#### Step 0d.3 — LangChain 어댑터 클래스



- **`OllamaRunnerLLM`**은 클래식 LLM chain용 `_call(prompt) → str`을 구현합니다.

- **`OllamaRunnerChatModel`**은 메시지 목록을 하나의 프롬프트 문자열로 평탄화합니다(이 코스에는 충분; 프로덕션 앱은 네이티브 chat API를 선호할 수 있음).



이 어댑터는 **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`**와 동일하여 Module 8 노트북 전반에서 일관된 패턴을 보여줍니다.
""",
    24: """#### Step 0d.4 — `chat_llm` 및 `ragas_llm` 인스턴스화



| 변수 | 사용처 |

|----------|----------|

| `chat_llm` | 선택적 OpenAI 직접 경로; Ollama 답변은 지표용 `call_ollama_runner()` 사용 |

| `ragas_llm` | RAGAS 지표 계산(행마다 자체 LLM 호출) |



**Ollama에서 LLM 객체가 두 개인 이유?**



- RAGAS는 Ollama의 **OpenAI 호환** 엔드포인트(`{OLLAMA_HOST}/v1`)를 가리키는 HTTP 클라이언트(`ChatOpenAI`)를 기대합니다.

- RAG 답변 함수는 runner JSON에서 `eval_count`와 정확한 지연 시간을 캡처하기 위해 **`call_ollama_runner()`**를 사용합니다.



두 경로 모두 **동일한 모델 이름**을 사용하면 평가가 비교 가능해지지만, RAGAS는 답변 생성 외에 추가 LLM 호출을 합니다.
""",
    26: """#### Step 0d.5 — RAGAS 및 Neo4jVector 재연결용 임베딩



**`sentence-transformers/all-MiniLM-L6-v2`**(384차원)를 사용합니다 — LangChain 랩 노트북과 동일한 기본값입니다.



| 소비자 | 임베딩이 중요한 이유 |

|----------|----------------------|

| **Neo4jVector** | 인덱스 구축 시 사용한 모델과 일치해야 함(Step 1c) |

| **RAGAS `answer_relevancy`** | 생성된 답변과 합성 질문을 임베딩하여 유사도 채점 |



벡터 인덱스를 다른 모델로 재구축한 경우에만 env var `RAG_EMBED_MODEL`로 재정의하세요.



**첫 실행:** Hugging Face에서 모델 가중치 다운로드(최초 1회 인터넷 필요).
""",
    28: """### Step 0e — `ollama_model_runner.py` 스모크 테스트



전체 평가 배치를 실행하기 **전에** runner, 모델 이름, Ollama 서비스가 함께 동작하는지 빠르게 확인합니다.



터미널 동등 명령(`Module_8/`에서):



```bash

python ollama_model_runner.py --host http://localhost:11434 \\

  --models llama3.2:3b --prompt "Reply with exactly: Ollama OK" --max-tokens 32

```



실패하면 Step 4 **전에** Ollama를 수정하세요 — 16회 이상의 LLM 호출(8개 질문 × 2개 파이프라인)이 같은 방식으로 실패합니다.
""",
    30: """**예상 출력(Ollama):** `Ollama OK`(또는 유사)가 포함된 줄과 지연 시간, `eval_count`.



응답이 예상과 다르면 `ollama list`에 모델이 있는지, `OLLAMA_HOST`가 `ollama serve`가 수신 대기하는 주소와 일치하는지 확인하세요.
""",
    31: """---



# Step 1 — 랩 그래프 확인 및 벡터 인덱스 재연결



이 평가는 **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`**에서 이미 `LangChainLab` 서브그래프를 시드하고 벡터 인덱스를 구축했다고 가정합니다.



### 동반 노트북에서 구축한 내용



```text

(Port)-[:LOCATED_IN]->(Country)

(Organization)-[:OPERATES_IN]->(Port)

(Organization)-[:USES_ROUTE]->(Canal)

(Chunk)-[:MENTIONS]->(Entity)

```



각 `Chunk` 노드에는 **`text`** 속성(임베딩됨)과 **`embedding`** 속성(`Neo4jVector.from_documents`로 저장됨)이 있습니다.



### Step 1에서 하는 일



| 하위 단계 | 목적 |

|----------|---------|

| 1a | Cypher 쿼리용 `Neo4jGraph` 연결 |

| 1b | 랩 노드 개수 확인 — 그래프가 비어 있으면 즉시 실패 |

| 1c | 기존 벡터 인덱스 재연결(재임베딩 없음) |

| 1d | 알려진 질문으로 검색 정상 동작 확인 |
""",
    32: """### Step 1a — `Neo4jGraph` 연결



`Neo4jGraph`는 Module 8 전반에서 사용하는 LangChain 래퍼입니다. 다음을 제공합니다:



- **`query(cypher, params)`** — Cypher 실행 및 Python dict 행 반환

- **`schema`** — text-to-Cypher용 텍스트 요약(이 평가 노트북에서는 불필요)



Step 0에서 `.env`로 로드한 동일한 연결 설정을 재사용합니다.
""",
    34: """### Step 1b — `LangChainLab` 데이터 존재 확인



레이블별로 노드를 개수합니다. 정상적인 랩 그래프에는 최소한 다음이 포함되어야 합니다:



| 레이블 | 일반적인 개수 | 역할 |

|-------|---------------|------|

| `Chunk` | 4+ | 벡터 검색용 텍스트 구절 |

| `Port` | 2 | Rotterdam, Singapore |

| `Organization` | 1 | Maersk |

| `Canal` | 1 | Panama Canal |

| `Country` | 2+ | Netherlands, Singapore |



**`Chunk` 개수가 0**이면 여기서 중단하고 동반 노트북 섹션 **3.1.3** 및 **3.2.1**을 실행하세요.



**Neo4j Browser에서 확인:**



```cypher

MATCH (o:Organization:LangChainLab)-[r]->(x)

RETURN o.id, type(r), x.id;

```
""",
    36: """### Step 1c — `Neo4jVector` 인덱스 재연결



LangChain 랩에서는 `Neo4jVector.from_documents`로 인덱스를 **생성**했습니다. 여기서는 `from_existing_index`로 **재연결**하여:



- 모든 청크를 **재임베딩하지 않음**(더 빠르고 멱등적)

- 랩과 동일한 인덱스 이름 및 노드 속성 사용



| 매개변수 | 이 랩의 값 |

|-----------|-------------------|

| `index_name` | `langchain_lab_chunk_index` |

| `node_label` | `Chunk` |

| `text_node_property` | `text` |

| `embedding_node_property` | `embedding` |



**실패 시:** 벡터 인덱스가 아직 없을 수 있음 — 먼저 동반 노트북 섹션 **3.2.1c**를 실행하세요.



두 파이프라인이 동일한 수의 청크를 검색하도록 **`as_retriever(search_kwargs={'k': RETRIEVAL_K})`**로 store를 래핑합니다.
""",
    38: """### Step 1d — 빠른 검색 정상 동작 확인



**`chunk_rotterdam`**에 답이 분명히 있는 질문을 합니다: *"Which port is the largest in Europe?"*



**확인할 사항:**



- 상위 결과에 **Rotterdam**과 **Europe**이 언급되어야 합니다.

- 메타데이터에 `chunk_id`가 포함되어야 합니다(Step 2의 GraphRAG 확장에 필요).



관련 없는 청크가 반환되면 동반 노트북에서 벡터 인덱스 생성을 다시 실행하거나 청크 `text` 속성이 채워져 있는지 확인하세요.
""",
    40: """**체크포인트:** 검색이 동작하고 메타데이터에 `chunk_id`가 나타납니다. Step 2에서 평가 파이프라인을 구축할 준비가 되었습니다.
""",
    41: """---



# Step 2 — vector RAG 및 GraphRAG 답변 함수 구축



평가에는 배치 실행 및 RAGAS 입력이 가능하도록 **동일한 딕셔너리 형태**를 반환하는 **두 개의 비교 가능한 파이프라인**이 필요합니다.



### 출력 딕셔너리(두 파이프라인 공통)



| 필드 | 목적 |

|-------|---------|

| `answer` | 모델 응답 텍스트 |

| `contexts` | 문자열 목록 — RAGAS **faithfulness**가 주장을 이에 대해 검증 |

| `retrieval_sec` | 벡터 검색(+ GraphRAG의 경우 그래프 Cypher) 시간 |

| `generation_sec` | LLM 답변 생성 시간 |

| `total_sec` | 합계 — Step 6 지연 시간 비교에 사용 |

| `eval_count` | Ollama 출력 토큰 — **비용 proxy** |



### 두 파이프라인을 비교하는 이유



```text

Vector RAG:   question → embed → top-k chunks → LLM → answer

GraphRAG:     question → embed → top-k chunks → Cypher expansion → LLM → answer

                                              ↑

                                    MENTIONS, USES_ROUTE, ...

```



- **Vector RAG**는 baseline — 청크 텍스트만으로 답변합니다.

- **GraphRAG**는 청크에 문자 그대로 나타나지 않을 수 있는 명시적 관계 사실을 추가합니다(예: `Maersk -[:USES_ROUTE]-> Panama_Canal`).



GraphRAG는 추가 Cypher 지연과 더 긴 프롬프트(더 많은 토큰) 비용으로 **관계 중심** 질문을 개선할 수 있습니다.
""",
    42: """### Step 2a — 공유 프롬프트 템플릿



컨텍스트가 부족할 때 모델이 *"I do not have enough information"*이라고 말하도록 **엄격한 grounding 프롬프트**를 사용합니다 — **faithfulness** 점수 해석이 쉬워집니다.



| 템플릿 | 사용처 | 컨텍스트 블록 |

|----------|---------|----------------|

| `RAG_PROMPT_TEMPLATE` | Vector RAG | 결합된 청크 텍스트 |

| `GRAPHRAG_PROMPT_TEMPLATE` | GraphRAG | 청크 텍스트 **및** 그래프 사실 줄 |



`format_docs()`는 LangChain `Document` 객체 목록을 프롬프트용 불릿 포인트 텍스트로 변환합니다.
""",
    44: """### Step 2b — 그래프 확장 헬퍼



이 함수들은 LangChain 랩 노트북 **섹션 3.2.3**을 반영합니다.



**`graph_context_for_chunks(chunk_ids)`**는 Cypher를 실행합니다:



1. 검색된 청크 ID에서 시작.

2. `(Chunk)-[:MENTIONS]->(Entity)`를 따라감.

3. 선택적으로 `LOCATED_IN`, `OPERATES_IN`, `USES_ROUTE`에서 1-hop 확장.

4. 각 행을 LLM용 읽기 쉬운 줄로 포맷.



**`graphrag_retrieve(question)`**는 다음을 조율합니다:



1. 벡터 검색(vector RAG와 동일한 retriever).

2. 각 문서 메타데이터에서 `chunk_id` 추출.

3. 그래프 확장을 호출하고 `{chunks, graph_context}` 반환.



**프로덕션 참고:** 교육용 헬퍼입니다. 프로덕션 GraphRAG는 랭킹, 제한, 보안 필터가 있는 패키지 retriever(예: `neo4j-graphrag`)를 사용할 수 있습니다.
""",
    46: """### Step 2c — 벡터 전용 RAG 답변 함수



**질문당 흐름:**



1. **검색** — `vector_retriever.invoke(question)` → `Document` 목록

2. **컨텍스트 구축** — `page_content` 문자열을 `---` 구분자로 결합

3. **생성** — 프롬프트 포맷, Ollama runner(또는 OpenAI) 호출

4. **반환** — 답변, contexts, 시간, 토큰 수



**검색**과 **생성**을 별도로 측정하여 Step 6에서 GraphRAG의 추가 Cypher가 검색 오버헤드를 늘리는지, 더 큰 프롬프트로 생성이 길어지는지 보여줍니다.
""",
    48: """### Step 2d — GraphRAG 답변 함수



vector RAG와 동일한 구조이며 두 가지 차이가 있습니다:



1. **검색**이 `graphrag_retrieve()`(벡터 + Cypher)를 호출합니다.

2. **RAGAS용 contexts**에 청크 텍스트 **및** `[Graph facts]` 블록을 포함하여 faithfulness가 검색된 증거에 대해 관계 주장을 검증할 수 있게 합니다.



LLM 프롬프트에는 별도의 **`chunks`** 및 **`graph`** 섹션이 있습니다 — 사람이 비구조화 텍스트와 구조화 사실을 나란히 읽는 방식을 반영합니다.



**RAGAS 참고:** 그래프 사실이 `contexts`에서 누락되면 그래프 블록에만 나타나는 올바른 관계 답변에 faithfulness가 불이익을 줄 수 있습니다.
""",
    50: """### Step 2e — 두 파이프라인 스모크 테스트



**관계 중심** 질문을 사용합니다: *"How is Maersk connected to the Panama Canal?"*



빠른 A/B 확인에 이상적인 질문입니다:



| 파이프라인 | 예상되는 내용 |

|----------|-------------------|

| Vector RAG | Maersk 또는 Panama 청크 텍스트만으로 답할 수 있음 |

| GraphRAG | `USES_ROUTE` 또는 동등한 그래프 사실을 인용해야 함 |



전체 8개 질문 배치를 실행하기 전에 **답변 품질**, **total_sec**, **eval_count**를 비교하세요.
""",
    52: """**스모크 테스트 읽는 법:**



- GraphRAG가 **더 느리지만** 이 질문에서 **더 정확**하면 그래프 보강 트레이드오프를 뒷받침합니다.

- 두 답변이 비슷하고 GraphRAG가 더 느리면 질문 세트에 그래프 확장이 도움이 안 될 수 있음 — Step 6이 모든 행에서 이를 정량화합니다.

- 어느 파이프라인이든 오류가 나면 Step 4 전에 수정하세요(배치 실행은 기본적으로 첫 실패에서 멈추지 않음).
""",
    53: """---



# Step 3 — Ground-truth 데이터셋



**Ground truth** 행은 **`question`**과 **`ground_truth`** 참조 답변을 짝짓습니다. RAGAS는 모델의 **`answer`**를 **`ground_truth`**(answer relevancy) 및 **`contexts`**(faithfulness)와 비교합니다.



### 이 랩에서 수동 라벨을 쓰는 이유



해운 랩 그래프는 **작고 감사 가능**합니다 — Neo4j Browser나 동반 노트북 시드 셀에서 모든 참조 답변을 확인할 수 있습니다. 수동 라벨은 **순환 편향**(동일 모델이 자신을 채점)을 피합니다.



더 큰 코퍼스의 경우 LLM 합성 ground-truth 워크플로는 **`Module_5_Building_an_End-to-End_RAG_Evaluation.ipynb`**(Module 4)를 참고하세요.



### 열 참조



| 열 | 의미 |

|--------|---------|

| `question` | 두 파이프라인에 묻는 내용 |

| `ground_truth` | 짧은 사실 참조 답변 |

| `needs_graph` | 올바른 답에 관계 탐색이 필요할 가능성이 높으면 `True` |



**`needs_graph=True`** 질문이 GraphRAG가 추가 지연 시간을 정당화하는지 판단하는 최선의 신호입니다.
""",
    54: """### Step 3a — 수동 ground-truth 행



아래 8개 질문은 다음을 다룹니다:



- **청크 전용 사실** — 벡터 검색만으로 답 가능(`needs_graph=False`)

- **그래프 사실** — 국가의 항구, Maersk 운영, 운하 경로(`needs_graph=True`)



랩을 확장할 때(예: 섹션 3.2.4 코퍼스 import 후) **새** 청크와 엔티티를 반영하는 행을 추가하세요 — `ground_truth` 문자열은 짧고 검증 가능하게 유지하세요.
""",
    56: """### Step 3b — ground truth를 CSV로 저장



라벨을 CSV로 저장하면:



- Python 목록을 다시 편집하지 않고 Step 4–6을 재실행할 수 있습니다.

- 팀원과 평가 세트를 공유할 수 있습니다.

- 질문 세트를 버전 관리할 수 있습니다(선호 시 답변 없이).



파일은 **`outputs/eval_graphrag/ground_truth_graphrag_lab.csv`**에 기록됩니다.
""",
    58: """---



# Step 4 — 두 파이프라인 평가 실행



이제 **모든 ground-truth 질문**을 두 파이프라인으로 실행하고 RAGAS용 원시 출력을 수집합니다.



### 배치 설계



| Step | 파이프라인 | 행 |

|------|----------|------|

| 4b | Vector RAG | 질문당 한 행 |

| 4c | GraphRAG | 질문당 한 행 |



각 행은 **answer**, **contexts**, **시간**, **eval_count**를 저장하므로 Step 5–6에서 동일 질문에 대해 LLM을 다시 호출하지 않습니다(이 단계를 재실행하지 않는 한).



### 시간 예산



8개 질문 × 2개 파이프라인 = **16회 답변 생성**, Step 5의 RAGAS LLM 호출 추가:



- 로컬 Ollama(`llama3.2:3b`): 하드웨어에 따라 대략 **5–15분** 총 소요

- 디버깅 중에는 ground-truth 목록을 줄이세요



> **팁:** Step 4b만 먼저 실행하세요. vector RAG가 동작하면 4c로 진행하세요.
""",
    59: """### Step 4a — 배치 실행 헬퍼



`run_pipeline_eval()`은 **`tqdm`** 진행 표시줄과 함께 ground-truth 행을 반복합니다.



`answer_with_vector_rag` / `answer_with_graphrag`와 동일한 시그니처의 **`answer_fn`**을 받아 배치 로직을 **파이프라인에 독립적**으로 유지합니다.



출력 DataFrame은 열 선택 후 RAGAS(Step 5)에 바로 사용할 수 있습니다.
""",
    61: """### Step 4b — vector RAG 평가 실행



**Baseline** 실행입니다. 미리보기 테이블을 검토하세요:



- **`answer`** — `ground_truth`와 대략 일치하는가?

- **`total_sec`** — 내 머신에서 질문당 일반적인 지연 시간

- **`eval_count`** — 출력 토큰(baseline 비용 proxy)



비정상적으로 느린 행은 긴 검색 컨텍스트나 첫 호출 시 모델 cold-start를 나타낼 수 있습니다.
""",
    63: """### Step 4c — GraphRAG 평가 실행



동일한 질문, 동일한 `RETRIEVAL_K`, 그래프 확장 포함.



Step 4b와 미리보기 열을 비교하세요:



- **`total_sec`**가 일관되게 더 높은가?(예상 — 추가 Cypher + 더 긴 프롬프트)

- **`eval_count`**가 더 높은가?(더 긴 그래프 컨텍스트 → 간접적으로 더 많은 입력 토큰; 출력도 늘 수 있음)



정확도는 아직 해석하지 마세요 — RAGAS가 Step 5에서 채점합니다.
""",
    65: """### Step 4d — 원시 출력 결합 및 저장



두 파이프라인을 하나의 CSV로 병합하여 감사 추적을 남깁니다. 컨텍스트 목록은 스프레드시트 가독성을 위해 `---` 구분자로 평탄화됩니다.



**파일:** `outputs/eval_graphrag/graphrag_eval_raw_outputs.csv`



`EVAL_RETRIEVAL_K` 증가 등 파이프라인 버전을 시간에 따라 비교할 때 이 파일을 보관하세요.
""",
    67: """---



# Step 5 — RAGAS로 채점



[RAGAS](https://docs.ragas.io/)(Retrieval Augmented Generation Assessment)는 RAG 시스템용 참조 없는 및 참조 기반 지표를 제공합니다.



### 이 랩에서 사용하는 지표



| 지표 | 범위 | 답하는 질문 |

|--------|-------|---------------------|

| **Faithfulness** | 0–1 | 답변이 **검색된 컨텍스트로 뒷받침**되는가? |

| **Answer relevancy** | 0–1 | 답변이 **질문에 부합**하는가(ground truth 의도 대비)? |



### 점수 조합 해석 방법



| Faithfulness | Relevancy | 일반적인 의미 |

|--------------|-----------|-----------------|

| 높음 | 높음 | 건강함 — grounded이고 주제에 맞음 |

| 높음 | 낮음 | grounded이지만 질문 의도를 놓침 |

| 낮음 | 높음 | 맞는 것 같지만 컨텍스트로 **뒷받침되지 않음**(환각 위험) |

| 낮음 | 낮음 | 광범위한 파이프라인 문제(검색, 프롬프트 또는 모델) |



### RAGAS 입력 스키마



필수 열: `question`, `answer`, `contexts`(문자열 목록), `ground_truth`.



> **참고:** RAGAS는 행마다 **추가 LLM 호출**을 하고(answer relevancy에 임베딩 사용). Step 4 이후 **추가 시간**을 예산에 포함하세요.
""",
    68: """### Step 5a.0 — RAGAS 호환 shim(RAGAS import 전 실행)



**알려진 문제:** `ragas` 0.4.x가 최신 `langchain-community`에서 **제거된** 경로에서 `ChatVertexAI`를 import합니다:



```text

langchain_community.chat_models.vertexai  # langchain-community 0.4+에서 제거됨

```



이 랩은 **Ollama만** 사용합니다 — Google Vertex AI가 필요 없습니다. 다음 셀은 `import ragas`가 성공하도록 작은 **stub 모듈**을 등록합니다.



| 증상 | 해결 |

|---------|-----|

| `No module named 'langchain_community.chat_models.vertexai'` | 아래 shim 셀 실행 후 Step 5a |

| 이 커널에서 shim 셀을 이미 실행함 | 재실행해도 안전 |



업스트림 참조: [ragas issue #2745](https://github.com/vibrantlabsai/ragas/issues/2745).
""",
    70: """### Step 5a — RAGAS import



이 커널 세션에서 호환 shim을 아직 적용하지 않았다면 먼저 **Step 5a.0**을 실행하세요.



다음을 import합니다:



- **`evaluate`** — 주요 RAGAS 채점 함수

- **`faithfulness`** 및 **`answer_relevancy`** — 이 랩에서 사용하는 지표



ragas 0.4.x에서 `ragas.metrics.collections` 관련 deprecation 경고는 예상되며 이 코스에서는 무시해도 됩니다.
""",
    72: """### Step 5b — RAGAS 헬퍼 함수



`run_ragas_scores()`:



1. RAGAS가 기대하는 네 열을 선택합니다.

2. Hugging Face **`Dataset`**으로 변환합니다.

3. `faithfulness`와 `answer_relevancy`로 **`evaluate()`**를 호출합니다.

4. 점수를 원본 평가 DataFrame에 다시 조인합니다.



Step 0에서 구성한 동일한 **`ragas_llm`**과 **`embeddings`**를 전달하여 채점을 재현 가능하게 합니다.
""",
    74: """### Step 5c — vector RAG 채점



**Baseline** 정확도 수치를 확립합니다.



다음에 집중하세요:



- **평균 faithfulness** — vector RAG가 검색된 청크 내에 머무는 빈도

- **평균 answer relevancy** — 답변이 `ground_truth` 의도와 얼마나 잘 맞는지

- **`needs_graph=True`**인데 점수가 낮은 행 — Step 5d에서 GraphRAG 개선 후보
""",
    76: """### Step 5d — GraphRAG 채점



Step 5c의 평균과 비교하세요:



- **`needs_graph=True` 행에서 faithfulness 상승** → 그래프 사실이 grounding에 도움

- **관계 질문에서 answer relevancy 상승** → 그래프 컨텍스트가 사실적 완전성 개선

- **전체 faithfulness 하락** → 모델이 `contexts`에 없는 그래프 줄에서 주장을 지어낼 수 있음(Step 2d 컨텍스트 조립 확인)



Step 6 집계를 읽기 전에 **`needs_graph`**로 미리보기를 머릿속으로 나눠 보세요.
""",
    78: """### Step 5e — 채점된 테이블 저장



| 파일 | 내용 |

|------|----------|

| `scored_vector_rag.csv` | Vector RAG 답변 + RAGAS 점수 |

| `scored_graphrag.csv` | GraphRAG 답변 + RAGAS 점수 |



이들은 Step 6 비교 및 Step 7 실패 분석의 주요 입력입니다.
""",
    80: """---



# Step 6 — 시간, 비용, 정확도 비교



프로덕션 팀은 **정확도만** 최적화하는 경우가 드뭅니다. 이 단계는 세 가지 차원을 결합합니다:



### 비교 차원



| 차원 | Vector RAG | GraphRAG | 중요한 이유 |

|-----------|------------|----------|----------------|

| **정확도** | 평균 faithfulness 및 relevancy | 동일 | 품질 |

| **지연 시간** | 평균 / p95 `total_sec` | 동일 | 사용자 경험 |

| **비용 proxy** | 평균 / 총 `eval_count` | 동일 | 용량 계획 |



**호스팅 API**의 경우 토큰 수에 제공자 가격표를 곱하세요. **로컬 Ollama**의 경우 달러 비용은 ~$0이지만 **토큰과 초**는 여전히 하드웨어 부하와 배치 작업 시간을 예측합니다.



**`needs_graph=True`** 부분집합에서도 지표를 계산합니다 — GraphRAG 승리를 기대하기 가장 공정한 곳입니다.
""",
    81: """### Step 6a — 정확도 요약



`metric_summary()`는 다음을 집계합니다:



- 전체 평균 **faithfulness** 및 **answer_relevancy**

- **`needs_graph=True`** 행으로 제한한 동일 평균



GraphRAG가 부분집합에서만 이기고 전체에서는 비기면 그래프 확장이 **관계 질문**에 특히 도움이 됩니다 — 흔한 실무 패턴입니다.
""",
    83: """### Step 6b — 지연 시간 및 비용 요약



| 지표 | 의미 |

|--------|---------|

| `mean_total_sec` | 질문당 평균 end-to-end 시간 |

| `p95_total_sec` | 95 백분위수 — 느린 이상치 포착 |

| `mean_retrieval_sec` | 벡터(+ 그래프) 검색만 |

| `mean_generation_sec` | LLM 호출만 |

| `mean_eval_count` | 답변당 평균 출력 토큰 |

| `total_eval_count` | 모든 질문 합계 — 배치 비용 proxy |



GraphRAG는 종종 **더 높은 `mean_retrieval_sec`**(Cypher)와 **더 높은 `mean_eval_count`**(더 긴 프롬프트)를 보입니다.
""",
    85: """### Step 6c — 결합 비교 테이블



파생 열:



| 열 | 의미 |

|--------|---------|

| `faithfulness_delta_vs_vector` | GraphRAG 평균 faithfulness minus vector RAG(양수 = 그래프 승) |

| `latency_ratio_vs_vector` | GraphRAG 평균 지연 시간 / vector RAG(>1 = 그래프가 더 느림) |



**결정 프레이밍:** 중요한 질문 유형에서 정확도 향상이 지연/비용 예산을 초과하면 GraphRAG를 수용하세요(예: +0.1 faithfulness가 1.3× 지연 시간 가치가 있음).
""",
    87: """### Step 6d — 질문별 나란히 비교



학습자에게 가장 실행 가능한 뷰입니다:



- **`faithfulness_gain`** — 질문당 GraphRAG minus vector RAG

- **`latency_delta_sec`** — 해당 질문에서 GraphRAG가 추가로 소요한 초



**`faithfulness_gain`** 내림차순 정렬로 그래프 보강이 가장 도움이 된 곳을 확인하세요. **`needs_graph`**와 교차 확인 — `True` 행의 이득이 GraphRAG 설계를 검증합니다.
""",
    89: """### Step 6e — 비교 아티팩트 저장



| 파일 | 대상 |

|------|----------|

| `comparison_summary.csv` | 이해관계자 — 파이프라인당 한 행 |

| `comparison_per_question.csv` | 엔지니어 — 질문별 drill-down |



`EVAL_RETRIEVAL_K`, 프롬프트 또는 모델을 변경할 때 이 파일들을 보관하여 회귀를 추적하세요.
""",
    91: """---



# Step 7 — 낮은 점수 샘플 검토



집계 지표는 **실패 모드**를 숨깁니다. `k`나 프롬프트를 변경하기 전에 개별 행을 검토하세요.



### 디버깅 워크플로



1. **낮은 faithfulness로 정렬** — 뒷받침되지 않는 주장(환각) 찾기.

2. **검색된 `contexts` 읽기** — 증거가 누락되었거나 무시되었는가?

3. **GraphRAG의 경우** — `[Graph facts]`가 비어 있는가? Neo4j Browser에서 `MENTIONS` 엣지 확인.

4. `comparison_per_question.csv`에서 동일 질문에 대해 **vector vs graph** 비교.



### 흔한 실패 패턴



| 패턴 | 가능한 원인 |

|---------|--------------|

| faithfulness 낮음, 검색 양호 | 모델이 컨텍스트 무시 — 프롬프트 강화 또는 더 큰 모델 |

| faithfulness 낮음, 검색 불량 | 잘못된 청크 — `k` 또는 임베딩 조정 |

| 그래프 컨텍스트 비어 있음 | `(Chunk)-[:MENTIONS]->(Entity)` 링크 누락 |

| relevancy 낮음, faithfulness 높음 | 답변이 너무 좁거나 질문에서 벗어남 — 프롬프트 또는 ground-truth 문구 |
""",
    92: """### Step 7a — faithfulness 최하위 행(GraphRAG)



GraphRAG 결과를 **faithfulness 오름차순**, 그다음 **answer relevancy 오름차순**으로 정렬합니다.



이 행들이 **우선 수정 목록**입니다 — faithfulness가 0에 가까울 때 환각 위험이 가장 높습니다.
""",
    94: """### Step 7b — 한 행 상세 검토



다른 실패를 검토하려면 **`row_idx`**를 변경하세요.



각 행에 대해 질문하세요:



1. **`ground_truth`**가 그래프/청크에 실제로 있는 내용과 일치하는가?

2. **`answer`**가 **`contexts`**에 없는 사실을 도입하는가?

3. vector RAG가 더 높은 점수를 받았을까?(`comparison_per_question.csv` 확인)



파이프라인 변경을 승격하기 전 수동 QA용 템플릿으로 이 셀을 사용하세요.
""",
    96: """### Step 7c — 반복 개선 아이디어



| 조절 항목 | 효과 |

|------|--------|

| `EVAL_RETRIEVAL_K` 증가 | 더 많은 청크 컨텍스트; 더 느린 프롬프트 |

| 코퍼스 청크 추가(LangChain 노트북 3.2.4) | 더 넓은 커버리지 |

| 누락된 `MENTIONS` 엣지 수정 | GraphRAG 확장이 비어 있음 반환 |

| 더 큰 Ollama 모델 사용(`llama3.1:8b`) | 더 나은 grounding 및 relevancy |

| 프롬프트 강화 | 뒷받침되지 않는 주장 감소 |

| 새 ground truth용 별도 라벨러 모델 | 순환 편향 방지(Module 4 랩 참고) |



**워크플로:** 한 가지 조절 → Step 4–6 재실행 → 새 `comparison_summary.csv`를 이전 실행과 비교.



**그래프 문제용 Neo4j Browser 확인:**



```cypher

MATCH (c:Chunk:LangChainLab)-[:MENTIONS]->(e)

RETURN c.id, e.id LIMIT 20;

```
""",
    97: """---



# Step 8 — 아티팩트 저장 및 체크리스트



### `outputs/eval_graphrag/`에 기록되는 파일



| 파일 | 내용 |

|------|----------|

| `ground_truth_graphrag_lab.csv` | 평가 질문 및 참조 답변 |

| `graphrag_eval_raw_outputs.csv` | 답변, contexts, 지연 시간, 토큰(두 파이프라인) |

| `scored_vector_rag.csv` | Vector RAG + RAGAS 점수 |

| `scored_graphrag.csv` | GraphRAG + RAGAS 점수 |

| `comparison_summary.csv` | 집계된 정확도 / 지연 / 토큰 |

| `comparison_per_question.csv` | 질문별 나란히 비교 |



### 학습자용 실용 체크리스트



1. 평가 **전에** Neo4j 랩 그래프와 벡터 인덱스 확인(Step 1).

2. **작고** 고품질 ground-truth 세트(8–15행)로 시작.

3. **`needs_graph=True`** 질문에서 **vector RAG vs GraphRAG**를 먼저 비교.

4. RAGAS 점수뿐 아니라 **지연 시간과 토큰**도 추적.

5. 생성 튜닝 전 **낮은 faithfulness** 행 검토(Step 7).

6. 파이프라인 변경마다 평가를 재실행하고 감사용 **CSV 아티팩트 보관**.



### 구축한 내용



**RAGAS**로 **Neo4j GraphRAG** 애플리케이션을 평가하고 **벡터 전용 RAG**와 비교했으며 **시간 / 비용 / 정확도** 트레이드오프를 측정했습니다 — 팀이 그래프 보강 검색을 프로덕션에 배포하기 전에 사용하는 동일한 워크플로입니다.
""",
    98: """### Step 8 — 최종 요약



다음 셀은 **`comparison`** 테이블을 출력합니다 — 한 페이지 요약 보고서입니다.



다음을 확인하세요:



- 어느 파이프라인의 **faithfulness_mean** 및 **answer_relevancy_mean**이 더 높은지

- GraphRAG의 **latency_ratio_vs_vector**가 사용 사례에 허용 가능한지

- **faithfulness_mean_needs_graph** — 그래프 탐색이 가치 제안이라면 핵심 지표
""",
}

PRINT_REPLACEMENTS: dict[int, list[tuple[str, str]]] = {
    8: [
        ("print('Module directory:', MODULE_DIR)", "print('모듈 디렉터리:', MODULE_DIR)"),
        ("print('Evaluation outputs:', OUTPUT_DIR)", "print('평가 출력:', OUTPUT_DIR)"),
    ],
    11: [
        ("print('Neo4j URI:', NEO4J_URI)", "print('Neo4j URI:', NEO4J_URI)"),
        ("print('Neo4j database:', NEO4J_DATABASE)", "print('Neo4j 데이터베이스:', NEO4J_DATABASE)"),
    ],
    13: [
        ("print('LLM backend:', LLM_BACKEND)", "print('LLM 백엔드:', LLM_BACKEND)"),
        ("print('Retrieval k:', RETRIEVAL_K)", "print('검색 k:', RETRIEVAL_K)"),
        ("print('Ollama model:', OLLAMA_MODEL, '@', OLLAMA_HOST)", "print('Ollama 모델:', OLLAMA_MODEL, '@', OLLAMA_HOST)"),
    ],
    15: [
        ("print('Connectivity check passed.')", "print('연결 확인 완료.')"),
    ],
    19: [
        ("print('OLLAMA_RUNNER:', OLLAMA_RUNNER)", "print('OLLAMA_RUNNER:', OLLAMA_RUNNER)"),
    ],
    25: [
        ("print(f'Using OpenAI: {OPENAI_MODEL}')", "print(f'OpenAI 사용: {OPENAI_MODEL}')"),
        (
            "print(f'Using Ollama runner: {OLLAMA_MODEL} @ {OLLAMA_HOST}')",
            "print(f'Ollama runner 사용: {OLLAMA_MODEL} @ {OLLAMA_HOST}')",
        ),
    ],
    27: [
        ("print('Embedding model:', EMBED_MODEL_NAME)", "print('임베딩 모델:', EMBED_MODEL_NAME)"),
    ],
    29: [
        ("print('Smoke response:', smoke['response'][:120])", "print('스모크 응답:', smoke['response'][:120])"),
        ("print('Latency (sec):', round(smoke['latency_sec'], 3))", "print('지연 시간(초):', round(smoke['latency_sec'], 3))"),
        (
            "print('Output tokens (eval_count):', smoke['eval_count'])",
            "print('출력 토큰 (eval_count):', smoke['eval_count'])",
        ),
        ("print('Skipped — OpenAI backend')", "print('건너뜀 — OpenAI 백엔드')"),
    ],
    33: [
        ("print('Neo4jGraph connected.')", "print('Neo4jGraph 연결 완료.')"),
    ],
    35: [
        ("print('LangChainLab node counts:')", "print('LangChainLab 노드 개수:')"),
        ("print('Chunk nodes ready:', chunk_count)", "print('청크 노드 준비 완료:', chunk_count)"),
    ],
    37: [
        (
            "print('Vector index connected:', VECTOR_INDEX_NAME, '| k =', RETRIEVAL_K)",
            "print('벡터 인덱스 연결됨:', VECTOR_INDEX_NAME, '| k =', RETRIEVAL_K)",
        ),
    ],
    39: [
        ("print('Query:', query)", "print('질의:', query)"),
    ],
    51: [
        ("print('Question:', _demo_q)", "print('질문:', _demo_q)"),
        ("print('\\n--- Vector RAG ---')", "print('\\n--- Vector RAG ---')"),
        (
            "print('Total sec:', round(_demo_vec['total_sec'], 3), '| eval_count:', _demo_vec['eval_count'])",
            "print('총 시간(초):', round(_demo_vec['total_sec'], 3), '| eval_count:', _demo_vec['eval_count'])",
        ),
        ("print('\\n--- GraphRAG ---')", "print('\\n--- GraphRAG ---')"),
        (
            "print('Total sec:', round(_demo_graph['total_sec'], 3), '| eval_count:', _demo_graph['eval_count'])",
            "print('총 시간(초):', round(_demo_graph['total_sec'], 3), '| eval_count:', _demo_graph['eval_count'])",
        ),
    ],
    55: [
        ("print('Ground-truth rows:', len(ground_truth_df))", "print('Ground-truth 행 수:', len(ground_truth_df))"),
    ],
    57: [
        ("print('Saved:', gt_path)", "print('저장됨:', gt_path)"),
    ],
    62: [
        ("print('Vector RAG rows:', len(eval_df_vector))", "print('Vector RAG 행 수:', len(eval_df_vector))"),
    ],
    64: [
        ("print('GraphRAG rows:', len(eval_df_graphrag))", "print('GraphRAG 행 수:', len(eval_df_graphrag))"),
    ],
    66: [
        ("print('Saved:', raw_path)", "print('저장됨:', raw_path)"),
    ],
    69: [
        ("print('RAGAS compatibility shim applied.')", "print('RAGAS 호환 shim 적용 완료.')"),
    ],
    71: [
        ("print('RAGAS imported successfully.')", "print('RAGAS import 성공.')"),
    ],
    73: [
        (
            "print(f'RAGAS dataset ({label}):', ragas_dataset)",
            "print(f'RAGAS 데이터셋 ({label}):', ragas_dataset)",
        ),
    ],
    75: [
        (
            "print('Vector RAG mean faithfulness:', round(scored_vector['faithfulness'].mean(), 3))",
            "print('Vector RAG 평균 faithfulness:', round(scored_vector['faithfulness'].mean(), 3))",
        ),
        (
            "print('Vector RAG mean answer_relevancy:', round(scored_vector['answer_relevancy'].mean(), 3))",
            "print('Vector RAG 평균 answer_relevancy:', round(scored_vector['answer_relevancy'].mean(), 3))",
        ),
    ],
    77: [
        (
            "print('GraphRAG mean faithfulness:', round(scored_graphrag['faithfulness'].mean(), 3))",
            "print('GraphRAG 평균 faithfulness:', round(scored_graphrag['faithfulness'].mean(), 3))",
        ),
        (
            "print('GraphRAG mean answer_relevancy:', round(scored_graphrag['answer_relevancy'].mean(), 3))",
            "print('GraphRAG 평균 answer_relevancy:', round(scored_graphrag['answer_relevancy'].mean(), 3))",
        ),
    ],
    79: [
        ("print('Saved scored CSVs under', OUTPUT_DIR)", "print('채점된 CSV 저장 위치:', OUTPUT_DIR)"),
    ],
    90: [
        ("print('Saved comparison CSVs')", "print('비교 CSV 저장 완료')"),
    ],
    93: [
        ("print('GraphRAG — lowest faithfulness:')", "print('GraphRAG — faithfulness 최하위:')"),
    ],
    95: [
        ("print('Question:', row['question'])", "print('질문:', row['question'])"),
        ("print('\\nGraphRAG answer:\\n', row['answer'])", "print('\\nGraphRAG 답변:\\n', row['answer'])"),
        ("print('\\nGround truth:\\n', row['ground_truth'])", "print('\\nGround truth:\\n', row['ground_truth'])"),
        (
            "print('\\nFaithfulness:', row['faithfulness'], '| Answer relevancy:', row['answer_relevancy'])",
            "print('\\nFaithfulness:', row['faithfulness'], '| Answer relevancy:', row['answer_relevancy'])",
        ),
        ("print('\\nRetrieved contexts:')", "print('\\n검색된 contexts:')"),
        (
            "print(f'--- context {i} ---\\n', ctx[:500])",
            "print(f'--- context {i} ---\\n', ctx[:500])",
        ),
    ],
    99: [
        ("print('=== Evaluation complete ===')", "print('=== 평가 완료 ===')"),
        ("print('\\nArtifacts directory:', OUTPUT_DIR)", "print('\\n아티팩트 디렉터리:', OUTPUT_DIR)"),
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

    md_indices = [i for i, c in enumerate(nb["cells"]) if c["cell_type"] == "markdown"]
    missing = set(md_indices) - set(MARKDOWN_KO)
    if missing:
        raise ValueError(f"Missing Korean markdown for cells: {sorted(missing)}")

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
