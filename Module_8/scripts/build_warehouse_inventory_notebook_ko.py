#!/usr/bin/env python3
"""Build Korean Module_8 Warehouse Inventory notebook from the English source."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Module_8_Warehouse_Inventory_Management_with_Knowledge_Graphs.ipynb"
DST = ROOT / "Module_8_Warehouse_Inventory_Management_with_Knowledge_Graphs_KO.ipynb"

MARKDOWN_KO: dict[int, str] = {
    0: """# 지식 그래프(Knowledge Graph)로 창고 및 재고 관리 실무 향상

**코스 모듈:** Module 8
**대상:** 실제 공급망(supply-chain) 운영 데이터에 Neo4j를 적용하려는 초급 학습자

## 코스 설명

창고 및 재고 팀은 **재고 수준(stock levels)**, **수요 신호(demand signals)**, **장비 가용성(equipment availability)**,
**공급업체 신뢰도(supplier reliability)**, **운영 리스크(operational risk)**를 관리합니다 — 종종 스프레드시트와
대시보드에 흩어져 있습니다. **지식 그래프(Knowledge Graph)**는 이러한 사실을 명시적으로 연결하여 SQL만으로는
다루기 어려운 관계 질문을 할 수 있게 합니다.

이 실습 코스에서는 다음을 수행합니다:

1. **물류 및 공급망(Logistics and Supply Chain)** CSV 데이터셋을 탐색합니다(창고 중심 관점).
2. 재고 관리를 위한 **도메인 그래프 모델**을 설계합니다.
3. Neo4j에 전용 서브그래프를 로드합니다(레이블 **`WarehouseInventoryLab`** — 다른 코스 그래프와 격리).
4. 재고 리스크, 이행(fulfillment), 장비 병목에 대한 **실무 Cypher 쿼리**를 실행합니다.
5. (선택) LLM + Cypher 체인으로 **자연어 질문**을 합니다.

> **언어:** 이 노트북의 안내 텍스트는 **한국어**입니다. 기술 용어는 필요 시 영어를 병기합니다.

> **설정(필수):** 코드 실행 전 **`NEO4J_SETUP.md`**를 완료하세요.
> 선택 LLM 섹션의 경우 **`LLM_MODEL_SETUP.md`**를 완료하고 **`ollama_model_runner.py`**를 실행하세요
> (또는 OpenAI를 구성).

### 이 노트북 사용법

1. 아래 **코드** 셀을 실행하기 전에 각 **마크다운** 셀을 읽으세요.
2. Step 0부터 **순서대로** 셀을 실행하세요.
3. 랩 데이터는 **`WarehouseInventoryLab`** 레이블을 사용합니다 — `CourseKG`, `KGApplicationsLab`,
   `LangChainLab`, `LlamaIndexLab`에 영향을 주지 않고 안전하게 삭제 후 재시드할 수 있습니다.
4. 코드 셀은 의도적으로 **짧게** 작성되었습니다. 마크다운이 각 단계의 *이유*를 설명합니다.
""",
    1: """## 사전 요구 사항

| 기술 | 필요한 이유 |
|-------|-----------------|
| Neo4j 기초 | 노드, 관계, `MATCH`, `RETURN` |
| Python & pandas | CSV 로드 및 변환 |
| (선택) LLM | Part 10 — 자연어 재고 Q&A |

### 데이터셋

| 파일 | 설명 |
|------|-------------|
| `data/logistics-supply-chain/dynamic_supply_chain_logistics_dataset.csv` | 시간별 물류 원격 측정 데이터(Kaggle, CC0-1.0) |

GPS 좌표에서 **창고 지역(warehouse regions)**을 도출하고, 읽기를 **주간 스냅샷(weekly snapshots)**으로 집계하여
초급자에게 적합한 그래프(~2,000 노드)를 만듭니다.

## 코스 개요

| 파트 | 주제 | 비즈니스 질문 |
|------|--------|-------------------|
| **0** | 환경 및 Neo4j 연결 | — |
| **1** | 창고를 위한 지식 그래프 | 그래프가 평면 테이블보다 나은 경우 |
| **2** | CSV 탐색 | 데이터에 어떤 신호가 있는가? |
| **3** | 그래프 모델 설계 | 어떤 엔티티와 관계가 필요한가? |
| **4** | Python으로 데이터 변환 | 행에서 그래프 레코드로 어떻게 가는가? |
| **5** | Neo4j에 로드 | 격리된 랩 서브그래프를 어떻게 시드하는가? |
| **6** | 저재고 탐지 | *어떤 창고가 심각하게 재고가 부족한가?* |
| **7** | 수요 vs 재고 | *수요가 가용 재고보다 높은 곳은 어디인가?* |
| **8** | 리스크 및 장비 스트레스 | *리스크와 장비 제약이 겹치는 곳은 어디인가?* |
| **9** | 공급업체 신뢰도 경로 | *어떤 스냅샷이 취약한 공급업체에 의존하는가?* |
| **10** | 비즈니스 Q&A (LLM + Cypher) | *일반 영어로 질문하기* |
| **11** | 고급 개선 사항(읽기) | 스스로 탐색할 다음 단계 |
| **12** | 마무리 | 패턴을 조직에 매핑 |
""",
    2: """---

# Step 0 — 환경 및 Neo4j 연결

### 코드 실행 전

1. **`NEO4J_SETUP.md`** 완료 — Aura, Desktop 또는 Docker; URI, 사용자명, 비밀번호 확인.
2. `Module_8/.env.example` → `Module_8/.env` 복사 후 Neo4j 자격 증명 입력.
3. **Part 10**(LLM Q&A)의 경우 **`LLM_MODEL_SETUP.md`**도 완료하고 `ollama serve`를 시작하세요.

### Step 0에서 하는 일

| Step | 목적 |
|------|---------|
| 0a | Python 패키지 설치 |
| 0b | 경로 및 환경 변수 로드 |
| 0c | Neo4j Bolt 연결 확인 |
| 0d | 헬퍼 정의(`run_cypher`, 선택 Ollama runner) |
""",
    3: """### Step 0a — Python 패키지 설치

**이 셀이 하는 일:** 노트북 나머지 부분에 필요한 Python 라이브러리를 설치합니다.

**실행 시점:** 가상 환경(conda, venv 또는 시스템 Python)당 한 번. 다른 Module 8 노트북에서
이미 설치했다면 이 셀을 건너뛸 수 있습니다.

| 패키지 | 이 코스에서의 역할 |
|---------|---------------------|
| `neo4j` | 공식 Bolt 드라이버 — Python을 Neo4j 데이터베이스에 연결 |
| `python-dotenv` | `Module_8/.env`를 로드하여 비밀을 노트북 밖에 유지 |
| `requests` | `ollama_model_runner.py`에서 간접적으로 사용하는 HTTP 호출 |
| `pandas` | 그래프 로드 전 물류 CSV 로드 및 변환 |
| `langchain`, `langchain-neo4j`, `langchain-openai` | Part 10 — 자연어 → Cypher Q&A |

**예상 출력:** Pip은 아무것도 출력하지 않을 수 있습니다(`-q` 조용 모드). 다음 셀은 `ModuleNotFoundError` 없이 import되어야 합니다.

> **문제 해결:** 설치가 실패하면 먼저 코스 가상 환경을 활성화한 후 다시 실행하세요.
> 전체 의존성 설명은 **`NEO4J_SETUP.md`**(Python 환경 섹션)에 있습니다.
""",
    5: """### Step 0b.1 — `Module_8` 폴더 확인

**이 셀이 하는 일:** 디스크에서 `Module_8` 디렉터리 위치를 찾고 `.env` 파일을 로드합니다.

**중요한 이유:** Jupyter의 *현재 작업 디렉터리*는 노트북 실행 방식에 따라 달라집니다:

- **저장소 루트**(`KMOU_Course/`)에서 노트북을 열면 `data/...` 같은 경로가 잘못될 수 있어 조정이 필요합니다.
- **`Module_8/`**에서 열면 경로가 바로 작동합니다.

로직은 `Path('.').name`을 확인합니다: `Module_8`이 아니면 자식 폴더 `Module_8/`을 찾습니다.

**핵심 줄:**

