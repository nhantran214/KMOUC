#!/usr/bin/env python3
"""Build Korean Module_6 Practical KG Applications notebook from the English source."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Module_6_Practical_Knowledge_Graph_Applications.ipynb"
DST = ROOT / "Module_6_Practical_Knowledge_Graph_Applications_KO.ipynb"

MARKDOWN_KO: dict[int, str] = {
    0: """# 실무 지식 그래프(Knowledge Graph) 응용

**코스 모듈:** Module 8
**대상:** Neo4j, Cypher 기초 및 (선택) LLM을 이해하는 초급 학습자

## 코스 설명

지식 그래프(Knowledge Graph)는 단순한 저장 형식이 아닙니다. 관계가 의사결정을 이끄는 **실제 애플리케이션**을 구동합니다:
물류, 규정 준수(compliance), 리스크, 추천, 근거 기반 질의응답(question answering) 등입니다.

이 실습 코스에서는 다음을 수행합니다:

1. Neo4j에서 **해운/공급망(supply-chain) 지식 그래프**를 구축합니다.
2. Cypher로 **7가지 실무 문제**를 해결합니다(LLM 보조 Q&A 포함).
3. 각 연습을 업계에서 들을 수 있는 **비즈니스 질문**과 연결합니다.

> **언어:** 이 노트북의 안내 텍스트는 **한국어**입니다. 기술 용어는 필요 시 영어를 병기합니다.

> **설정(필수):** 코드 실행 전 **`NEO4J_SETUP.md`**를 완료하세요.
> LLM 섹션의 경우 **`LLM_MODEL_SETUP.md`**를 완료하고 **`ollama_model_runner.py`**를 실행하세요
> (또는 OpenAI를 구성).

### 이 노트북 사용법

1. 아래 **코드** 셀을 실행하기 전에 각 **마크다운** 셀을 읽으세요.
2. Step 0부터 **순서대로** 셀을 실행하세요.
3. 랩 데이터는 **`KGApplicationsLab`** 레이블을 사용합니다 — 안전하게 삭제 후 재시드할 수 있습니다.
4. 코드 셀은 의도적으로 **짧게** 작성되었습니다. 마크다운이 각 단계의 *이유*를 설명합니다.
""",
    1: """## 사전 요구 사항

| 기술 | 필요한 이유 |
|-------|-----------------|
| Neo4j 기초 | 노드, 관계, `MATCH`, `RETURN` |
| Python | 노트북 셀 실행 |
| (선택) LLM | Part 8 — 자연어 비즈니스 Q&A |

### 관련 Module 8 노트북

| 노트북 | 초점 |
|----------|-------|
| `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb` | LLM으로 텍스트에서 그래프 추출 |
| `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb` | LangChain RAG / GraphRAG / agent |
| `Module_8_Evaluating_GraphRAG_with_RAGAS.ipynb` | GraphRAG 품질 측정 |

**이 노트북**은 그래프가 존재한 **이후에 할 수 있는 일**에 초점을 맞춥니다 — 프레임워크 API가 아닌 **응용(application)**입니다.

## 코스 개요

| 파트 | 주제 | 실무 문제 |
|------|--------|-------------------|
| **0** | 환경 및 Neo4j 연결 | — |
| **1** | 응용 지형 | 그래프가 테이블보다 나은 경우 |
| **2** | 랩 그래프 구축 | 해운 물류 도메인 모델 |
| **3** | 네트워크 탐색 | *누가 어디서 운영하나?* |
| **4** | 경로 및 영향 분석 | *경로가 중단되면 무엇이 깨지나?* |
| **5** | 엔티티 해소(entity resolution) | *이 두 레코드가 같은 회사인가?* |
| **6** | 추천 | *어떤 항구가 유사한가?* |
| **7** | 규정 준수 매핑 | *어떤 규칙이 어떤 운송사에 적용되나?* |
| **8** | 비즈니스 Q&A (LLM + Cypher) | *일반 영어로 질문하기* |
| **9** | 그래프 분석 | *어떤 허브가 가장 중요한가?* |
| **10** | 마무리 | 연습을 자신의 도메인에 매핑 |
""",
    2: """---

# Step 0 — 환경 및 Neo4j 연결

### 코드 실행 전