- `load_dotenv(MODULE_DIR / '.env')` — `NEO4J_URI`, `NEO4J_PASSWORD`, `LLM_BACKEND` 등을 읽습니다.
- `print('Module directory:', ...)` — `data/`와 `.env`가 있는 폴더를 가리키는지 확인하세요.

**예상 출력:**

```text
Module directory: /path/to/KMOU_Course/Module_8
```

> **문제 해결:** `.env`가 없으면 `Module_8/.env.example` → `Module_8/.env`를 복사하고 **`NEO4J_SETUP.md`**에 따라 Neo4j 자격 증명을 입력하세요.
""",
    7: """### Step 0b.2 — 경로, 랩 레이블, Neo4j 설정

**이 셀이 하는 일:** 이후 모든 단계에서 사용하는 상수를 정의합니다 — 데이터셋 경로, 랩 격리 레이블,
Neo4j 연결 매개변수, 조정 가능한 랩 제한.

**설정 변수:**

| 변수 | 기본값 | 의미 |
|----------|---------|---------|
| `DATA_PATH` | `data/logistics-supply-chain/...csv` | 창고 랩용 소스 CSV |
| `LAB_LABEL` | `WarehouseInventoryLab` | 이 코스의 **모든** 노드에 붙는 마커 레이블 |
| `LAB_TOP_WAREHOUSES` | `15` | 모델링할 가장 바쁜 GPS 지역 수(`.env`로 재정의 가능) |
| `LAB_BATCH_SIZE` | `100` | 로드 중 Neo4j `UNWIND` 배치당 행 수 |
| `NEO4J_URI` | `neo4j://localhost:7687` | Bolt URL — Aura는 `neo4j+s://...` 사용 |
| `NEO4J_DATABASE` | `neo4j` | 데이터베이스 이름(Aura Free: 보통 `neo4j`) |

**`LAB_LABEL`이 중요한 이유:** 다른 Module 8 노트북은 다른 레이블(`CourseKG`, `LangChainLab` 등)을 사용합니다.
모든 노드에 `WarehouseInventoryLab`을 태그하면 다른 노트북에서 구축한 그래프에 영향을 주지 않고
**이 랩의 그래프만** 삭제하거나 쿼리할 수 있습니다.

**예상 출력:**

- `Dataset exists: True` — `False`이면 Kaggle CSV를 `data/logistics-supply-chain/`에 다운로드하세요.
- `Neo4j URI:`는 설정과 일치해야 합니다(로컬 Docker 또는 Aura).
""",
    9: """### Step 0b.3 — LLM 설정 (Part 10 전용)

**이 셀이 하는 일:** LLM 관련 환경 변수를 읽습니다. Part 1–9는 **Cypher만** 사용합니다;
Part 10에서 자연어 질의응답을 추가합니다.

**지원되는 두 백엔드:**

| `LLM_BACKEND` | 모델 호출 방식 | 설정 가이드 |
|---------------|-------------------------|-------------|
| `ollama` (권장) | Subprocess → `ollama_model_runner.py` → Ollama HTTP API | **`LLM_MODEL_SETUP.md`** 옵션 1 |
| `openai` | `langchain_openai.ChatOpenAI` | **`LLM_MODEL_SETUP.md`** 옵션 2 |

**Ollama 변수:**

- `OLLAMA_HOST` — `ollama serve` 실행 중이면 보통 `http://localhost:11434`.
- `OLLAMA_MODEL` — 예: `llama3.2:3b`(빠름) 또는 `llama3.1:8b`(Cypher 생성 품질 향상).
- `OLLAMA_MAX_TOKENS` — 응답 길이 상한; 답변이 잘리면 늘리세요.

**Part 10을 건너뛸 수 있습니다** — 창고 Cypher 연습만 원한다면 — 하지만 이 셀 실행은 무해합니다.

**예상 출력:** `LLM backend: ollama` (또는 `openai`).
""",
    11: """### Step 0c — Neo4j 연결 확인

**이 셀이 하는 일:** Neo4j에 짧은 Bolt 세션을 열고 한 줄 스모크 테스트를 실행합니다.

**데이터 로드 전에 하는 이유:** 연결 문제를 일찍 발견하면 Part 5 중 디버깅 시간을 절약합니다.
일반적인 실패는 여기서 발생합니다 — 잘못된 비밀번호, 데이터베이스 미실행, 잘못된 URI 스킴.

**동작 방식:**

1. `GraphDatabase.driver(NEO4J_URI, auth=(username, password))` — 드라이버(연결 풀) 생성.
2. `session.run('RETURN "Neo4j connection OK" AS message')` — 가장 단순한 쿼리.
3. `driver.close()` — 리소스 해제.

**예상 출력:**

```text
Neo4j connection OK
Connectivity check passed.
```

> **문제 해결:** **`NEO4J_SETUP.md`** 참고 — Docker 컨테이너 미실행, Aura URI 오타,
> `.env`의 빈 `NEO4J_PASSWORD`. Aura는 `neo4j+s://` 필요; 로컬 Docker는 `neo4j://` 사용.
""",
    13: """### Step 0d.1 — Cypher 헬퍼

**이 셀이 하는 일:** `run_cypher(query, params)` — Neo4j 드라이버를 감싼 재사용 가능한 래퍼를 정의합니다.

**드라이버 코드 반복 대신 헬퍼를 쓰는 이유:** Part 5–9의 모든 쿼리마다 5–6줄의 연결 보일러플레이트가
반복됩니다. 헬퍼는 **코드 셀을 짧게** 유지하고 Cypher에 집중하게 합니다.

**함수 동작:**

- 드라이버를 열고 선택적 매개변수(`$rows`, `$values` 등)로 쿼리 실행,
- 각 결과 레코드를 Python `dict`로 변환,
- 루프하거나 검사할 수 있는 `list[dict]` 반환.

**매개변수화 쿼리:** `params={'rows': batch}`를 전달하면 문자열 연결 버그와 injection 위험을 방지합니다.
Neo4j는 Cypher 내부에서 `$rows`를 안전하게 치환합니다.

**예상 출력:** `run_cypher() ready.`
""",
    15: """### Step 0d.2 — `ollama_model_runner.py` 위치 찾기

**이 셀이 하는 일:** `ollama_model_runner.py` 경로를 찾고 LangChain 기본 클래스를 import합니다.

**별도 runner 스크립트를 쓰는 이유:** Module 4/5/8은 동일한 패턴을 사용합니다 — Jupyter 커널이 노트북 내부가 아닌
subprocess로 Ollama를 호출합니다. 긴 생성 시 커널 크래시를 피하고 **`LLM_MODEL_SETUP.md`**와 일치합니다.

**검색 순서:**

1. `Module_8/ollama_model_runner.py` (기본)
2. `Module_4/ollama_model_runner.py` (대체)
3. 현재 디렉터리

**예상 출력:** `OLLAMA_RUNNER:` 뒤에 전체 경로가 출력됩니다.

> Cypher만 연습한다면 Part 10까지 Step 0d.2–0d.4를 건너뛰세요.
""",
    17: """### Step 0d.3 — `call_ollama_runner()` 및 `OllamaRunnerLLM`

**이 셀이 하는 일:** 두 가지를 구현합니다:

1. **`call_ollama_runner(prompt)`** — 프롬프트를 임시 파일에 쓰고 runner 스크립트를 호출한 뒤 JSON stdout을 파싱합니다.
2. **`OllamaRunnerLLM`** — `GraphCypherQAChain`이 OpenAI와 동일한 방식으로 Ollama를 호출할 수 있도록 하는 얇은 LangChain `LLM` 래퍼입니다.

**프롬프트에 임시 파일을 쓰는 이유:** Part 10의 창고 질문은 길 수 있습니다; `--prompt-file`로 전달하면
셸 이스케이프 문제를 피합니다.

**오류 처리:** Ollama가 실행 중이 아니거나 모델 이름이 잘못되면 stderr가 포함된 `RuntimeError`가 발생합니다 —
**`LLM_MODEL_SETUP.md`**에 따라 `ollama serve`와 `ollama list`를 확인하세요.

**예상 출력:** `Ollama helpers defined.`
""",
    19: """### Step 0d.4 — LLM 객체 인스턴스화