1. **`NEO4J_SETUP.md`** 완료 — Aura, Desktop 또는 Docker; URI, 사용자명, 비밀번호 확인.
2. `Module_8/.env.example` → `Module_8/.env` 복사 후 Neo4j 자격 증명 입력.
3. **Part 8**(LLM Q&A)의 경우 **`LLM_MODEL_SETUP.md`**도 완료하고 `ollama serve`를 시작하세요.

### Step 0에서 하는 일

| Step | 목적 |
|------|---------|
| 0a | Python 패키지 설치 |
| 0b | 경로 및 환경 변수 로드 |
| 0c | Neo4j Bolt 연결 확인 |
| 0d | (선택) Part 8용 Ollama runner 연결 |
""",
    3: """### Step 0a — Python 패키지 설치

핵심 패키지: Neo4j driver, `python-dotenv`, Part 8에서 사용하는 LangChain 구성 요소.
가상 환경당 한 번 실행하세요.
""",
    5: """### Step 0b.1 — `Module_8` 폴더 확인

Jupyter는 저장소 루트 또는 `Module_8` 내부에서 시작할 수 있습니다. 이 셀은 `.env`와 `data/`가 있는 폴더를 찾습니다.
""",
    7: """### Step 0b.2 — Neo4j 연결 설정

값은 `Module_8/.env`에서 가져옵니다(**`NEO4J_SETUP.md`** 참고).
""",
    9: """### Step 0b.3 — LLM 설정 (Part 8 전용)

Part 1–7은 **Cypher만** 사용합니다. Part 8에서 자연어 Q&A를 추가합니다.

- **`LLM_BACKEND=ollama`** → `ollama_model_runner.py` (권장)
- **`LLM_BACKEND=openai`** → `ChatOpenAI`
""",
    11: """### Step 0c — Neo4j 연결 확인

실패하면 **`NEO4J_SETUP.md`** 문제 해결 섹션으로 돌아가세요.
""",
    13: """### Step 0d — Neo4j 헬퍼 및 (선택) Ollama runner

노트북 전체에서 사용하는 작은 `run_cypher()` 헬퍼를 정의합니다.
Ollama runner 블록은 **Part 8**에만 필요합니다 — 원하면 0d.2–0d.4는 나중에 건너뛸 수 있습니다.
""",
    18: """---

# Part 1 — 실무 지식 그래프 응용

관계형 데이터베이스는 **행과 조인**에 강합니다. 지식 그래프는 다음 경우에 강합니다:

- **연결 구조** 자체가 제품인 경우(공급망, 조직도, 사기 네트워크).
- **다중 홉(multi-hop) 추론**이 필요한 경우(*공급업체 → 공장 → 항구 → 운하*).
- 여러 팀이 **단일 연결 모델**을 공유하는 경우(운영, 규정 준수, 데이터 과학).

### 응용 지도 (이 코스)

| 산업 | 그래프 응용 | 노트북 파트 |
|----------|-------------------|---------------|
| 물류 | 경로 및 허브 분석 | 3, 4, 9 |
| 소매 | 제품 추천 | 6 |
| 금융 | 엔티티 해소, AML 경로 | 5 |
| 헬스케어 | 치료 경로 | (Part 4와 동일한 패턴) |
| 기업 | 정책 / 규정 준수 매핑 | 7 |
| GenAI | 근거 기반 비즈니스 Q&A | 8 |

### 실습 도메인: 해운 및 공급망

**항구, 운송사(carrier), 운하, 국가, 규정**을 사용합니다 — 글로벌 무역의 현실적인 단면입니다.
데이터는 Cypher(구조화)로 시드되며, 선택적으로 `data/dbpedia_maritime_corpus.txt`의 텍스트를 사용합니다(`data/DATASETS.md` 참고).
""",
    19: """---

# Part 2 — 응용 지식 그래프 구축

## 2.1 데이터 모델

```text
(Port)-[:LOCATED_IN]->(Country)
(Organization)-[:OPERATES_IN]->(Port)
(Organization)-[:USES_ROUTE]->(Waterway)
(Organization)-[:HEADQUARTERED_IN]->(Country)
(Regulation)-[:ISSUED_BY]->(Agency)
(Organization)-[:SUBJECT_TO]->(Regulation)
(Port)-[:CONNECTED_TO]->(Port)   // trade lanes
```

모든 랩 노드에는 **`KGApplicationsLab`** 레이블도 있어 안전하게 삭제하고 재구축할 수 있습니다.
""",
    20: """### Step 2.1a — 이전 랩 데이터 삭제

노트북을 다시 실행해도 노드가 중복되지 않아야 합니다.
""",
    22: """### Step 2.1b — 국가 및 수로(waterway) 생성

다른 노드가 연결할 **참조 엔티티**부터 시작합니다.
""",
    24: """### Step 2.1c — 항구 생성

항구는 네트워크의 **허브**입니다. Part 9 분석을 위해 처리량(throughput) 순위를 저장합니다.
""",
    26: """### Step 2.1d — 해운 조직 생성

운송사는 항구에서 **운영**하고 전략적 수로를 **사용**합니다.
""",
    28: """### Step 2.1e — 항구 간 무역 경로(trade lane)

`CONNECTED_TO` 엣지는 **빈번한 무역 경로**를 나타냅니다(단순화를 위해 무방향).
""",
    30: """### Step 2.1f — 규정 및 규정 준수 엣지

규제 지식은 전형적인 KG 사용 사례입니다: **어떤 규칙이 누구에게 적용되나?**
""",
    32: """### Step 2.1g — 그래프 확인

시드 후 실행하세요. Neo4j Browser를 열고 `KGApplicationsLab` 노드를 시각화하세요.
""",
    34: """---

# Part 3 — 응용: 네트워크 탐색 및 검색

**비즈니스 질문:** *유럽 항구에서 운영하는 해운 회사는 어디인가?*

SQL은 종종 많은 조인이 필요합니다. 그래프에서는 `Organization`에서 `Port`, `Country`로 **엣지를 따라갑니다**.
""",
    35: """### Step 3.1 — 네덜란드에서 운영하는 운송사
""",
    37: """### Step 3.2 — 특정 운송사가 서비스하는 모든 항구

**비즈니스 질문:** *Maersk는 어디서 운영하나?*
""",
    39: """### Step 3.3 — 매개변수화된 검색 함수

Cypher를 Python으로 감싸 제품 팀이 API에서 하나의 함수를 호출할 수 있게 합니다.
""",
    41: """---

# Part 4 — 응용: 경로 및 영향 분석

**비즈니스 질문:** *수에즈 운하(Suez Canal)가 중단되면 어떤 운송사와 항구가 영향을 받나?*

그래프는 **의존성 탐색**을 명시적으로 만듭니다: 운송사 → `USES_ROUTE` → 수로.
""",
    42: """### Step 4.1 — 수에즈 운하를 사용하는 운송사
""",
    44: """### Step 4.2 — 영향받는 운송사의 하류 항구

2홉 패턴: **수로 → 운송사 → 항구**.
""",
    46: """### Step 4.3 — 두 항구 간 최단 무역 경로

**비즈니스 질문:** *우리 경로 모델에서 로테르담과 로스앤젤레스는 어떻게 연결되나?*
""",
    48: """### Step 4.4 — 영향 보고서 헬퍼

운영 대시보드를 위한 그래프 결과를 패키징합니다.
""",
    50: """---

# Part 5 — 응용: 엔티티 해소(Entity Resolution)

**비즈니스 질문:** *"MSC"와 "Mediterranean Shipping Company"는 같은 조직인가?*

실제 데이터는 **여러 소스**에서 서로 다른 이름으로 도착합니다. 그래프는 다음을 지원합니다:

1. **후보 생성** — 유사한 이름 찾기
2. **병합** — 하나의 정규(canonical) 노드로 통합
3. **출처 추적(provenance)** — 감사를 위해 `alt_names` 유지
""",
    51: """### Step 5.1 — 중복 레코드 시드 (두 번째 데이터 피드 시뮬레이션)
""",
    53: """### Step 5.2 — 해소 후보 찾기

간단한 규칙: 동일한 **정규화된 이름** 또는 겹치는 **항구 운영**.
""",
    55: """### Step 5.3 — 중복을 정규 노드에 병합

교육 명확성을 위해 `MERGE` + `apoc.refactor.mergeNodes` 패턴을 `MATCH`로 수동 구현합니다.
""",
    58: """---

# Part 6 — 응용: 추천 및 유사도

**비즈니스 질문:** *확장 계획을 위해 싱가포르와 유사한 항구는 어디인가?*