**이 셀이 하는 일:** Part 10의 `GraphCypherQAChain`에서 사용하는 `llm` 변수를 생성합니다.

**분기 로직:**

- `LLM_BACKEND=openai` → `.env`에 `OPENAI_API_KEY` 필요; `ChatOpenAI` 사용.
- `LLM_BACKEND=ollama` → `OllamaRunnerLLM()` 사용(클라우드 API 키 불필요).
- 그 외 → `llm = None`; Part 10 셀은 건너뛰기 메시지를 출력합니다.

**예상 출력:**

```text
LLM ready: Ollama llama3.2:3b via runner
```

> Part 10이 나중에 실패하면 **`LLM_MODEL_SETUP.md`**의 스모크 테스트를 실행하세요.
""",
    21: """---

# Part 1 — 창고 및 재고 관리를 위한 지식 그래프

### 운영 문제

창고 관리자는 다음을 추적합니다:

- **재고 수준(inventory levels)** — 보유 재고량
- **수요 신호(demand signals)** — 고객 또는 하류 사이트가 필요로 하는 것
- **이행 성과(fulfillment performance)** — 주문이 제시간에 완료되는가?
- **하역 장비(handling equipment)** — 지게차, 컨베이어, 도크 도어 — 가용한가?
- **공급업체 신뢰도(supplier reliability)** — 보충이 약속대로 도착하는가?
- **리스크 요인(risk factors)** — 날씨, 혼잡, 경로 중단

관계형 데이터베이스에서는 각 주제가 별도 테이블에 있습니다. 다음 질문에 답하려면
*"어떤 창고가 재고가 부족**하고** 장비가 제약**되고** 같은 주에 운영 리스크가 높은가?"*
여러 팩트 테이블을 신중하게 조인해야 합니다.

### 지식 그래프가 추가하는 것

| 관계형 패턴 | 그래프 패턴 |
|-------------------|---------------|
| 여러 테이블 `JOIN` | 타입이 있는 관계 탐색 |
| 열 이름에 암묵적 링크 | 명시적 엣지(`HAS_SNAPSHOT`, `HAS_RISK`) |
| 비즈니스 사용자에게 설명 어려움 | Neo4j Browser의 시각적 모델 |

### 이 코스에서 가르치는 기본 방법(구조화 ETL → 그래프)

1. CSV 열과 비즈니스 의미를 **이해**합니다.
2. 엔티티를 **모델링**합니다: `Warehouse`, `InventorySnapshot`, `RiskCategory` 등.
3. Python으로 표 형식 행을 노드와 관계로 **변환**합니다.
4. 배치 Cypher(`UNWIND`)로 Neo4j에 **로드**합니다.
5. 재고 의사결정을 위해 Cypher로 **쿼리**합니다.

> CSV/ERP/WMS보내기에 운영 데이터가 이미 있을 때 가장 흔한 **프로덕션** 패턴입니다.
""",
    22: """---

# Part 2 — 물류 데이터셋 탐색

Kaggle 데이터셋에는 합성 공급망 네트워크의 **시간별 원격 측정**이 포함됩니다.
GPS 좌표는 차량/창고 위치를 나타냅니다; 이를 **창고 지역**으로 클러스터링합니다.

### 재고 관리와 가장 관련 있는 열

| 열 | 재고/창고 의미 |
|--------|------------------------------|
| `warehouse_inventory_level` | 보유 재고(단위) |
| `historical_demand` | 계획용 수요 신호 |
| `order_fulfillment_status` | 이행률(0–1) |
| `handling_equipment_availability` | 장비 가용성(0–1) |
| `loading_unloading_time` | 도크 활동 지속 시간 |
| `supplier_reliability_score` | 공급업체 신뢰도(0–1) |
| `risk_classification` | Low / Moderate / High 운영 리스크 |
| `vehicle_gps_latitude/longitude` | 창고 지역용 위치 프록시 |
""",
    23: """### Step 2.1 — CSV 로드

**이 셀이 하는 일:** Kaggle 물류 CSV를 `raw_df`라는 pandas DataFrame으로 읽습니다.

**Neo4j 전에 pandas를 쓰는 이유:** 지식 그래프는 Neo4j 전에 **구조화된 레코드**가 필요합니다. pandas는
필터링, 집계, 파생 열을 위한 교육 친화적 계층입니다. 프로덕션 파이프라인은 dbt, Spark 또는 ETL 도구를
사용할 수 있지만 — 그래프 모델링 단계는 동일합니다.

**핵심 연산:**

- `parse_dates=['timestamp']` — Part 4의 주간 그룹화를 가능하게 합니다.
- `raw_df.head(3)` — 처음 몇 행 미리보기; Jupyter는 셀 아래에 테이블을 표시합니다.

**예상 출력:** 행 수(~32,065)와 열 수(26). 3행 테이블 미리보기.

> **문제 해결:** `FileNotFoundError`는 CSV가 `DATA_PATH`에 없다는 뜻입니다. `data/DATASETS.md`에 따라 다운로드하세요.
""",
    25: """### Step 2.2 — 재고 관련 열 검사

**이 셀이 하는 일:** 창고 및 재고 관리 개념에 매핑되는 열에 대해 기술 통계(`count`, `mean`, `min`, `max`, `std`)를 계산합니다.

**테이블 읽는 법:**

| 열 | 주목할 점 |
|--------|----------------|
| `warehouse_inventory_level` | 일반 범위 0–1000; 이후 재고 상태 레이블에 사용 |
| `historical_demand` | 재고보다 종종 큼 — Part 7에서 양의 `demand_gap` 예상 |
| `order_fulfillment_status` | 0–1 척도; 1에 가까우면 이행 양호 |
| `handling_equipment_availability` | 0–1 척도; 낮은 값은 Part 8에서 장비 경보 유발 |
| `supplier_reliability_score` | 0–1 척도; Low/Medium/High 등급으로 버킷팅 |

**지금 26열 전체를 로드하지 않는 이유:** 초급자는 재고 스토리에 먼저 집중합니다. 다른 열
(`port_congestion_level`, `iot_temperature`)도 확장 연습을 위해 스냅샷 노드에 저장됩니다.

**예상 출력:** 통계당 한 행이 있는 스타일 `describe()` 테이블.
""",
    27: """### Step 2.3 — 리스크 분포

**이 셀이 하는 일:** 각 `risk_classification` 버킷에 속하는 시간별 행 수를 셉니다.

**비즈니스 의미:** 리스크는 합성 데이터셋의 복합 신호입니다(교통, 날씨, 중단 등).
창고 계획자에게 **High Risk** 주는 보충 및 이행을 어렵게 하는 상관이 있습니다.

**그래프 모델링 선택:** 모든 스냅샷에 문자열 속성으로만 리스크를 저장하는 대신
**공유 `RiskCategory` 노드**(`Low Risk`, `Moderate Risk`, `High Risk`)를 만듭니다. 많은 스냅샷이
`[:HAS_RISK]`로 동일 노드에 연결됩니다. 중복 문자열 스캔 없이 *"모든 창고에서 High Risk 스냅샷 수"* 같은
쿼리가 가능합니다.

**예상 출력:** `High Risk`가 보통 지배적(~75% 행). pandas 버전에 따라 정확한 수는 약간 다를 수 있습니다.
""",
    29: """### Step 2.4 — GPS에서 창고 지역 도출

**이 셀이 하는 일:** GPS 좌표를 정수 도 단위로 반올림하여 합성 `warehouse_id`를 만듭니다.

**이 해킹이 있는 이유:** 실제 WMS/ERP보내기에는 `warehouse_code`가 있습니다. 이 Kaggle 파일에는
위치 프록시로 `vehicle_gps_latitude` / `vehicle_gps_longitude`만 있습니다. lat/lon 빈닝은 시설 마스터 데이터의
**교육용 대체**입니다.

**ID 형식:** `WH_40.0_-77.0`은 "40°N, 77°W 근처 중심 지역"을 의미합니다.

**트레이드오프:**

| 접근 | 장점 | 단점 |
|----------|------|------|
| 정수 도 빈(이 랩) | 단순, 빠름, 적은 지역 | 거친 지리 |
| 더 세밀한 빈(0.1°) | 더 정밀 | ~22k 지역 — 초급자에게 너무 큼 |
| 실제 창고 마스터 | 프로덕션 정확 | 내부 데이터 필요 |

Neo4j 그래프를 교실 규모로 유지하기 위해 Part 4에서 **가장 바쁜 상위 15개** 지역만 유지합니다.

**예상 출력:** 전체 데이터에서 수천 개의 고유 지역; 상위 지역은 각각 수백 개의 시간별 읽기를 보여줍니다.
""",
    31: """---

# Part 3 — 창고 재고 그래프 모델 설계

## 3.1 엔티티-관계 스케치

```text
(Warehouse)-[:HAS_SNAPSHOT]->(InventorySnapshot)
(InventorySnapshot)-[:IN_WEEK]->(TimeWeek)
(InventorySnapshot)-[:HAS_RISK]->(RiskCategory)
(InventorySnapshot)-[:HAS_INVENTORY_STATUS]->(InventoryStatus)
(InventorySnapshot)-[:HAS_SUPPLIER_TIER]->(SupplierTier)
(InventorySnapshot)-[:HAS_EQUIPMENT_STATUS]->(EquipmentStatus)
(InventorySnapshot)-[:HAS_FULFILLMENT_STATUS]->(FulfillmentStatus)
```

## 3.2 노드 레이블

| 레이블 | 역할 |
|-------|------|
| `Warehouse` | 지리적 재고 허브(GPS에서 클러스터링) |
| `InventorySnapshot` | 주간 집계 운영 읽기 |
| `TimeWeek` | 달력 주 버킷 |
| `RiskCategory` | Low / Moderate / High 리스크(공유 참조) |
| `InventoryStatus` | Critical / Low / Balanced / Overstock |
| `SupplierTier` | Low / Medium / High 공급업체 신뢰도 |
| `EquipmentStatus` | Critical / Constrained / Available 장비 |
| `FulfillmentStatus` | Behind / AtRisk / OnTrack 이행 |
| **`WarehouseInventoryLab`** | **모든** 랩 노드의 마커(다른 그래프와 격리) |

## 3.3 다른 Module 8 그래프와의 격리

모든 노드에 `WarehouseInventoryLab`이 포함됩니다. 이 코스만 지우려면:

```cypher
MATCH (n:WarehouseInventoryLab) DETACH DELETE n;
```

다른 코스 레이블(`CourseKG`, `KGApplicationsLab`, `LangChainLab`, `LlamaIndexLab`)은 그대로입니다.

## 3.4 설계 원칙(Part 4 전에 읽기)

1. **스냅샷을 팩트로** — 각 `InventorySnapshot`은 창고-주 관측 하나(팩트 테이블 행과 유사).
2. **카테고리를 차원으로** — 상태 노드(`InventoryStatus`, `RiskCategory`, …)는 스타 스키마의 차원 테이블처럼 동작하지만 **일급 그래프 노드**로.
3. **명시적 시간** — `TimeWeek` 노드로 문자열 파싱 없이 *"창고 간 동일 주"* 쿼리 가능.
4. **속성 + 관계** — 숫자 지표는 스냅샷에; 범주 레이블은 탐색 가능한 엣지로.
""",
    32: """---

# Part 4 — 표 형식 데이터를 그래프 레코드로 변환

Part 4는 pandas와 Neo4j 사이의 **ETL 브리지**입니다. 아래 코드를 실행하기 전에 각 마크다운 셀을 읽으세요.

### 전체 전략

1. **상위 N개** 가장 바쁜 창고 지역 유지(`LAB_TOP_WAREHOUSES`, 기본 15).
2. 시간별 행을 **주간** 스냅샷으로 집계(숫자 필드는 평균, 리스크는 최빈값).
3. 연속 값을 **비즈니스 카테고리**로 분류(재고 상태, 장비 상태 등).
4. Part 5 Neo4j `UNWIND` 로드용 Python 딕셔너리 생성.

**Part 4 출력:** 두 리스트 — `warehouse_records`(~15 dict)와 `snapshot_records`(~2,000 dict).
""",
    33: """### Step 4.1 — 분류 헬퍼 함수

**이 셀이 하는 일:** 연속 측정값을 그래프 노드 ID로 사용되는 **비즈니스 카테고리**로 바꾸는 Python 함수를 정의합니다.

**분류를 하는 이유:** Part 6–9의 Cypher 쿼리는 `Critical` 또는 `High Risk` 같은 레이블로 필터합니다.
버킷 함수는 운영 팀의 사고 방식을 반영합니다 — 계획자는 *"inventory < 137.2"*보다
*"critical stock"*을 묻습니다.

**임계값 참조(이 랩):**

| 함수 | 입력 | 출력 버킷 |
|----------|-------|----------------|
| `classify_inventory_status` | `inventory_level` | Critical (<100), Low (<250), Balanced (<600), Overstock |
| `classify_supplier_tier` | `supplier_score` 0–1 | Low / Medium / High |
| `classify_equipment_status` | `equipment_availability` 0–1 | Critical / Constrained / Available |
| `classify_fulfillment_status` | `fulfillment_rate` 0–1 | Behind / AtRisk / OnTrack |

> **프로덕션 참고:** 임계값은 SLA와 ABC 분석에서 와야 합니다 — 조직에 맞게 함수를 조정하세요.

**예상 출력:** `Classification helpers ready.`
""",
    35: """### Step 4.2 — 상위 창고 필터 및 주별 집계

**이 셀이 하는 일:**

1. 행 수 기준 **상위 `LAB_TOP_WAREHOUSES`** 지역 선택(CSV에서 가장 바쁜 위치).
2. pandas `Period('W')`로 `week` 열 추가 — ISO 스타일 주 버킷.
3. `groupby(['warehouse_id', 'week']).agg(...)`로 시간별 노이즈를 **창고당 주당 한 행**으로 축소.

**집계 선택:**

| 필드 | 집계 | 이유 |
|-------|-------------|--------|
| 숫자 지표 | `mean` | 시간별 스파이크를 주간 대표값으로 평활화 |
| `risk_classification` | `mode`(최빈) | 해당 주의 지배적 리스크 레이블 선택 |

**시간별이 아닌 주간인 이유:** ~32k 시간별 행 → 15개 창고에 ~2k 주간 행 — Neo4j 로드 빠름,
Browser 시각화 쉬움, 교육 쿼리에 충분한 신호.

**예상 출력:**

```text
Warehouses modeled: 15
Weekly snapshots: ~1995
```

및 `weekly_df` 3행 미리보기.
""",
    37: """### Step 4.3 — 각 스냅샷에 그래프 카테고리 부착

**이 셀이 하는 일:** ETL을 마무리하며 다음을 추가합니다:

- `snapshot_id` — 각 창고-주에 대한 고유 키 `WH_...__2021-01-01/...`.
- 카테고리 열 — `inventory_status`, `supplier_tier`, `equipment_status`, `fulfillment_status`.
- `demand_gap` — `demand - inventory_level`; 양수 ⇒ 수요가 보유 재고를 초과.

**두보내기 구조:**

| 변수 | 내용 | Part 5 단계에서 사용 |
|----------|----------|---------------------|
| `warehouse_records` | 창고당 dict 하나(`warehouse_id`, lat, lon) | Step 5.3 |
| `snapshot_records` | 모든 지표 + 카테고리가 있는 창고-주당 dict 하나 | Step 5.4 |

`to_dict(orient='records')`는 DataFrame을 dict 리스트로 변환 — Cypher에 `$rows`를 전달할 때
Neo4j Python 드라이버가 기대하는 형식입니다.

**예상 출력:** 스냅샷 및 창고 수; 상태와 `demand_gap`이 있는 5행 미리보기.
""",
    39: """---

# Part 5 — 창고 재고 그래프를 Neo4j에 로드

네 단계로 로드합니다:

1. 이전 `WarehouseInventoryLab` 데이터 삭제.
2. **참조 카테고리** 노드 생성(리스크, 재고 상태 등).
3. **창고** 노드 생성.
4. **주간 스냅샷** 및 관계를 배치 로드.

**아래 각 코드 셀 전에 읽으세요.** Step 5.1–5.4는 순서대로 실행해야 합니다. Step 5.5는 성공을 확인합니다.
Step 5.6은 Browser 연습(Python 없음).
""",
    40: """### Step 5.1 — 이전 랩 서브그래프 삭제