**협업 필터링 패턴:** **같은 운송사**에 연결된 항구는 유사합니다.
이는 *X를 산 사용자가 Y도 구매*와 같은 아이디어이지만 그래프 위에서입니다.
""",
    59: """### Step 6.1 — 싱가포르와 운송사를 공유하는 항구
""",
    61: """### Step 6.2 — 신규 항구에 운송사 추천 (공동 위치 패턴)

신규 항구가 **유럽**에 있다면, 이미 유럽 항구에서 운영 중인 운송사를 추천합니다.
""",
    63: """---

# Part 7 — 응용: 규정 준수 및 규제 매핑

**비즈니스 질문:** *Maersk에 적용되는 IMO 규정은 무엇인가? 누가 발행했나?*

규정 준수 그래프는 **정책 → 당국 → 엔티티**를 연결합니다. 감사인은 PDF를 개별적으로 읽는 대신 엣지를 탐색합니다.
""",
    64: """### Step 7.1 — 운송사에 적용되는 규정
""",
    66: """### Step 7.2 — 특정 규정 하의 모든 운송사
""",
    68: """### Step 7.3 — 규정 준수 체크리스트보내기
""",
    70: """---

# Part 8 — 응용: LLM + Cypher 비즈니스 Q&A

**비즈니스 질문:** *이해관계자는 일반 영어로 질문하고, 분석가는 모든 질문에 Cypher를 작성하지 않아야 한다.*

LangChain의 **`GraphCypherQAChain`**과 스키마 인트로스펙션을 사용합니다 — `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`와 동일한 패턴이며 랩 그래프에 범위를 한정합니다.

> **필요:** `LLM_MODEL_SETUP.md` 및 Step 0d의 동작하는 `llm`.
""",
    71: """### Step 8.1 — LangChain Neo4jGraph 연결
""",
    73: """### Step 8.2 — GraphCypherQAChain

체인: 질문 → LLM이 Cypher 작성 → 실행 → LLM이 답변 요약.
""",
    75: """### Step 8.3 — 직접 비즈니스 질문 시도

이 랩 그래프에서 잘 동작하는 예시:

- *Which ports are in the Netherlands?*
- *What regulations apply to COSCO?*
- *Which waterway does Maersk use?*
""",
    77: """---

# Part 9 — 응용: 그래프 분석 (허브 중요도)

**비즈니스 질문:** *무역 경로 네트워크에서 가장 연결이 많은 허브 항구는 어디인가?*

중심성(centrality) 지표는 **병목**과 **전략적 위치**를 강조합니다.
이 코스에서는 순수 Cypher로 차수 중심성(degree centrality)을 사용합니다(GDS 플러그인 불필요).
""",
    78: """### Step 9.1 — 항구 차수 (무역 경로 이웃 수)
""",
    80: """### Step 9.2 — 운송사 발자국 (운영 차수)
""",
    82: """### Step 9.3 — 선택: Neo4j Graph Data Science (GDS)

프로덕션 분석의 경우 Neo4j Desktop 또는 AuraDS에 **Graph Data Science** 라이브러리를 설치하세요.
**PageRank**, **Louvain 커뮤니티 탐지**, **betweenness centrality** 같은 알고리즘은
투영 그래프에서 실행됩니다. 9.1–9.2의 Cypher 패턴은 추가 플러그인 없이 동일한 직관을 가르칩니다.
""",
    83: """---

# Part 10 — 마무리 및 다음 단계

## 연습한 내용

| 파트 | 응용 | 핵심 Cypher 아이디어 |
|------|-------------|-----------------|
| 3 | 네트워크 탐색 | 다중 홉 `MATCH` |
| 4 | 영향 분석 | 경로 쿼리, `shortestPath` |
| 5 | 엔티티 해소 | `MERGE`, 노드 중복 제거 |
| 6 | 추천 | 공유 이웃 패턴 |
| 7 | 규정 준수 | 정책 → 엔티티 탐색 |
| 8 | 비즈니스 Q&A | LLM + `GraphCypherQAChain` |
| 9 | 분석 | 차수 / 순위 |

## 자신의 도메인에 매핑

`Port` / `Organization`을 **자신의** 산업 엔티티로 교체하세요:

| 도메인 | 노드 예시 | 관계 예시 |
|--------|---------------|----------------------|
| 헬스케어 | Patient, Treatment, Diagnosis | `RECEIVED`, `INDICATED_FOR` |
| 금융 | Account, Transaction, Company | `TRANSFERRED_TO`, `OWNS` |
| 사이버보안 | IP, Domain, Malware | `RESOLVES_TO`, `COMMUNICATES_WITH` |
| HR | Employee, Skill, Project | `HAS_SKILL`, `WORKED_ON` |

## 학습 계속하기

1. **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** — 문서에서 그래프 채우기.
2. **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** — RAG, GraphRAG, agent.
3. **`Module_8_Evaluating_GraphRAG_with_RAGAS.ipynb`** — 답변 품질 측정.

## 정리 (선택)

```cypher
MATCH (n:KGApplicationsLab) DETACH DELETE n;
```

---

*코스 종료 — 실무 지식 그래프 응용*
""",
}

PRINT_REPLACEMENTS: dict[int, list[tuple[str, str]]] = {
    6: [
        ("print('Module directory:', MODULE_DIR)", "print('모듈 디렉터리:', MODULE_DIR)"),
    ],
    8: [
        ("print('Neo4j URI:', NEO4J_URI)", "print('Neo4j URI:', NEO4J_URI)"),
        ("print('Neo4j database:', NEO4J_DATABASE)", "print('Neo4j 데이터베이스:', NEO4J_DATABASE)"),
    ],
    10: [
        ("print('LLM backend:', LLM_BACKEND)", "print('LLM 백엔드:', LLM_BACKEND)"),
        ("print('Ollama host:', OLLAMA_HOST)", "print('Ollama 호스트:', OLLAMA_HOST)"),
        ("print('Ollama model:', OLLAMA_MODEL)", "print('Ollama 모델:', OLLAMA_MODEL)"),
    ],
    12: [
        ("print('Connectivity check passed.')", "print('연결 확인 통과.')"),
    ],
    14: [
        ("print('run_cypher() ready.')", "print('run_cypher() 준비 완료.')"),
    ],
    15: [
        ("print('OLLAMA_RUNNER:', OLLAMA_RUNNER)", "print('OLLAMA_RUNNER:', OLLAMA_RUNNER)"),
    ],
    16: [
        ("print('Ollama helpers defined.')", "print('Ollama 헬퍼 정의 완료.')"),
    ],
    17: [
        (
            "print(f'LLM ready: OpenAI {OPENAI_MODEL}')",
            "print(f'LLM 준비 완료: OpenAI {OPENAI_MODEL}')",
        ),
        (
            "print(f'LLM ready: Ollama {OLLAMA_MODEL} via runner')",
            "print(f'LLM 준비 완료: Ollama {OLLAMA_MODEL} (runner 경유)')",
        ),
        (
            "print('LLM not configured — Part 8 will be skipped unless you set LLM_BACKEND.')",
            "print('LLM 미구성 — LLM_BACKEND를 설정하지 않으면 Part 8을 건너뜁니다.')",
        ),
    ],
    21: [
        (
            "print('Cleared prior KGApplicationsLab data.')",
            "print('이전 KGApplicationsLab 데이터 삭제 완료.')",
        ),
    ],
    23: [
        ("print('Countries and waterways created.')", "print('국가 및 수로 생성 완료.')"),
    ],
    25: [
        ("print(f'Created {len(ports)} ports.')", "print(f'{len(ports)}개 항구 생성 완료.')"),
    ],
    27: [
        (
            "print('Organizations and relationships created.')",
            "print('조직 및 관계 생성 완료.')",
        ),
    ],
    29: [
        ("print(f'Created {len(lanes)} trade lanes.')", "print(f'{len(lanes)}개 무역 경로 생성 완료.')"),
    ],
    31: [
        (
            "print('Regulations linked to shipping organizations.')",
            "print('해운 조직에 규정 연결 완료.')",
        ),
    ],
    33: [
        ("print('\\nTop relationship types:')", "print('\\n상위 관계 유형:')"),
    ],
    36: [
        (
            'print(f"{r[\'carrier\']} → {r[\'port\']} ({r[\'country\']})")',
            'print(f"{r[\'carrier\']} → {r[\'port\']} ({r[\'country\']})")',
        ),
    ],
    38: [
        (
            'print(f"{r[\'port\']} (rank {r[\'global_rank\']})")',
            'print(f"{r[\'port\']} (순위 {r[\'global_rank\']})")',
        ),
    ],
    40: [
        ("print('Netherlands:', carriers_in_country('Netherlands'))", "print('네덜란드:', carriers_in_country('Netherlands'))"),
        ("print('China:', carriers_in_country('China'))", "print('중국:', carriers_in_country('China'))"),
    ],
    43: [
        (
            'print(f"{r[\'carrier\']} depends on {r[\'waterway\']}")',
            'print(f"{r[\'carrier\']} — {r[\'waterway\']} 의존")',
        ),
    ],
    45: [
        (
            'print(f"{r[\'disrupted_route\']}: {r[\'carrier\']} → {r[\'affected_port\']}")',
            'print(f"{r[\'disrupted_route\']}: {r[\'carrier\']} → {r[\'affected_port\']}")',
        ),
    ],
    47: [
        (
            'print(\'Route:\', \' → \'.join(r[\'route\']), f"({r[\'hops\']} hops)")',
            'print(\'경로:\', \' → \'.join(r[\'route\']), f"({r[\'hops\']} 홉)")',
        ),
    ],
    52: [
        (
            "print('Duplicate MSC record created (id=MSC_DUP).')",
            "print('중복 MSC 레코드 생성 완료 (id=MSC_DUP).')",
        ),
    ],
    54: [
        (
            'print(f"Candidate merge: {r[\'id_a\']} + {r[\'id_b\']} (name={r[\'shared_name\']})")',
            'print(f"병합 후보: {r[\'id_a\']} + {r[\'id_b\']} (이름={r[\'shared_name\']})")',
        ),
    ],
    56: [
        ("print('Merged MSC_DUP into MSC.')", "print('MSC_DUP를 MSC에 병합 완료.')"),
    ],
    60: [
        (
            'print(f"{r[\'similar_port\']}: {r[\'shared_carriers\']} shared carrier(s)")',
            'print(f"{r[\'similar_port\']}: 공유 운송사 {r[\'shared_carriers\']}개")',
        ),
    ],
    62: [
        (
            'print(f"{r[\'recommended_carrier\']}: {r[\'european_ports\']} EU port(s)")',
            'print(f"{r[\'recommended_carrier\']}: EU 항구 {r[\'european_ports\']}개")',
        ),
    ],
    65: [
        (
            'print(f"{r[\'organization\']} must follow {r[\'regulation\']} (issued by {r[\'issued_by\']})")',
            'print(f"{r[\'organization\']} — {r[\'regulation\']} 준수 필요 (발행: {r[\'issued_by\']})")',
        ),
    ],
    67: [
        (
            "print('SOLAS applies to:', [r['carrier'] for r in rows])",
            "print('SOLAS 적용 대상:', [r['carrier'] for r in rows])",
        ),
    ],
    72: [
        (
            "print('Schema snippet (first 800 chars):')",
            "print('스키마 일부 (처음 800자):')",
        ),
    ],
    74: [
        (
            "print('Skip: configure LLM_BACKEND in .env (see LLM_MODEL_SETUP.md).')",
            "print('건너뜀: .env에서 LLM_BACKEND를 구성하세요 (LLM_MODEL_SETUP.md 참고).')",
        ),
        ("print('\\nQuestion:', question)", "print('\\n질문:', question)"),
        ("print('Answer:', answer.get('result', answer))", "print('답변:', answer.get('result', answer))"),
    ],
    76: [
        ("print('Q:', MY_QUESTION)", "print('질문:', MY_QUESTION)"),
        ("print('A:', result.get('result', result))", "print('답변:', result.get('result', result))"),
        ("print('Configure LLM to run this cell.')", "print('이 셀을 실행하려면 LLM을 구성하세요.')"),
    ],
    79: [
        (
            'print(f"{r[\'port\']}: {r[\'lane_degree\']} neighbors (throughput rank {r[\'throughput_rank\']})")',
            'print(f"{r[\'port\']}: 이웃 {r[\'lane_degree\']}개 (처리량 순위 {r[\'throughput_rank\']})")',
        ),
    ],
    81: [
        (
            'print(f"{r[\'carrier\']}: {r[\'ports_served\']} port(s)")',
            'print(f"{r[\'carrier\']}: 항구 {r[\'ports_served\']}개")',
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