**이 셀이 하는 일:** `WarehouseInventoryLab` 레이블이 있는 **모든** 노드(및 관계)를 삭제합니다.

**먼저 삭제하는 이유:** 삭제 없이 Part 5를 다시 실행하면 스냅샷이 **중복**되고 수가 부풀어 오릅니다.
이 패턴은 코스 노트북에서 표준입니다 — 랩 데이터를 지우고 재구축.

**안전:** 쿼리는 `MATCH (n:WarehouseInventoryLab) DETACH DELETE n`입니다.

- `DETACH DELETE`는 관계 **와** 노드를 제거합니다.
- `WarehouseInventoryLab`이 없는 노드(다른 노트북)는 **매칭되지 않습니다**.

**예상 출력:** `Cleared prior WarehouseInventoryLab data.`

> **경고:** 이 랩의 그래프만 파괴합니다. 레이블을 `:Node` 같은 넓은 이름으로 바꾸지 마세요.
""",
    42: """### Step 5.2 — 참조 카테고리 노드 생성

**이 셀이 하는 일:** 스냅샷 로드 전에 범주 값에 대한 **차원 스타일** 노드를 생성합니다.

**카테고리를 먼저 로드하는 이유:** Step 5.4는 `MATCH (risk:RiskCategory ... {id: row.risk})`를 사용합니다 — 해당 노드가 있어야 합니다.
참조를 먼저 만들면 철자도 일관됩니다(`High Risk` vs `high risk`).

**`MERGE` vs `CREATE`:** `MERGE`는 *없으면 생성, 있으면 재사용* — Step 5.2만 다시 실행해도 안전.

**생성되는 노드 유형:**

- `RiskCategory` (3값)
- `InventoryStatus` (4값)
- `SupplierTier`, `EquipmentStatus`, `FulfillmentStatus` (각 3값)

각 노드는 `:RiskCategory:WarehouseInventoryLab`(예) 레이블과 속성 `id`, `name`을 받습니다.

**예상 출력:** `Reference categories created.`
""",
    44: """### Step 5.3 — 창고 노드 생성

**이 셀이 하는 일:** `UNWIND $rows`로 `warehouse_records`의 항목마다 `Warehouse` 노드 하나를 로드합니다.

**저장되는 속성:**

| 속성 | 의미 |
|----------|---------|
| `id` | ETL의 `warehouse_id`와 동일(예: `WH_30.0_-70.0`) |
| `latitude`, `longitude` | 해당 지역의 평균 GPS — 이후 지도 오버레이에 유용 |
| `region_label` | Browser 캡션용 읽기 쉬운 `id` 복제 |

**`UNWIND` 패턴:** Cypher가 한 트랜잭션에서 Python 리스트를 반복 — 15개의 별도 쿼리보다 빠름.

**예상 출력:** `Loaded 15 warehouse nodes.` (또는 `LAB_TOP_WAREHOUSES` 값).
""",
    46: """### Step 5.4 — 재고 스냅샷 배치 로드

**이 셀이 하는 일:** `LAB_BATCH_SIZE`(기본 100) 배치로 모든 `snapshot_records`를 로드합니다.
각 행마다 `InventorySnapshot` 노드 하나와 **여섯 관계**를 만듭니다.

**행당 생성되는 그래프 패턴:**

```text
(Warehouse)-[:HAS_SNAPSHOT]->(InventorySnapshot)-[:IN_WEEK]->(TimeWeek)
(InventorySnapshot)-[:HAS_RISK]->(RiskCategory)
(InventorySnapshot)-[:HAS_INVENTORY_STATUS]->(InventoryStatus)
(InventorySnapshot)-[:HAS_SUPPLIER_TIER]->(SupplierTier)
(InventorySnapshot)-[:HAS_EQUIPMENT_STATUS]->(EquipmentStatus)
(InventorySnapshot)-[:HAS_FULFILLMENT_STATUS]->(FulfillmentStatus)
```

**배치를 쓰는 이유:** ~2,000 스냅샷을 한 쿼리로 하면 느린 인스턴스에서 타임아웃; 100개씩 20배치가 부드럽습니다.

**`TimeWeek`의 `MERGE`:** 여러 창고가 같은 달력 주를 공유 — 주 문자열당 `TimeWeek` 노드 하나.

**실행 시간:** Neo4j 배포(Aura vs 로컬 Docker)에 따라 30초에서 수 분.

**예상 출력:** `Loaded 1995 inventory snapshots.` (대략).
""",
    48: """#### Step 5.4 이후 — 방금 무슨 일이 있었나?

대략 **이천 개**의 `InventorySnapshot` 노드를 로드했으며, 각각 다음에 연결됩니다:

- `Warehouse` 하나(상위 사이트),
- `TimeWeek` 하나(공유 달력 버킷),
- 카테고리 노드 다섯 개(리스크, 재고, 공급업체, 장비, 이행).

셀이 예외 없이 끝났는데 Part 6 결과가 비어 있으면 Step 5.5를 실행하세요 —
수에서 `InventorySnapshot`이 수천 개여야 합니다.
""",
    49: """### Step 5.5 — 그래프 수 확인

**이 셀이 하는 일:** 모든 `WarehouseInventoryLab` 노드를 *기본* 레이블별로 그룹화하고 수를 출력합니다.

**결과 해석:**

| node_type | 대략적 수 | 정상 확인 |
|-----------|-------------------|--------------|
| `InventorySnapshot` | ~1,995 | 가장 큼 — 창고-주당 하나 |
| `TimeWeek` | ~수백 | 더 작음 — 창고 간 주 공유 |
| `Warehouse` | 15 | `LAB_TOP_WAREHOUSES`와 일치 |
| `RiskCategory` 등 | 각 3–4 | 작은 고정 참조 집합 |

`InventorySnapshot`이 0이면 Step 5.1–5.4를 다시 실행하고 위 Cypher 오류를 확인하세요.

**예상 출력:** 레이블 → 수 쌍의 출력 목록.
""",
    51: """### Step 5.6 — Neo4j Browser에서 시각화

Neo4j Browser를 열고 실행:

```cypher
MATCH (w:Warehouse:WarehouseInventoryLab)-[:HAS_SNAPSHOT]->(s)-[:HAS_INVENTORY_STATUS]->(st)
RETURN w, s, st LIMIT 50;
```

창고가 주간 스냅샷 및 재고 상태 카테고리에 연결된 것을 볼 수 있어야 합니다.

**Neo4j Browser 사용법:**

1. [http://localhost:7474](http://localhost:7474)(Docker) 또는 Aura **Query** 링크를 엽니다.
2. 위 Cypher를 붙여넣고 **Run**을 클릭합니다.
3. **graph** 뷰(테이블 아님)로 전환하여 노드와 엣지를 봅니다.
4. `Warehouse` 노드를 클릭 — 사이드 패널에서 `latitude`, `longitude`, `id`를 검사합니다.

이 시각 확인은 Part 6–9에서 더 많은 Cypher를 쓰기 전 직관을 쌓습니다.
""",
    52: """---

# Part 6 — 응용: 심각한 저재고 탐지

**비즈니스 질문:** *어떤 창고 지역이 심각하게 재고가 부족했고, 언제인가?*

`Warehouse` → `InventorySnapshot` → `InventoryStatus`로 탐색하며 상태가 `Critical` 또는 `Low`인 경우.

**Part 6에서 사용하는 그래프 패턴:**

```cypher
(w:Warehouse)-[:HAS_SNAPSHOT]->(s:InventorySnapshot)-[:HAS_INVENTORY_STATUS]->(st:InventoryStatus)
```

시설에서 상태 카테고리까지의 **2홉 탐색** — 소매 그래프의
`Store → Order → ProductCategory` 탐색과 동일한 패턴입니다.
""",
    53: """### Step 6.1 — 심각한 재고 스냅샷

**이 셀이 하는 일:** `InventoryStatus.id = 'Critical'`인 창고-주를 나열합니다(주간 평균 후 재고 < 100단위).

**Cypher 설명:**

1. `MATCH`로 창고 → 스냅샷 → 상태 체인.
2. `WHERE st.id = 'Critical'`로 심각한 저재고만 필터.
3. `ORDER BY s.inventory_level ASC`로 가장 심각한 경우를 먼저 표시.
4. `LIMIT 15`로 노트북 출력을 읽기 쉽게 유지.

**운영 조치:** 이 행은 **긴급 보충** 또는 **다른 DC에서 이전** 후보입니다.

**예상 출력:** `WH_30.0_-70.0 | week 2023-05-09 | inventory=42.3` 같은 줄.
""",
    55: """### Step 6.2 — 창고별 저재고 주 수

**이 셀이 하는 일:** 모든 주에 걸쳐 각 창고가 `Critical` 또는 `Low` 상태였던 **빈도**를 집계합니다.

**집계가 중요한 이유:** Step 6.1은 개별 나쁜 주를 보여줍니다; 이 단계는 **만성** 문제 사이트를 순위화합니다.
40주 스트레스 창고는 일회성 출하가 아닌 구조적 수정(안전 재고, 공급업체 변경)이 필요합니다.

**Cypher 개념:** `count(s)`는 `RETURN w.id AS warehouse, count(s)` 후 `w.id`당 매칭 스냅샷을 셉니다.

**예상 출력:** `stressed_weeks` 정수가 가장 높은 상위 창고.
""",
    57: """---

# Part 7 — 응용: 수요가 재고를 초과

**비즈니스 질문:** *역사적 수요가 보유 재고보다 높은 곳은 어디인가?*

`demand_gap = demand - inventory_level` 속성은 ETL 중 계산되었습니다.
양수 값은 수요 신호 대비 **재고 부족(under-stocked)** 조건을 나타냅니다.

**SQL vs 그래프:** SQL에서는 필터와 함께 `warehouse_facts`를 자기 자신과 `JOIN`할 수 있습니다. 여기서는 스냅샷 노드에
이미 `demand_gap`이 속성으로 저장되어 있지만 — 지역 맥락을 위해 창고에서 스냅샷으로 여전히 **탐색**합니다.
""",
    58: """### Step 7.1 — 최대 수요 갭

**이 셀이 하는 일:** `demand_gap > 0`인 스냅샷을 찾아 가장 큰 갭 순으로 정렬합니다.

**열 읽는 법:**

- `inventory` — 주간 평균 보유 재고.
- `demand` — 주간 평균 역사적 수요 신호.
- `demand_gap` — 수요가 재고를 얼마나 초과하는지(CSV와 동일 단위).

**비즈니스 인사이트:** 큰 양의 갭은 상태가 아직 `Critical`이 아니어도 **재고 소진(stockout) 리스크**를 시사합니다
(분류는 고정 임계값 사용; 수요 맥락이 뉘앙스를 더함).

**예상 출력:** `demand_gap` 내림차순 15줄.
""",
    60: """### Step 7.2 — 재고 부족 및 이행 지연

**이 셀이 하는 일:** **숫자 필터**(`demand_gap > 500`)와 **관계 필터**
(`FulfillmentStatus.id = 'Behind'`)를 결합합니다.

**다중 요인을 쓰는 이유:** 재고만으로는 전체 스토리를 말하지 못합니다 — 사이트가 재고 부족**이면서**
이미 주문 이행에 실패(`Behind`)할 수 있습니다. 운영 관리자의 우선순위 대기열입니다.

**Cypher 패턴:** `HAS_FULFILLMENT_STATUS`를 통한 단일 `MATCH` 경로; 스냅샷 속성의 숫자 조건.

**임계값 조정:** 프로덕션 데이터의 제품 단위 규모에 맞게 `500`을 변경하세요.

**예상 출력:** 큰 갭과 `Behind` 이행이 있는 창고-주 쌍.
""",
    62: """---

# Part 8 — 응용: 리스크 및 장비 병목

**비즈니스 질문:** *높은 운영 리스크와 제약된 장비가 겹치는 곳은 어디인가?*

전형적인 **다중 요인** 창고 경보: 재고가 충분해도 장비 가용성이 낮으면 이동이 어렵습니다.

**실제 유사 사례:** 창고에 랙에 팔레트가 있어도 도크 도어와 지게차가 멈추면
실효 재고는 **갇혀 있음** — 그래프 링크가 한 쿼리로 이를 보여줍니다.
""",
    63: """### Step 8.1 — High Risk + Critical 장비

**이 셀이 하는 일:** **High Risk**와 **Critical** 장비 상태에 모두 연결된 스냅샷을 찾습니다.

**동일 스냅샷에 두 `MATCH` 절:**

1. 첫 경로: `HAS_RISK` → `id = 'High Risk'`인 `RiskCategory`.
2. 둘째 경로: `HAS_EQUIPMENT_STATUS` → `id = 'Critical'`인 `EquipmentStatus`.

Neo4j는 둘 다 동일 `s` 노드에 바인딩 — 관계 간 논리 **AND**.

**예상 출력:** `equipment_availability`가 매우 낮은(거의 0) 창고-주 행.
""",
    65: """### Step 8.2 — 반복적인 장비 스트레스 창고

**이 셀이 하는 일:** 창고가 **High Risk**이고 장비가 **Critical 또는 Constrained**인 주 수를 셉니다.

**Step 8.1과의 차이:** Step 8.1은 개별 주를 나열; Step 8.2는 **빈도**로 창고 순위 — 자본 계획(새 하역 장비 투자처)에 유용.

**인라인 노드 필터:** `MATCH`의 `RiskCategory {id: 'High Risk'}`가 일찍 행을 줄임 — 흔한 Cypher 최적화.

**예상 출력:** `alert_weeks` 내림차순 창고.
""",
    67: """---

# Part 9 — 응용: 공급업체 신뢰도 및 보충 리스크

**비즈니스 질문:** *재고가 이미 낮은데 신뢰도 낮은 공급업체에 의존하는 재고 스냅샷은 어디인가?*

그래프 탐색은 동일 스냅샷에서 **재고 상태**와 **공급업체 등급**을 연결합니다 —
프로덕션에서 실제 공급업체 마스터 데이터로 확장할 패턴입니다.

**확장 아이디어:** ERP 벤더 마스터에서 `(Supplier)-[:REPLENISHES]->(Warehouse)` 노드를 추가하세요.
""",
    68: """### Step 9.1 — 저재고 + Low 공급업체 등급

**이 셀이 하는 일:** 동시에 다음인 스냅샷을 찾습니다:

- 저재고 또는 심각 재고(`InventoryStatus`가 `Critical`, `Low`), **그리고**
- **Low** 공급업체 등급(주간 평균 후 `supplier_score` 0.33 미만).

**보충 리스크:** 이 사이트는 취약합니다 — 재고가 이미 낮고 공급 채널이 신뢰할 수 없습니다.

**예상 출력:** `supplier_score` 오름차순(최악 공급업체 먼저) 행.
""",
    70: """### Step 9.2 — 창고 전체 공급업체 등급 분포

**이 셀이 하는 일:** 각 `SupplierTier`에 연결된 스냅샷 수를 셉니다 — 공급업체 노출의 **포트폴리오 뷰**.

**유용한 이유:** 대부분 스냅샷이 `Low` 등급이면 네트워크에 공급업체 개발 또는 이중 소싱이 필요할 수 있습니다.

**Cypher 참고:** 집계는 창고가 아닌 `InventorySnapshot` 노드에서 시작 — 각 사이트의 각 주가 한 번씩 카운트.

**예상 출력:** 스냅샷 수가 있는 세 줄(`High`, `Medium`, `Low`).
""",
    72: """---

# Part 10 — 응용: 자연어 창고 Q&A

**비즈니스 질문:** *계획자가 Cypher 대신 영어로 질문할 수 있는가?*

LangChain **`GraphCypherQAChain`**을 사용합니다: 질문 → LLM이 Cypher 생성 → 실행 → 요약 답변.
더 깊은 GraphRAG 패턴은 `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`도 참고하세요.

> **필요:** `LLM_MODEL_SETUP.md` 및 Step 0d의 작동하는 `llm`.
""",
    73: """### Step 10.1 — LangChain Neo4jGraph 연결

**이 셀이 하는 일:** Neo4j 데이터베이스를 LangChain의 `Neo4jGraph` 헬퍼로 감싸 **노드 레이블, 관계 유형, 속성 키**를 내성합니다.

**스키마 내성을 하는 이유:** `GraphCypherQAChain`은 이 스키마를 LLM에 전달하여 유효한 Cypher를 쓰게 합니다
(테이블 이름이 노드 레이블, 외래 키가 관계 유형).

**주의:** 한 데이터베이스에 **많은** 코스 그래프가 있으면 스키마에 다른 랩 레이블이 포함될 수 있습니다.
**창고**, **재고(inventory)**, **WarehouseInventoryLab** 개념을 언급하는 질문이 가장 좋은 결과를 냅니다.

**예상 출력:** 스키마 텍스트의 처음 ~900자.
""",
    75: """### Step 10.2 — GraphCypherQAChain 데모

**이 셀이 하는 일:** **NL → Cypher → 실행 → NL 답변** 파이프라인을 한 번 실행합니다.

**파이프라인 단계(`verbose=True`일 때):**

1. 영어 질문이 그래프 스키마 맥락과 함께 LLM에 전송됩니다.
2. LLM이 Cypher 쿼리를 제안합니다.
3. Neo4j가 쿼리를 실행합니다.
4. LLM이 결과를 일반 영어로 요약합니다.

**데모 질문:** **심각한 재고(critical inventory)**가 있는 창고를 묻습니다 — Part 6에서 이미 답을 알고 있으므로
LLM 경로가 작동하는지 확인한 뒤 더 어려운 질문을 시도하세요.

**요구 사항:** `ollama serve` 실행, 모델 pull, Step 0d.4의 `llm`.

**예상 출력:** 상세 체인 로그와 창고 id 및 주를 나열하는 자연어 답변.
""",
    77: """### Step 10.3 — 직접 질문해 보기

이 랩 그래프에서 잘 작동하는 예:

- *How many inventory snapshots have High Risk?*
- *Which warehouses have the most Low supplier tier snapshots?*
- *List weeks where fulfillment status is Behind and inventory status is Critical.*

**더 나은 LLM 답변 팁:**

- 노드 유형 언급: *inventory snapshots*, *warehouses*, *supplier tier*.
- 개수 또는 top-N 목록 요청 — 열린 요약보다 쉬움.
- Cypher가 실패하면 Part 3 레이블(`InventoryStatus`, `EquipmentStatus`)을 명시해 다시 표현하세요.
""",
    78: """### Step 10.3 — 직접 질문 실행

**이 셀이 하는 일:** `MY_QUESTION`으로 동일한 `chain`을 호출합니다 — **문자열을 편집**하여 실험하세요.

**기본 질문:** **제약된 장비(constrained equipment)** 스냅샷이 가장 많은 창고를 찾습니다 —
장비 상태 탐색과 집계를 결합(Part 8과 비교).

**`llm is None`인 경우:** `.env`에서 `LLM_BACKEND`를 설정하고 Step 0b.3, 0d.2–0d.4를 다시 실행하세요.
""",
    80: """---

# Part 11 — 고급 개선 사항(자습 읽기)

이 코스의 **기본 방법**은: **구조화 ETL → 명시적 그래프 모델 → Cypher 분석**입니다.
CSV, WMS 또는 ERP보내기에 창고 데이터가 이미 있을 때 올바른 시작점입니다.

아래는 **스스로 연구할 개선 경로**입니다. 이 랩을 마치기 위해 구현할 필요는 없습니다.

## 11.1 더 풍부한 도메인 모델링

| 개선 | 이유 | 시작 자료 |
|-------------|-----|-------------------|
| 실제 **시설 마스터 데이터**(창고 ID, 존, SKU) | GPS 빈닝을 권위 있는 위치로 대체 | WMS/ERP 스키마 |
| **SKU 수준** 재고 노드 | 지역 재고가 아닌 품목 세분화 추적 | Neo4j 공급망 모델링 가이드 |
| **로트/배치** 추적 | 유통기한, 리콜, FEFO 피킹 | GS1 표준, 콜드체인 KG 논문 |

## 11.2 LLM 기반 그래프 구축

| 개선 | 이유 | Module 8 노트북 |
|-------------|-----|-----------------|
| **비구조화 보고서**(사고 로그, 이메일)에서 엔티티 추출 | CSV가 놓치는 것 포착 | `Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb` |
| **스키마 가이드** LLM 추출 | 더 높은 정밀도 노드 유형 | 동일 노트북, Section 2.3 |

## 11.3 GraphRAG 및 에이전트

| 개선 | 이유 | Module 8 노트북 |
|-------------|-----|-----------------|
| **GraphRAG**(벡터 + 그래프 검색) | 문서 근거로 질문에 답변 | `Module_8_Using_Knowledge_Graph_with_LangChain.ipynb` |
| RAGAS로 **평가** | 답변의 충실도 측정 | `Module_8_Evaluating_GraphRAG_with_RAGAS.ipynb` |
| **에이전트** 워크플로 | 다단계 계획(재주문, 경로 변경) | LangChain / LlamaIndex 노트북 |

## 11.4 분석 및 운영

| 개선 | 이유 | 시작 자료 |
|-------------|-----|-------------------|
| **Neo4j Graph Data Science**(PageRank, Louvain) | 병목 창고 및 커뮤니티 찾기 | [Neo4j GDS docs](https://neo4j.com/docs/graph-data-science/) |
| **스트리밍 수집**(Kafka → Neo4j) | 거의 실시간 재고 이벤트 | Neo4j 스트리밍 통합 |
| IoT 센서 연결 **디지털 트윈** | 실시간 `iot_temperature`, 장비 원격 측정 | IIoT + 지식 그래프 문헌 |

## 11.5 데이터 품질 및 거버넌스

- **엔티티 해소(entity resolution)**: 시스템 간 중복 창고 코드 병합(`Module_8_Practical_Knowledge_Graph_Applications.ipynb` Part 5 참고).
- **계보(lineage)**: 감사 가능성을 위해 `source_file`, `loaded_at`로 스냅샷 태그.
- **역할 기반 접근**: 계획자 vs 분석가 vs 경영진 뷰용 Neo4j RBAC.
""",
    81: """---

# Part 12 — 마무리

## 연습한 내용

| 파트 | 기술 | 비즈니스 결과 |
|------|-------|------------------|
| 2–4 | pandas ETL + 분류 | CSV를 그래프 레코드로 변환 |
| 5 | 배치 Cypher 로드 | 격리된 창고 서브그래프 시드 |
| 6 | 상태 탐색 | 저재고 창고 찾기 |
| 7 | 숫자 + 상태 필터 | 수요-재고 불일치 탐지 |
| 8 | 다중 요인 패턴 | 리스크 + 장비 경보 |
| 9 | 공급업체 연결 | 보충 리스크 뷰 |
| 10 | LLM + Cypher | 자연어 재고 Q&A |

## 조직에 매핑

`Warehouse` / `InventorySnapshot`을 자신의 엔티티로 대체:

| 시스템 | 그래프 노드 | 관계 예 |
|-------------|------------|----------------------|
| WMS | `Warehouse`, `Zone`, `SKU` | `(Warehouse)-[:STORES]->(SKU)` |
| TMS | `Shipment`, `Carrier` | `(Shipment)-[:ORIGIN]->(Warehouse)` |
| ERP | `PurchaseOrder`, `Supplier` | `(Supplier)-[:REPLENISHES]->(Warehouse)` |

## 정리(선택)

```cypher
MATCH (n:WarehouseInventoryLab) DETACH DELETE n;
```

## 학습 계속하기

1. **`Module_8_Practical_Knowledge_Graph_Applications.ipynb`** — 더 많은 응용 패턴.
2. **`Module_8_Building_Knowledge_Graphs_with_LLMs.ipynb`** — 문서에서 그래프.
3. **`Module_8_Using_Knowledge_Graph_with_LangChain.ipynb`** — GraphRAG 및 에이전트.

---

*코스 종료 — 지식 그래프로 창고 및 재고 관리 실무 향상*
""",
}

PRINT_REPLACEMENTS: dict[int, list[tuple[str, str]]] = {
    6: [
        ("print('Module directory:', MODULE_DIR)", "print('모듈 디렉터리:', MODULE_DIR)"),
    ],
    8: [
        ("print('Dataset:', DATA_PATH)", "print('데이터셋:', DATA_PATH)"),
        ("print('Dataset exists:', DATA_PATH.exists())", "print('데이터셋 존재:', DATA_PATH.exists())"),
        ("print('Lab label:', LAB_LABEL)", "print('랩 레이블:', LAB_LABEL)"),
        ("print('Top warehouses to model:', LAB_TOP_WAREHOUSES)", "print('모델링할 상위 창고 수:', LAB_TOP_WAREHOUSES)"),
        ("print('Neo4j URI:', NEO4J_URI)", "print('Neo4j URI:', NEO4J_URI)"),
    ],
    10: [
        ("print('LLM backend:', LLM_BACKEND)", "print('LLM 백엔드:', LLM_BACKEND)"),
    ],
    12: [
        ("print(record['message'])", "print(record['message'])"),
        ("print('Connectivity check passed.')", "print('연결 확인 통과.')"),
    ],
    14: [
        ("print('run_cypher() ready.')", "print('run_cypher() 준비 완료.')"),
    ],
    16: [
        ("print('OLLAMA_RUNNER:', OLLAMA_RUNNER)", "print('OLLAMA_RUNNER:', OLLAMA_RUNNER)"),
    ],
    18: [
        ("print('Ollama helpers defined.')", "print('Ollama 헬퍼 정의 완료.')"),
    ],
    20: [
        (
            "print(f'LLM ready: OpenAI {OPENAI_MODEL}')",
            "print(f'LLM 준비 완료: OpenAI {OPENAI_MODEL}')",
        ),
        (
            "print(f'LLM ready: Ollama {OLLAMA_MODEL} via runner')",
            "print(f'LLM 준비 완료: Ollama {OLLAMA_MODEL} (runner 경유)')",
        ),
        (
            "print('LLM not configured — Part 10 will be skipped unless you set LLM_BACKEND.')",
            "print('LLM 미구성 — LLM_BACKEND를 설정하지 않으면 Part 10을 건너뜁니다.')",
        ),
    ],
    24: [
        ("print('Rows:', len(raw_df))", "print('행 수:', len(raw_df))"),
        ("print('Columns:', len(raw_df.columns))", "print('열 수:', len(raw_df.columns))"),
    ],
    28: [
        ("print(risk_counts.to_string())", "print(risk_counts.to_string())"),
    ],
    30: [
        (
            "print('Distinct warehouse regions (all data):', raw_df['warehouse_id'].nunique())",
            "print('고유 창고 지역 수(전체 데이터):', raw_df['warehouse_id'].nunique())",
        ),
        ("print('Top 5 busiest regions:')", "print('가장 바쁜 상위 5개 지역:')"),
        ("print(raw_df['warehouse_id'].value_counts().head())", "print(raw_df['warehouse_id'].value_counts().head())"),
    ],
    34: [
        ("print('Classification helpers ready.')", "print('분류 헬퍼 준비 완료.')"),
    ],
    36: [
        ("print('Warehouses modeled:', weekly_df['warehouse_id'].nunique())", "print('모델링된 창고 수:', weekly_df['warehouse_id'].nunique())"),
        ("print('Weekly snapshots:', len(weekly_df))", "print('주간 스냅샷 수:', len(weekly_df))"),
    ],
    38: [
        ("print('Snapshot records:', len(snapshot_records))", "print('스냅샷 레코드 수:', len(snapshot_records))"),
        ("print('Warehouse nodes:', len(warehouse_records))", "print('창고 노드 수:', len(warehouse_records))"),
    ],
    41: [
        (
            "print('Cleared prior WarehouseInventoryLab data.')",
            "print('이전 WarehouseInventoryLab 데이터 삭제 완료.')",
        ),
    ],
    43: [
        ("print('Reference categories created.')", "print('참조 카테고리 생성 완료.')"),
    ],
    45: [
        (
            "print(f'Loaded {len(warehouse_records)} warehouse nodes.')",
            "print(f'{len(warehouse_records)}개 창고 노드 로드 완료.')",
        ),
    ],
    47: [
        (
            "print(f'Loaded {len(snapshot_records)} inventory snapshots.')",
            "print(f'{len(snapshot_records)}개 재고 스냅샷 로드 완료.')",
        ),
    ],
    50: [
        (
            'print(f"{row[\'node_type\']}: {row[\'cnt\']}")',
            'print(f"{row[\'node_type\']}: {row[\'cnt\']}")',
        ),
    ],
    54: [
        (
            'print(f"{r[\'warehouse\']} | week {r[\'week\']} | inventory={r[\'inventory_level\']}")',
            'print(f"{r[\'warehouse\']} | 주 {r[\'week\']} | 재고={r[\'inventory_level\']}")',
        ),
    ],
    56: [
        (
            'print(f"{r[\'warehouse\']}: {r[\'stressed_weeks\']} stressed week(s)")',
            'print(f"{r[\'warehouse\']}: 스트레스 주 {r[\'stressed_weeks\']}주")',
        ),
    ],
    59: [
        (
            '        f"{r[\'warehouse\']} | {r[\'week\']} | inv={r[\'inventory\']} demand={r[\'demand\']} gap={r[\'demand_gap\']}"',
            '        f"{r[\'warehouse\']} | {r[\'week\']} | 재고={r[\'inventory\']} 수요={r[\'demand\']} 갭={r[\'demand_gap\']}"',
        ),
    ],
    61: [
        (
            'print(f"{r[\'warehouse\']} | {r[\'week\']} | gap={r[\'gap\']} | {r[\'fulfillment\']}")',
            'print(f"{r[\'warehouse\']} | {r[\'week\']} | 갭={r[\'gap\']} | {r[\'fulfillment\']}")',
        ),
    ],
    64: [
        (
            'print(f"{r[\'warehouse\']} | {r[\'week\']} | equipment={r[\'equipment_availability\']}")',
            'print(f"{r[\'warehouse\']} | {r[\'week\']} | 장비={r[\'equipment_availability\']}")',
        ),
    ],
    66: [
        (
            'print(f"{r[\'warehouse\']}: {r[\'alert_weeks\']} alert week(s)")',
            'print(f"{r[\'warehouse\']}: 경보 주 {r[\'alert_weeks\']}주")',
        ),
    ],
    69: [
        (
            '        f"{r[\'warehouse\']} | {r[\'week\']} | {r[\'inventory_status\']} | supplier={r[\'supplier_score\']}"',
            '        f"{r[\'warehouse\']} | {r[\'week\']} | {r[\'inventory_status\']} | 공급업체={r[\'supplier_score\']}"',
        ),
    ],
    71: [
        (
            'print(f"{r[\'supplier_tier\']}: {r[\'snapshots\']} snapshot(s)")',
            'print(f"{r[\'supplier_tier\']}: 스냅샷 {r[\'snapshots\']}개")',
        ),
    ],
    74: [
        (
            "print('Schema snippet (first 900 chars):')",
            "print('스키마 일부 (처음 900자):')",
        ),
        ("print((neo4j_graph.schema or '')[:900])", "print((neo4j_graph.schema or '')[:900])"),
    ],
    76: [
        (
            "print('Skip: configure LLM_BACKEND in .env (see LLM_MODEL_SETUP.md).')",
            "print('건너뜀: .env에서 LLM_BACKEND를 구성하세요 (LLM_MODEL_SETUP.md 참고).')",
        ),
        ("print('\\nQuestion:', question)", "print('\\n질문:', question)"),
        ("print('Answer:', answer.get('result', answer))", "print('답변:', answer.get('result', answer))"),
    ],
    79: [
        ("print('Q:', MY_QUESTION)", "print('질문:', MY_QUESTION)"),
        ("print('A:', result.get('result', result))", "print('답변:', result.get('result', result))"),
        ("print('Configure LLM to run this cell.')", "print('이 셀을 실행하려면 LLM을 구성하세요.')"),
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

    markdown_indices = {i for i, c in enumerate(nb["cells"]) if c["cell_type"] == "markdown"}
    missing_md = markdown_indices - set(MARKDOWN_KO.keys())
    if missing_md:
        raise ValueError(f"Missing Korean markdown for cells: {sorted(missing_md)}")

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
