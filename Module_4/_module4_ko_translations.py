"""Korean translations for Module 4 Building a comprehensive RAG system notebook."""

MARKDOWN_KO = {
    0: """# 종합 RAG(Retrieval-Augmented Generation, 검색 증강 생성) 시스템 구축

이 노트북은 단일 규제 PDF에서 **RAG(검색 증강 생성)**를 구축하는 **단계별 실습**입니다. 원시 페이지에서 embedding(임베딩), 벡터 검색, 근거 기반 프롬프트, 환각(hallucination) 위험에 대한 정성적 점검까지 진행합니다.

## 문서 및 실행 환경

- **Corpus(코퍼스)**: `data/IGF Code (124Pages).pdf`
- **주 LLM 경로(Section A)**: **`llama-cpp-python`**과 **GGUF** 모델을 이용한 로컬 추론
- **선택 서비스 LLM(Section B)**: `ollama_model_runner.py`로 **Ollama** 호출(RAG 로직은 노트북에 유지)
- **프레임워크 트랙(선택)**: **LangChain**(Section C)과 **LlamaIndex**(Section D)가 동일한 `manual_chunks`를 재사용해 공정 비교

## 구축할 내용

1. **Ingestion(수집)**: PDF에서 페이지별 텍스트 추출
2. **Chunking(청킹)**: 청킹 전략 비교 및 파이프라인 기본값 선택
3. **Embeddings(임베딩)**: Sentence Transformers로 chunk 인코딩; 벡터 sanity check
4. **Indexing(인덱싱)**: FAISS(핵심) 및 Chroma(선택 영속화)
5. **Retrieval(검색)**: top-k 검색, context 포맷팅, 간단한 실험
6. **Generation(생성)**: 근거 기반 프롬프트 및 로컬 completion
7. **Trust and quality(신뢰·품질)**: 인용, 경량 검증, 소규모 다중 질문 점검
8. **Extensions(확장)**: Ollama 클라이언트 워크플로; LangChain·LlamaIndex 검색 패턴

## 노트북 사용 방법

- 강사 지시가 없으면 **Step 0**부터 end-to-end RAG 셀까지 **Section A**를 순서대로 실행하세요.
- **Section B**는 선택이며 Ollama가 별도로 설치·실행 중이어야 합니다.
- **Section C·D**는 선택 추가; Section A에서 chunking을 완료해 `manual_chunks`가 있어야 합니다.
- 설치로 환경이 바뀌면 **커널을 한 번 재시작**한 뒤 Step 0부터 다시 실행하세요.

## 사전 지식(개념)

Jupyter에서 Python 사용, 벡터·코사인 유사도 기본 개념, 첫 모델 다운로드에 대한 인내.

> **팁:** 모델 답변을 읽을 때 검색된 context를 함께 보세요 — 대부분의 “RAG 버그”는 LLM만의 문제가 아니라 retrieval 또는 chunking 문제입니다.
""",
    1: """## Section A — Ollama 없이 노트북 기반 RAG

이 섹션은 `llama-cpp-python`으로 로컬 생성을 수행하며, 노트북 셀에서 전체 RAG 워크플로를 직접 실행합니다.
""",
    2: """## Step 0 — Colab용 `llama-cpp-python` + GGUF 설정

이 노트북은 [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python)과 **`.gguf`** 모델 파일로 **프로세스 내 로컬 추론**을 사용합니다.

### 이 단계에서 하는 일

1. 현재 노트북 커널에 필요 패키지 설치/확인
2. Hugging Face에서 기본 GGUF 모델 다운로드(선택)
3. 이후 셀이 모델을 로드할 수 있도록 `LLAMA_CPP_GGUF` 설정

### 필요 패키지

- `llama-cpp-python`
- `huggingface_hub`
- `pypdf`
- `sentence-transformers`
- `faiss-cpu`
- `chromadb` (선택)

### Colab 참고

- 첫 모델 다운로드는 용량이 크고 시간이 걸릴 수 있습니다.
- gated 모델이면 먼저 `HF_TOKEN`을 설정하세요.
- GGUF 파일 경로가 이미 있으면 `LLAMA_CPP_GGUF`를 설정하고 다운로드 셀을 건너뛰세요.
- 설치 후에도 import 오류가 남으면 runtime을 재시작하고 Step 0a부터 다시 실행하세요.

### conda / 로컬 Linux 참고

- `llama-cpp-python`이 컴파일을 시도하고 CMake가 잘못된 `CC`(흔히 `gcc -pthread -B .../compiler_compat`)를 보고하면, Step 0a가 해당 설치에 대해 `CC`/`CXX`를 비우고 maintainer index의 wheel을 우선해 로컬 컴파일러가 보통 필요 없습니다.
""",
    9: """## Step 1 — PDF(`IGF Code`)에서 소스 데이터 로드

이 단계에서는 원시 PDF를 나중에 chunking·인덱싱할 수 있는 구조화 in-memory 데이터셋으로 변환합니다.

주 소스 파일:
- `data/IGF Code (124Pages).pdf`

### 이 단계가 중요한 이유
- RAG 품질은 ingestion 품질에서 시작합니다.
- 추출이 noisy하거나 섹션이 빠지면 하류 retrieval·생성이 저하됩니다.

### 코드가 하는 일
1. 각 PDF 페이지를 로드합니다.
2. 텍스트를 추출하고 공백을 정규화합니다.
3. 매우 짧거나 빈 페이지는 버립니다.
4. `page`, `title`, `text`가 있는 레코드를 만듭니다.

### 기대 출력
- 로드된 페이지 수.
- 추출 품질 확인용 한 페이지 미리보기.

미리보기가 깨져 보이면(깨진 텍스트, 많은 누락 줄) 계속하기 전에 추출을 먼저 수정하세요.
""",
    11: """### Step 1 — PDF 페이지를 레코드로 읽고 PDF 추출 실행

chunking 전에 페이지 텍스트를 추출해 구조화 레코드(`page`, `title`, `text`)로 저장합니다.
이 워크샵은 **이 PDF 파생 레코드만** retrieval corpus로 사용합니다.

다음 셀을 실행해 IGF PDF의 모든 페이지를 파싱하고 `manual_docs`를 만드세요.
이후 chunking 전략을 시작합니다.
""",
    13: """## Step 2 — 확장 chunking 전략(여러 방법 비교)

Chunking은 retrieval 품질에 큰 영향을 줍니다. 이 단계에서는 IGF PDF 텍스트에 여러 방법을 비교합니다:

1. **Sentence-window semantic chunking**(기본): 문장 기반 윈도우 + overlap.
2. **Fixed-size word chunking**: 결정적이고 단순한 baseline.
3. **Heading-aware chunking**: 감지된 섹션형 제목으로 분할 후 윈도우.

왜 비교하나?
- 작은 chunk는 정밀도는 높지만 context를 잃을 수 있습니다.
- 큰 chunk는 context는 유지하지만 retrieval 특이성이 떨어질 수 있습니다.
- Heading-aware chunk는 법규/규제 문서 retrieval에 종종 유리합니다.

이 단계 끝에 하류 embedding/인덱싱용 기본 방법을 하나 고릅니다.
""",
    14: """### Step 2.1 — Chunking 함수 정의

아래 코드 셀은 Step 2.2 이후에 쓸 **텍스트 분할(chunking) 로직**을 재사용 가능한 Python 함수로 모읍니다. 목표는 **추출된 PDF 페이지 하나**를 embedding·벡터 검색·RAG 프롬프트에 적합한 **여러 더 작은 구간**으로 바꾸는 것입니다.

#### 전체 처리 흐름(코드 전에 읽기)

1. **Input**: 각 페이지의 `text` 문자열(이전 단계에서 공백 정규화 완료).
2. **문장·단어·제목 기준 분할**: 방법에 따라 문장 경계, 고정 단어 수, 목차형 줄로 분할.
3. **Chunk 조립**: 각 chunk는 전체 페이지보다 짧지만 사용자 질문에 충분한 context를 담은 텍스트 구간.
4. **출력 정규화**: `build_manual_chunks`가 각 chunk를 통일 **dictionary**(`chunk_id`, 페이지 번호, method 등)로 감싸 이후 단계가 chunking 세부를 몰라도 됩니다.

---

#### `sentence_split(text)`

- **목적**: 긴 구절을 **문장 목록**(문자열)으로 분할.
- **동작**: `re.sub(r'\\s+', ' ', ...)`로 모든 공백(줄바꿈, 탭, 다중 공백)을 한 칸으로; `re.split(r'(?<=[.!?])\\s+', ...)`로 **`.` `!` `?` 뒤 공백**에서 분할 — 무거운 NLP 없이 가벼운 문장 경계.
- **한계**: `Fig. 2.3`이나 `Dr.`이 있는 기술 문서는 사람 판단과 다른 경계가 될 수 있음 — 읽기 쉬운 강의용 코드의 trade-off.

---

#### `chunk_sentence_window(text, max_words, overlap_sentences)`

- **목적**: **연속 문장**을 묶어 총 **단어** 수(`len(sentence.split())`)가 `max_words`를 넘지 않게 chunk 생성; 가득 차면 **chunk를 닫고** 새 chunk 시작.
- **Overlap**: `overlap_sentences`는 현재 chunk **끝 문장** 중 다음 chunk **시작**에 **복사**할 개수. chunk 경계 context가 embedding이나 쿼리가 문장 경계에 맞을 때 완전히 사라지지 않게 합니다.
- **루프**: `current`에 누적 문장; `current_len`은 단어 수; 새 문장 추가 시 `max_words` 초과하면 이전 chunk를 `append`하고 `current`를 overlap 꼬리 + 새 문장으로 리셋.

---

#### `chunk_fixed_words(text, chunk_words, overlap_words)`

- **목적**: **고정 단어 수** 분할 — 항상 재현 가능한(결정적) 단순 baseline.
- **`step`**: `chunk_words - overlap_words`(최소 1)가 슬라이딩 stride: 각 윈도우는 `chunk_words` 단어, `step`만큼 전진해 다음 chunk가 이전과 `overlap_words`만큼 **겹침**(overlap < chunk_words일 때).
- **장단점**: 이해·파라미터 비교가 매우 쉬움; **문장·법조 중간**에서 잘릴 수 있어 retrieval 품질이 문장/제목 기반보다 나쁠 수 있음.

---

#### `chunk_heading_aware(text, max_words)`

- **목적**: 규제 텍스트에서 **문서 구조**를 존중: 줄/문장 분할, **섹션 제목**처럼 보이는 줄(Chapter, Section, Part, `1.2.3` 형) 감지, 각 "section" 블록에 `chunk_fixed_words`(`chunk_words=max_words`) 적용해 섹션이 너무 길지 않게.
- **`heading_pattern`**: 섹션 헤더처럼 보이는 줄을 표시하는 regex; 새 섹션에서 `current`에 내용이 있으면 전체를 하나의 **section**으로 push하고 해당 제목 줄부터 새 section 시작.
- **참고**: 휴리스틱(근사 규칙)이며 진짜 PDF 구조 분석은 아님; "structure-aware chunking" 아이디어를 보여 주기에 유용.

---

#### `build_manual_chunks(docs, method, params)`

- **목적**: 세 전략(`sentence_window`, `fixed_words`, `heading_aware`) 중 하나를 전체 `docs` 페이지 목록에 적용하는 **단일 진입점**, 통일 dict 목록 반환.
- **각 dict의 주요 필드**:
  - `chunk_id`: `product_id`, 페이지 번호, method 약칭, chunk 인덱스로 만든 거의 고유 ID.
  - `page`, `title`: 강사·학습자가 인용을 검증할 때 출처 추적.
  - `chunk_method`: 사용한 method 기록 — 실험 비교에 유용.
  - `text`: embedding / retrieval에 전달되는 내용.

---

#### 스키마(메타데이터)가 왜 중요한가?

RAG에서 retrieval 후 학습자는 **어느 페이지·어떤 chunking method**인지 알아야 합니다. `chunk_id`, `page`, `chunk_method`, `text`를 유지하면 **추적성**, **인용**, **디버깅**(예: `sentence_overlap`을 바꾸고 동일 논리 `chunk_id` 비교)을 하류 파이프라인 재작성 없이 할 수 있습니다.
""",
    16: """### Step 2.2 — 실험 파라미터 설정(대화형 튜닝)

이 파라미터 셀은 chunking 실험용 **제어판**입니다.

### 파라미터 의미
- `sentence_max_words`: sentence-window chunk 최대 크기.
- `sentence_overlap`: 다음 chunk로 이어지는 끝 문장 개수.
- `fixed_chunk_words`: fixed-word chunk 목표 크기.
- `fixed_overlap_words`: fixed-word chunk overlap 크기.
- `heading_max_words`: heading 기반 분할 후 최대 크기.

### 실험 방법
1. 한 번에 파라미터 하나만 변경.
2. Step 2.3 → Step 2.7 재실행.
3. chunk 수·미리보기 변화 관찰.
4. 가독성 + retrieval 정렬 개선에 대한 메모 유지.
""",
    18: """### Step 2.3 — Method A: Sentence-window chunking(시각 예시)

이 방법은 문장 경계를 존중하고 문장 overlap을 추가합니다.
규제 텍스트에 종종 좋은 기본값입니다.
""",
    20: """### Step 2.4 — Method B: Fixed-size word chunking(시각 예시)

단순하고 결정적인 방법입니다.
`fixed_chunk_words`와 `fixed_overlap_words`를 바꿔 경계 동작을 관찰해 보세요.
""",
    23: """### Step 2.5 — Method C: Heading-aware chunking(시각 예시)

제목형 패턴을 감지해 문서 구조를 존중하려고 시도합니다.

### 도움이 되는 이유
- 규제/표준 문서는 장/절 논리가 많습니다.
- 섹션 단위 텍스트를 함께 두면 retrieval 일관성이 좋아질 수 있습니다.

### 점검할 것
- Chunk가 섹션 전환과 맞는가?
- 중요 context가 과하게 쪼개지지 않았는가?
- Method A/B와 chunk 수 비교.
""",
    26: """### Step 2.6 — 모든 방법 비교(표 + 간단 막대)

다음 코드 셀은 현재 `chunk_params`로 **전체 로드 corpus**에서 방법을 비교합니다.

### 출력 내용
- 방법별 `n_chunks`, `min_words`, `avg_words`, `median_words`, `max_words` **표**.
- 동일 표의 **plain text** 출력(실습 노트 복사용).
- `n_chunks`용 간단 **ASCII 막대**로 차이를 시각적으로 확인.

Step 2.3–2.5 미리보기와 함께 보세요: **chunk 수가 비슷해도 경계는 다를 수 있습니다**.
""",
    28: """### Step 2.7 — 하류 파이프라인용 기본 chunk method 선택

이 셀은 Step 3 이후 사용할 chunk 집합을 정합니다.

### 권장 워크플로
1. Method A/B/C 미리보기 검토.
2. Step 2.6 지표 검토.
3. `DEFAULT_CHUNK_METHOD` 설정.
4. 이 셀 재실행 후 embedding으로 진행.

Step 2는 언제든 돌아와 선택을 바꿀 수 있습니다.
""",
    30: """## Step 3 — 선택 chunk를 embedding으로 변환(심화)

텍스트 전처리에서 벡터화로 넘어갑니다.

### 학습 목표
1. Chunk 텍스트가 숫자 벡터가 되는 과정 이해.
2. 인코딩 설정이 속도·품질에 미치는 영향 확인.
3. 인덱싱 전 embedding 검증.

### 이 단계 범위
- 선택 chunk method 기준 기본 embedding 실행.
- 선택 성능 튜닝(`batch_size`).
- Sanity 진단(shape, norm, NaN).
- 쿼리–chunk 유사도로 의미 미리보기.

### 이 단계가 중요한 이유
Embedding 품질이 나쁘면 프롬프트 엔지니어링이 강해도 retrieval은 나쁩니다.
FAISS/Chroma 인덱싱 전 **품질 게이트**로 취급하세요.
""",
    32: """### Step 3.1 — Embedding 설정 및 성능 튜닝

Embedding 단계는 품질과 런타임 비용 모두에 직접 영향을 줍니다.

### 실무 고려
- **모델 선택**: 큰 모델은 의미 품질은 좋을 수 있으나 지연·메모리 증가.
- **Batch size**: GPU에서 큰 batch는 빠르지만 OOM 가능.
- **Normalization**: `normalize_embeddings=True`이면 inner product로 cosine similarity 계산 가능.

### 다음에 할 일
명시적 batch 설정으로 인코딩을 다시 실행해 학습자가 런타임과 출력 shape를 관찰합니다.
""",
    34: """## Step 4 — FAISS로 벡터 검색 설정

RAG 파이프라인의 주 retrieval 엔진을 구축합니다.

### 코드가 하는 일
1. Embedding 벡터로 in-memory FAISS index 구축.
2. FAISS vector id를 chunk 메타데이터에 매핑.
3. top-k 의미 검색용 `search_faiss(...)` 정의.
4. 샘플 쿼리로 retrieval 품질 확인.

### 중요 포인트
- 정규화 embedding에 `IndexFlatIP` 사용(cosine 유사 동작).
- 여기 retrieval 품질이 Step 7/9 최종 답 품질에 큰 영향.
- 상위 결과를 지금 점검; 무관해 보이면 chunking 수정.
""",
    36: """### 선택 미리보기 — Chroma 설정 및 collection 수명주기

Step 5 준비용 미리보기입니다.
설정과 쿼리를 분리하고 collection 수명주기를 명확히 합니다.

핵심 아이디어:
- collection을 안전하게 create(또는 reuse)
- FAISS 파이프라인과 메타데이터 스키마 일관 유지
- insert 전 embedding 벡터 shape 유효성 확인
""",
    38: """### 선택 미리보기 — Chroma insert 및 query

이 미리보기 셀은 벡터를 insert하고 테스트 쿼리 하나를 실행합니다.

팁: 여러 번 재실행하면 ID가 이미 있을 수 있음; production에서는 upsert/update 전략 사용.
""",
    40: """### Step 4.1 — FAISS index 구축

In-memory FAISS index를 초기화하고 모든 chunk 벡터를 로드합니다.

핵심:
- 정규화 embedding에 `IndexFlatIP` — cosine similarity 순위와 유사.

출력 확인:
- `index.ntotal`은 chunk 수와 같아야 함.
- metadata map 크기는 index 크기와 일치해야 함.
""",
    42: """### 선택 미리보기 — 페이지 범위 필터 retrieval

헬퍼 `retrieve_context_filtered(...)`는 `search_faiss`로 over-fetch한 뒤 `page`가 `[min_page, max_page]` 안인 hit만 유지합니다. index search API가 있는 **Step 4.2 코드 셀**(`search_faiss` 바로 뒤)에 **정의**되어 index보다 먼저 실행되지 않습니다.

Step 6 등에서 유용합니다. 긴 PDF에서는 페이지 범위 필터로 노이즈를 줄일 수 있습니다.

예시:
- 운영 장(chapter)만 집중
- 부록·참고 페이지 제외
""",
    44: """### Step 4.2 — Retrieval 헬퍼 함수 정의

`search_faiss(...)`는 의미 검색용 재사용 API입니다. 같은 셀에 `retrieve_context_filtered(...)`(페이지 범위 필터)도 정의하고 작은 demo를 실행 — Step 4.1 FAISS index **이후**에 두어야 합니다.

함수로 감싸는 이유?
- Step 6·9가 동일 retrieval 로직 호출.
- 한 곳에서 검색 동작 조정.
- 노트북 흐름이 깔끔하고 유지보수 쉬움.
""",
    46: """### Step 4.3 — Retrieval 실험(쿼리·`top_k` 민감도)

쿼리 문구와 `top_k`를 바꿀 때 동작 변화를 이해하는 실험 셀입니다.

확인할 것:
- 상위 chunk가 관련 페이지에서 오는지.
- 1위 이후 score가 얼마나 빨리 떨어지는지.
- `top_k` 증가가 유용한 context를 더 주는지, 주로 노이즈인지.
""",
    48: """## Step 5 — 선택 벡터 DB: Chroma

로컬 demo에는 FAISS만으로 충분한 경우가 많습니다. Chroma는 collection 영속화와 메타데이터 중심 워크플로에 유용합니다.

### 이 단계에서
1. Chroma collection create/get.
2. document, metadata, embedding insert.
3. retrieval 확인용 쿼리 하나 실행.

Chroma를 쓸 수 없으면 이 단계를 건너뛰고 계속하세요.
""",
    50: """## Step 6 — PDF chunk 위 retrieval 파이프라인 구축

원시 벡터 검색 출력을 프롬프트용 재사용 retrieval 인터페이스로 바꿉니다.

### 핵심 함수
1. `retrieve_context(...)`: top-k chunk 후보 반환.
2. `format_context(...)`: 검색 chunk를 프롬프트용 context 블록으로 포맷.

### 포맷팅이 중요한 이유
- 구조화 context는 LLM 지시를 더 일관되게 함.
- 명시적 doc 번호(`[Doc 1]`, `[Doc 2]`)로 Step 7 인용 인식 프롬프트 가능.
- `page` metadata 포함으로 답을 출처 위치에 연결.
""",
    52: """## Step 7 — 검색 context로 로컬 LLM(`llama-cpp-python`) 프롬프트

Retrieval 출력을 근거 기반 생성으로 변환합니다.

### 프롬프트 설계 목표
- 답이 검색 evidence 안에 머물도록 강제.
- 추적성을 위해 인용(`[Doc i]`) 요구.
- context 부족 시 불확실성 반환.

### 코드 초점
- `build_grounded_prompt(...)`: 엄격한 답변 정책.
- `build_llama_cpp(...)`: 런타임 설정으로 로컬 GGUF 초기화.
- `call_local_llm(...)`: completion 실행 및 raw 응답 반환.

모델이 로드되지 않았으면 진행 전 `LLAMA_CPP_GGUF`를 수정하세요.
""",
    54: """### Step 7a — 프롬프트 구성 및 로컬 모델 실행

로컬 GGUF 모델을 실행합니다. 이전 기본값보다 **높은 `max_tokens`**로 답을 읽고 비교하기 충분히 길게 출력합니다.

**출력:** 프롬프트 발췌, **stats**, **전체** 답이 담긴 스크롤 가능 HTML 패널(앞 몇 줄만이 아님), 로그용 plain-text head/tail echo.
""",
    56: """### 선택 유틸 — 프롬프트 temperature 실험

Step 7a **다음** 코드 셀을 실행하세요(위 선택 인용 셀을 실행했다면 그 이후). `prompt`와 `call_local_llm`이 이미 있어야 합니다.

**출력:** `temperature`별 요약 표(길이 + 4000자 preview), **`max_tokens = 640`**으로 모델 호출.

**저장:** 실행 후 `experiment_answers`가 `data/step7_temperature_experiment.json`(전체 레코드, `answer_full` 포함)과 `data/step7_temperature_experiment.csv`(preview 열)에 기록됩니다.

다른 temperature로 답을 생성해 안정성 vs 창의성을 관찰하세요.
RAG 지원 use case에서는 일관성을 위해 낮은 temperature가 보통 선호됩니다.
""",
    58: """## Step 8 — 응답에서 환각(hallucination) 처리

RAG를 써도 프롬프트가 약하거나 retrieval이 핵심 evidence를 놓치면 환각이 남을 수 있습니다.

### 흔한 실패 패턴
- 검색 chunk에 없는 주장.
- 부분 evidence로 과신하는 답.
- 지시에도 불구하고 인용 누락.

### 여기서 쓰는 완화 흐름
1. 제약 프롬프트 정책(Step 7).
2. 필수 인용 형식.
3. 경량 어휘 evidence 검사(`simple_evidence_check`).
4. 근거가 약할 때 안전 fallback 응답.

실무 baseline입니다. production에서는 더 강한 faithfulness 검사를 고려하세요.
""",
    60: """## Step 9 — End-to-end RAG 함수(retrieval + 로컬 생성 + 안전)

이 함수는 다음을 결합합니다:
1. Vector DB에서 retrieval
2. 프롬프트 구성
3. `llama-cpp-python` 로컬 LLM 생성
4. 환각 안전 검사

필요하면 다른 LLM backend로 교체할 수 있습니다.
""",
    62: """### 선택 유틸 — 인용 형식 검사

**Step 7a 바로 다음** **다음** 코드 셀을 실행하세요(`sample_llm_answer`가 이미 있어야 함 — 이 선택 블록은 Step 7a 코드 셀 바로 아래).

Overlap 검사 외에 `[Doc 1]` 같은 인용 포함 여부를 검증합니다.
근거 기반 응답용 경량 guardrail입니다.
""",
    64: """## Step 10 — 학습자 실습 과제

이 연습으로 이해를 깊이고 설계 trade-off를 평가하세요.

1. 해양 PDF를 더 추가하고 출처 metadata(`doc_name`, `page`, `section`) 유지.
2. Chunk 크기 80 vs 120 vs 180 단어로 retrieval 품질 비교.
3. 장/페이지 범위 metadata 필터 추가.
4. 다른 로컬 GGUF 모델 시도 및 답 품질 비교.
5. 근거 프롬프트 + evidence 검사 전후 환각률 측정.

---

## 요약

로컬 추론으로 전체 RAG 워크플로를 완료했습니다:
- PDF ingestion 및 chunk 설계
- PDF chunk 위 벡터 인덱싱·retrieval
- `llama-cpp-python` 근거 기반 로컬 생성
- 기본 환각 완화 및 안전 fallback

이 노트북은 교육용 실습으로 정리되었으며 production 지향 prototype으로 확장할 수 있습니다.
""",
    65: """---

## Section B — 노트북 RAG와 Ollama 모델 서비스 사용

Section B 중요 설계 규칙:
- **RAG 로직은 이 노트북에 유지**(chunking, embedding, retrieval, context 포맷).
- 별도 Python 파일은 **Ollama 모델 호출만** 담당.

전용 Ollama 클라이언트 파일:
- `ollama_model_runner.py`

실무 아키텍처와 유사:
1. 노트북이 검색 context에서 프롬프트 준비.
2. 외부 클라이언트 스크립트가 하나 또는 여러 Ollama 모델 호출.
3. 노트북이 모델 응답 시각화.

""",
    66: """### Step 1: 경량 클라이언트 의존성 설치

이 의존성은 노트북에서 Ollama API 호출 및 응답 파싱용입니다.
노트북 RAG 단계를 대체하지 않습니다.
""",
    69: """### Step 2: Ollama 서비스/모델 설치·준비(수동 체크리스트)

먼저 Ollama를 설치하세요(노트북 밖):

- **Windows**: [https://ollama.com/download](https://ollama.com/download)에서 다운로드·설치
- **macOS**: `brew install ollama` 또는 Ollama 웹사이트 설치
- **Linux**:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

터미널에서 다음 명령 실행:

```bash
ollama serve
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama list
```

노트북 밖에서 하는 이유:
- Ollama는 영구 서비스 프로세스.
- 노트북 커널은 재시작·백그라운드 서비스 중단 가능.
- 외부 서비스 + 스크립트 호출이 반복 실험에 더 안정적.

설치·서비스 시작이 끝나면 아래 셀을 계속 실행하세요.
""",
    72: """### Step 3: 노트북 생성 프롬프트로 모델 클라이언트 실행

외부 클라이언트 스크립트를 실행합니다.
RAG context/프롬프트는 노트북에서 준비한 뒤 Python 클라이언트로 Ollama에 전송합니다.
""",
    75: """### Step 4: 시각 비교용 JSON 요약 파싱

스크립트 끝에 JSON 요약을 출력합니다.
이 셀은 노트북에서 읽기 쉽게 주요 필드를 추출·시각화합니다.
""",
    78: """### Step 5: 다른 모델 세트로 재실행·비교

여러 실행을 빠르게 비교하는 템플릿 셀입니다.
모델 세트를 수정하고 재실행하세요.
""",
    80: """### 문제 해결 체크리스트

실행 실패 시:
1. Ollama 서버 실행 확인: `ollama serve`.
2. 모델 존재 확인: `ollama list`.
3. 없는 모델 pull: `ollama pull <model>`.
4. host·port 확인(`http://localhost:11434`).
5. Step 3 재실행 후 stderr 점검.

노트북 runtime 안에서 Ollama를 직접 호스팅하는 것보다 이 분리 runner 아키텍처가 의도적이며 더 견고합니다.
""",
    82: """---

## Section C — LangChain 고급 RAG

### 이 섹션이 있는 이유(초보자용)

**Section A**에서는 RAG를 “손으로” 만들었습니다: chunking, embedding, FAISS 저장, retrieval 함수 작성, 프롬프트로 LLM 호출. 각 구성요소를 *이해*하기에 가장 좋습니다.

**LangChain**은 흔한 RAG 패턴을 재사용 가능한 조각(document, embedding, vector store, retriever, chain)으로 감쌉니다. 수학(벡터 유사도 검색)은 같지만 boilerplate 연결이 줄고 retrieval 전략 교체가 빨라집니다.

이 섹션은 Section A를 **대체하지 않습니다**. 이미 만든 동일 `manual_chunks`를 **재사용**해 “raw pipeline” vs “LangChain orchestration”을 같은 데이터로 비교합니다.

### 사전 조건(먼저 실행)

1. **Section A** chunking까지 완료해 `manual_chunks`가 비어 있지 않게.
2. 가능하면 Section A **embedding 설정**도 완료 — `embed_model_name`을 재사용해 LangChain이 노트북과 **동일** Sentence-Transformers 모델명 사용(공정 비교).
3. `call_local_llm(...)`을 쓰는 QA 셀은 Section A **로컬 LLM 설정** 완료(생성 방식 동일).

### 여기서 연습할 것

- **Document와 metadata**: 각 chunk를 page 번호·chunk id가 있는 LangChain `Document`(`page_content`, `metadata`)로.
- **Vector store**: document 위 LangChain FAISS wrapper 구축(수동 FAISS와 병렬 두 번째 index).
- **Retriever**: **similarity** vs **MMR**(다양성 인식 retrieval) 비교.
- **End-to-end QA**: LangChain으로 retrieve, 생성은 노트북 `call_local_llm` — *retrieval layer*만 실험 간 변경.

### 학습 목표

Section C 끝에 설명할 수 있어야 합니다: *LangChain이 plain Python + FAISS 위에 무엇을 더하나?* *MMR이 모델이 보는 evidence를 어떻게 바꿀 수 있나?*
""",
    83: """### Step 1: LangChain 패키지 설치

LangChain은 여러 installable 패키지로 나뉩니다. 이 워크샵에서는:

- **`langchain`**: 예제 전반 core 추상화·조합 유틸.
- **`langchain-community`**: community 통합, 여기서 쓰는 **FAISS vector store wrapper**(`langchain_community.vectorstores.FAISS`).
- **`langchain-huggingface`**: **`HuggingFaceEmbeddings`** wrapper — LangChain이 노트북과 같은 Sentence-Transformers 계열 호출.

#### pip 셀 실행 시

- 패키지가 현재 Python 환경(로컬, Colab VM 등)에 다운로드됩니다.
- 버전 변경 시 설치 후 **커널 재시작** 안내가 나올 수 있습니다. 설치 직후 import 실패면 커널 한 번 재시작 후 import 재실행.

#### 초보자 흔한 이슈

- **첫 import 느림**: HuggingFace/Sentence-Transformers가 첫 사용 시 가중치 다운로드.
- **디스크/RAM**: 전체 PDF를 두 번 embedding(Section A index + LangChain index)하면 메모리 추가 사용 — 교육 노트북에서는 정상.

이 단계 성공 후 Step 2에서 `manual_chunks`를 LangChain document로 변환합니다.
""",
    85: """### Step 2: LangChain document 및 vector store 구축

#### Mental model: `manual_chunks` → LangChain 객체

`manual_chunks` 목록은 이미 깔끔한 텍스트 snippet “DB 테이블”입니다. LangChain은 각 행을 **`Document`**로 기대합니다:

- **`page_content`**: retriever가 순위 매기고 LLM이 읽을 실제 chunk 텍스트.
- **`metadata`**: 나중 필터용 구조 필드(여기: `chunk_id`, `page`, `chunk_method`). 좋은 metadata는 *어느 PDF 페이지*가 답을 뒷받침했는지 보여 디버깅이 쉬움.

#### 코드 셀이 하는 일(실행 전 읽기)

1. **`Document(...)`**: `manual_chunks` 각 dict를 LangChain 표준 타입으로 감쌈.
2. **`HuggingFaceEmbeddings(model_name=...)`**: 문자열→벡터 방법 지정. Section A `embed_model_name`이 있으면 의도적으로 재사용해 embedding 비교 가능.
3. **`FAISS.from_documents(...)`**(코드에서 `LCFAISS`): LangChain이 document로 **in-memory FAISS index** 구축. 수동 FAISS와 **병렬**이며 이전 작업을 **삭제하지 않음**.

#### 두 번째 index를 만드는 이유?

LangChain retriever demo는 vector store가 LangChain 객체일 때 가장 쉽습니다. **교육적으로**: *같은 chunk, 같은 embedding 아이디어, 다른 retrieval 실험 “API surface”*.

#### 기대 출력

LangChain doc 수, embedding model 이름 등이 출력됩니다. `manual_chunks` 없음 `RuntimeError`면 Section A chunking 셀로 돌아가세요.
""",
    87: """### Step 3: 고급 retriever 설정(Similarity vs MMR)

Retrieval은 LLM이 **볼 수 있는 evidence**를 정합니다. 작은 변경도 모델이 같아도 답을 많이 바꿀 수 있습니다.

#### Strategy A: Similarity search(baseline)

**아이디어**: embedding 유사도로 chunk 순위 매기고 top `k` 반환.

- **강점**: 단순·빠름; “정답”이 소수 highly similar 구절에 몰릴 때 보통 좋음.
- **약점**: 상위 결과가 **거의 중복**(인접 페이지 유사 chunk)일 수 있음 — context window 낭비, 같은 생각 반복 편향.

LangChain: `search_type='similarity'`.

#### Strategy B: MMR(Max Marginal Relevance)

**아이디어**: highly similar 후보 pool(`fetch_k`)에서 시작해 `k` chunk 선택 시 균형:

- 쿼리 relevance, 및
- 선택 chunk 간 **다양성**(거의 같은 단락 다섯 개 피하기).

`lambda_mult`가 trade-off(1.0에 가까우면 relevance, 0.0에 가까우면 diversity — 구현마다 약간 다르므로 tuning knob로 취급).

LangChain: `search_type='mmr'`.

#### 표 출력 읽는 법

동일 demo 쿼리를 두 retriever로 실행해 결합 preview 표 출력. 비교:

- **Pages**: MMR이 evidence를 더 많은 페이지에 퍼뜨리는가?
- **Text previews**: MMR이 반복 wording을 줄이는가?

#### 조정 가능 파라미터(학습 연습)

- `k`: 프롬프트 context에 들어갈 chunk 수.
- `fetch_k`(MMR): diversify 전 고려 후보 수.
- `lambda_mult`(MMR): relevance vs diversity.

""",
    89: """### Step 4: LangChain 스타일 grounded QA 함수 구축

**Retrieval**과 **generation**을 하나의 helper로 연결합니다.

#### `lc_answer_question(...)`가 하는 일(개념적으로 한 줄씩)

1. `strategy`(`similarity` vs `mmr`)와 `top_k`로 retriever 선택.
2. **`retriever.invoke(question)`**: LangChain이 해당 질문용 순위 `Document` 목록 반환.
3. **`lc_join_context(...)`**: 검색 doc을 `[i] (p.X)` 마커가 있는 하나의 context 문자열로 — 모델·사람이 evidence 위치 참조.

#### 여기서 LangChain chat model 대신 `call_local_llm(...)`을 쓰는 이유

교육용 통제 실험:

- **변경**: retrieval orchestration(LangChain retriever mode).
- **유지**: 프롬프트 형식·로컬 model backend.

`build_grounded_prompt(...)`가 있으면 재사용 후 Section A와 동일 `call_local_llm(...)` 호출 — 답 차이를 retrieval 동작에 귀속하기 쉬움.

#### 출력 answer preview에서 볼 것

- 답이 프롬프트 요구대로 grounded way로 evidence 인용하는가?
- MMR이 similarity-only보다 code의 **더 넓은** 측면을 언급하는가?

`call_local_llm` 미정의면 Section A LLM 설정 셀 후 실행.
""",
    91: """### Step 5: 질문별 retrieval 전략 비교

**미니 evaluation loop**: 동일 세 질문을 두 번(similarity vs MMR) 답합니다.

#### 출력 표 해석

각 행은 `(question, strategy)` 한 쌍. 교실 토론용 열:

- **`retrieved_pages`**: top-k evidence에 나온 PDF 페이지. MMR 의도대로면 similarity만보다 **더 퍼짐**(항상은 아님 — 쿼리·chunking에 따름).
- **`answer_len`**: 장황함 rough proxy(품질 자체는 아님).
- **`answer_preview`**: 빠른 스캔용 snippet.

#### “좋음”의 실무 기준

좋은 RAG 답이 꼭 가장 길 필요는 없습니다. 확인:

- 검색 페이지에 묶인 grounded 진술,
- 모순 적음,
- 한 구절 “복붙 반복” 적음.

#### 연습 확장

- `lc_questions`에 질문 추가.
- `top_k=6` vs `top_k=3` — evidence vs 환각 위험.
- `lc_answer_question(...)` 호출에서 temperature 변경(안정성 연구).

Section C 종료: **chunks → LangChain vector store → retriever → prompt → local LLM** 전 경로를 설명하고 MMR이 evidence bundle을 바꿀 수 있는 이유를 설명할 수 있어야 합니다.
""",
    93: """---

## Section D — LlamaIndex 고급 RAG

### 이 섹션이 있는 이유(초보자용)

**LlamaIndex**는 LLM과 함께 지식 **indexing**·**querying**에 초점을 둔 프레임워크입니다. LangChain처럼 Section A fundamentals를 “대체”하지 않고, document·index·retriever·query engine 등 상위 객체로 retrieval 중심 워크플로를 빠르게 반복합니다.

**동일** `manual_chunks`로 세 스타일 비교:

1. **Section A**: 명시적 Python + FAISS + 자체 함수.
2. **Section C**: LangChain document/vectorstore/retriever API.
3. **Section D**: LlamaIndex document/index/retriever API.

### LlamaIndex 핵심 용어(한 번 읽기)

- **`Document`**: metadata와 함께 chunk 하나(LangChain `Document`와 유사하지만 LlamaIndex 클래스).
- **`VectorStoreIndex`**: 설정 embedding model(`Settings.embed_model`)로 document에서 vector index 구축.
- **`Retriever`**: 쿼리용 순위 **node**(검색 구절) 반환.
- **Node vs Document(직관)**: 많은 LlamaIndex flow에서 document가 내부 “node”가 됨. 초보자는 retrieved `node.text`를 모델이 읽을 chunk 텍스트로 보면 됨.

### 사전 조건

Section C와 동일:

- Section A에서 `manual_chunks` 필요.
- 가능하면 `embed_model_name` 재사용 — embedding 정렬.
- 생성은 Section A `call_local_llm(...)`.

### 여기서 연습할 것

- `Settings.embed_model`로 전역 embedding model 설정.
- `VectorStoreIndex.from_documents(...)` 구축.
- LLM 호출 전 retrieval 결과를 표로 inspect.
- 소규모 multi-question evaluation snapshot.

### 학습 목표

Section D 끝: *LlamaIndex가 raw FAISS 코드 대비 무엇을 최적화하나?* *Retrieval 디버깅 시 항상 무엇을 출력해야 하나(pages, scores, previews)?*
""",
    94: """### Step 1: LlamaIndex 패키지 설치

두 부분 설치:

- **`llama-index`**: core(document, indexing, retrieval, query engine 등).
- **`llama-index-embeddings-huggingface`**: HuggingFace/Sentence-Transformers embedding을 LlamaIndex embedding interface로.

#### 별도 embeddings 패키지인 이유

LlamaIndex는 optional 통합을 모듈화해 필요할 때까지 install을 작게 유지. 여기서는 notebook embedding 방식과 맞추려 HuggingFace embedding이 필요.

#### 설치 후

pip 직후 import 실패면 커널 재시작 → install 셀 → import 셀 순으로 재실행.

다음 단계는 `Settings.embed_model` 연결 — 이후 index 작업이 앞서 고른 embedding model name(`embed_model_name` 있을 때) 사용.
""",
    96: """### Step 2: LlamaIndex document 및 vector index 구축

#### 코드 셀이 하는 일

1. **`LIDocument(text=..., metadata=...)`**: 각 `manual_chunks` 항목을 LlamaIndex document로. Metadata는 투명성(page, chunk id)에 중요.
2. **`Settings.embed_model = HuggingFaceEmbedding(...)`**: 이 notebook session 이후 LlamaIndex 작업의 **전역 기본** embedding model.
3. **`VectorStoreIndex.from_documents(li_docs)`**: 모든 document embedding 후 query 가능 vector index.

#### Section A·C와의 관계

- Section A: 벡터·FAISS 수동 관리.
- Section C: LangChain 자체 FAISS wrapper.
- Section D: LlamaIndex 자체 internal vector store/index.

셋 공존 가능 — **embedding + nearest neighbor search**에 대한 다른 “front door”.

#### 초보자 성능 참고

Corpus를 다시 embedding. 예상:

- 첫 모델 다운로드 지연,
- 머신에 따른 CPU/GPU 시간.

#### 기대 출력

document 수, embedding model 이름. `manual_chunks` 없으면 Section A chunking으로.
""",
    98: """### Step 3: Retriever 설정 및 검색 node inspect

의도적으로 **retrieval만**(아직 LLM 없음). 실무에서 ROI 높은 디버깅: *모델 탓하기 전에 retrieval 검증.*

#### `as_retriever(similarity_top_k=5)` 의미

`similarity_top_k`: “쿼리 embedding과 가장 유사한 구절 top 5 반환”.

LangChain similarity의 `k`와 개념 같고 파라미터 이름만 framework마다 다름.

#### Preview 표 읽는 법

- **`rank`**: 1이 retriever 1순위.
- **`score`**: 있으면 retriever/node similarity 관련 score(버전/backend마다 해석 다를 수 있음). **한 쿼리 내 상대** 신호로, 절대 물리 단위 아님.
- **`page` / `chunk_id`**: chunking 출력 추적.
- **`text_preview`**: 검색 텍스트 on-topic sanity check.

#### 학습자 디버깅 질문

- 상위 구절이 쿼리 주제를 실제로 언급하는가?
- boilerplate/헤더만 반복 검색되는가?
- retrieval이 나쁘면 LLM 변경보다 chunking·embedding model 개선이 더 도움이 될까?

Retrieval이 그럴듯하면 Step 4 generation 추가.
""",
    100: """### Step 4: Notebook LLM backend로 LlamaIndex QA 함수

LlamaIndex는 full query engine(retriever + LLM + prompt template) orchestration 가능. 이 워크샵은 **의도적으로 단순화**:

1. LlamaIndex retrieval(`retrieve(...)`)로 evidence node 선택.
2. Node text를 하나의 context 문자열(`li_join_context`)로 결합.
3. 가능하면 grounded prompt builder(`build_grounded_prompt`) 재사용.
4. Section A와 동일 **`call_local_llm(...)`** 생성.

#### 이 설계 이유?

초보자는 “framework magic”과 “model intelligence”를 혼동하기 쉬움. generator 고정으로 LlamaIndex가 바꾼 것만 격리: **evidence 선택·패키징**.

#### `li_answer_question(...)` 반환

작은 Python dict:

- `nodes`: raw retrieved objects(심화 디버깅),
- `context`: 프롬프트에 들어간 정확한 문자열,
- `answer`: model output.

#### Section C와 비교

같은 질문에 대해:

- retrieved pages,
- context packaging,
- answer style·grounding.

Retrieved pages는 비슷한데 답이 크게 다르면 prompt/temperature/max tokens 이슈일 수 있음 — framework 아님.

Retrieved pages가 다르면 retrieval 설정(`similarity_top_k`)이 첫 tuning knob.

""",
    102: """### Step 5: Multi-question evaluation snapshot

고정 세 질문용 경량 “benchmark sheet”.

#### Evaluation 표 읽는 법

각 행은 `li_answer_question(...)` 한 번 실행.

- **`retrieved_pages`**: evidence breadth proxy. 항상 좁은 page만 보이면 쿼리가 모호하거나 `top_k`가 작거나 chunk가 반복 template text에 지배될 수 있음.
- **`answer_len`**: rough signal; 품질 채점은 full answer 수동 읽기와 병행.
- **`answer_preview`**: 환각 red flag 빠른 스캔(근거 없는 구체 숫자, 무관 규정 등).

#### 제안 교실 활동

1. retrieval 약한 질문 하나: **쿼리 wording** 먼저 개선(“list requirements”, “cite page numbers” 등 제약).
2. `similarity_top_k`를 약간 올려 evidence 개선 vs noisy해지는지 관찰.
3. 같은 질문 Section A baseline 답과 best LlamaIndex run 비교.

#### 다음 단계(선택 자습)

LlamaIndex는 query engine, response synthesizer, reranker, hybrid retrieval 등 풍부한 composition 지원. 이 노트북은 scope를 작게 유지해 초보자가 mental model을 먼저 완성.

Section D 완료: **documents → Settings embed model → vector index → retriever → grounded prompt → local LLM**, transparency용 표 포함.
""",
}

PRINT_REPLACEMENTS = [
    ('OK - llama-cpp-python and huggingface_hub are ready in this kernel.', '설정 완료 — llama-cpp-python과 huggingface_hub가 이 커널에서 준비되었습니다.'),
    ('Next: run Step 0b to download GGUF (or set LLAMA_CPP_GGUF manually).', '다음: Step 0b에서 GGUF 다운로드(또는 LLAMA_CPP_GGUF 수동 설정).'),
    ('Shared imports ready. Chroma available:', '공유 import 준비됨. Chroma 사용 가능:'),
    ('Using existing LLAMA_CPP_GGUF — skip download:', '기존 LLAMA_CPP_GGUF 사용 — 다운로드 건너뜀:'),
    ('Downloading from Hub:', 'Hub에서 다운로드:'),
    ('Set LLAMA_CPP_GGUF to:', 'LLAMA_CPP_GGUF 설정:'),
    ('Done. Continue to run next Steps', '완료. 다음 Step을 계속 실행하세요'),
    ("LLAMA_CPP_GGUF =", "LLAMA_CPP_GGUF ="),
    ("(not set)", "(미설정)"),
    ('Loaded pages from PDF:', 'PDF에서 로드한 페이지:'),
    ('Sample page title:', '샘플 페이지 제목:'),
    ('Sample text preview:', '샘플 텍스트 미리보기:'),
    ('  STEP 2.2 — chunk experiment parameters + sample page for A/B/C previews', '  STEP 2.2 — chunk 실험 파라미터 + A/B/C 미리보기용 샘플 페이지'),
    ('\\nchunk_params:', '\\nchunk_params:'),
    ('\\nSample page (for Step 2.3–2.5):', '\\n샘플 페이지(Step 2.3–2.5용):'),
    ('  title :', '  title :'),
    ('  words :', '  words :'),
    ('  note: no page had >= ', '  참고: >= '),
    (' words; using longest page — ', ' 단어인 페이지 없음 — 가장 긴 페이지 사용 — '),
    ('each method may still return a single chunk.', '각 method가 여전히 chunk 하나만 반환할 수 있습니다.'),
    ('\\nCorpus (all loaded pages) word-count summary:', '\\nCorpus(로드된 전체 페이지) 단어 수 요약:'),
    ('  pages: ', '  pages: '),
    ('  |  min / median / max words per page: ', '  |  페이지당 min / median / max words: '),
    ('\\nRun Step 2.3, then 2.4, then 2.5 and compare the boxed headers + previews in order.', '\\nStep 2.3 → 2.4 → 2.5 순으로 실행하고 박스 헤더·미리보기를 순서대로 비교하세요.'),
    ('  Step 2.4 add-on — fixed_words sensitivity (two settings on the SAME page)', '  Step 2.4 추가 — fixed_words 민감도(동일 페이지에서 설정 두 가지)'),
    ('\\nTip: lower chunk_words -> more chunks; higher overlap -> more text repeated between neighbors.', '\\n팁: chunk_words를 낮추면 chunk 수 증가; overlap을 높이면 인접 chunk 간 텍스트 반복 증가.'),
    ('  Step 2.5 add-on — heading_aware sensitivity (two max_words on the SAME page)', '  Step 2.5 추가 — heading_aware 민감도(동일 페이지에서 max_words 두 가지)'),
    ('\\nTip: smaller max_words usually increases chunk count after sections are formed.', '\\n팁: max_words를 작게 하면 섹션 형성 후 chunk 수가 보통 증가합니다.'),
    ('  STEP 2.6 — full corpus: three methods, identical chunk_params', '  STEP 2.6 — 전체 corpus: 세 method, 동일 chunk_params'),
    ('\\nTable (all pages in manual_docs):', '\\n표(manual_docs의 모든 페이지):'),
    ('\\nn_chunks visual (longer bar => more chunks for this corpus + params):', '\\nn_chunks 시각화(막대가 길수록 이 corpus + params에서 chunk 더 많음):'),
    ('\\nNote: equal n_chunks does not mean equal chunk boundaries — compare Step 2.3–2.5 previews.', '\\n참고: n_chunks가 같아도 chunk 경계는 다를 수 있음 — Step 2.3–2.5 미리보기 비교.'),
    ('Using default chunk method:', '기본 chunk method 사용:'),
    ('Selected chunk method:', '선택된 chunk method:'),
    ('Total chunks:', '총 chunk 수:'),
    ('Embedding model:', 'Embedding model:'),
    ('Embedding shape:', 'Embedding shape:'),
    ('Vector preview (first 8 dims):', '벡터 미리보기(처음 8차원):'),
    ('Batch size:', 'Batch size:'),
    ('Encoded ', '인코딩 완료 '),
    (' chunks in ', '개 chunk, '),
    ('Chroma collection ready:', 'Chroma collection 준비됨:'),
    ('Current item count (before add):', '현재 항목 수(add 전):'),
    ('Chroma not available in this runtime.', '이 runtime에서 Chroma를 사용할 수 없습니다.'),
    ('Add warning (possibly duplicate IDs):', 'Add 경고(중복 ID 가능):'),
    ('Skip: Chroma not available.', '건너뜀: Chroma 사용 불가.'),
    ('Index vectors:', 'Index vectors:'),
    ('Vector dimension:', 'Vector dimension:'),
    ('Metadata rows:', 'Metadata rows:'),
    ('Baseline top-4:', 'Baseline top-4:'),
    ('Tip: larger score_drop usually indicates stronger separation between top and tail results.', '팁: score_drop이 클수록 1위와 꼬리 결과 간 분리가 강함을 보통 의미합니다.'),
    ('Chroma retrieval sample:', 'Chroma retrieval 샘플:'),
    ('| score:', '| score:'),
    ('Chroma not available. FAISS pipeline is enough for this workshop.', 'Chroma 사용 불가. 이 워크샵에는 FAISS 파이프라인만으로 충분합니다.'),
    ('\\n--- Local LLM output ---\\n', '\\n--- 로컬 LLM 출력 ---\\n'),
    ('\\nSaved experiment_answers / Saved experiment_answers:', '\\n저장됨 experiment_answers:'),
    ('  JSON (full text):', '  JSON (전체 텍스트):'),
    ('  CSV (preview cols):', '  CSV (preview 열):'),
    ("\nFallback: I don't have enough evidence from retrieved documents.", "\nFallback: 검색된 문서에서 충분한 evidence가 없습니다."),
    ('Answer:\\n', 'Answer:\\n'),
    ('\\nSafety check:', '\\n안전 검사:'),
    ('Warning: answer has no explicit [Doc i] citations.', '경고: 답에 명시적 [Doc i] 인용이 없습니다.'),
    ('Runner exists:', 'Runner 존재:'),
    ('Runner path:', 'Runner 경로:'),
    ('Prompt chars:', 'Prompt chars:'),
    ('Command preview:', '명령 미리보기:'),
    ('Return code:', '반환 코드:'),
    ('\\n--- STDOUT (first 2500 chars) ---\\n', '\\n--- STDOUT (처음 2500자) ---\\n'),
    ('\\n--- STDERR (first 1200 chars) ---\\n', '\\n--- STDERR (처음 1200자) ---\\n'),
    ('Executing command:', '명령 실행:'),
    ('Elapsed:', '경과:'),
    (' sec', ' 초'),
    ('STDOUT chars:', 'STDOUT chars:'),
    ('| STDERR chars:', '| STDERR chars:'),
    ('--- STDOUT PREVIEW ---', '--- STDOUT 미리보기 ---'),
    ('(empty stdout)', '(stdout 비어 있음)'),
    ('\\n--- STDERR PREVIEW ---', '\\n--- STDERR 미리보기 ---'),
    ('(empty stderr)', '(stderr 비어 있음)'),
    ('Failed to parse JSON output from ollama_model_runner.py', 'ollama_model_runner.py JSON 출력 파싱 실패'),
    ('Error:', 'Error:'),
    ('\\nRaw stdout preview:', '\\n원시 stdout 미리보기:'),
    ('Raw stdout preview:', '원시 stdout 미리보기:'),
    ('Top-level keys:', '최상위 keys:'),
    ('Host:', 'Host:'),
    ('Models:', 'Models:'),
    ('No model outputs found in parsed payload.', '파싱된 payload에 model 출력 없음.'),
    ('Run Step 4 parsing cell first to generate out_df.', 'out_df 생성을 위해 먼저 Step 4 parsing 셀을 실행하세요.'),
    ('Parsed keys:', '파싱된 keys:'),
    ('LangChain docs:', 'LangChain docs:'),
    ('Question:', 'Question:'),
    ('Strategy:', 'Strategy:'),
    ('\\nAnswer preview:\\n', '\\nAnswer preview:\\n'),
    ('LlamaIndex docs:', 'LlamaIndex docs:'),
    ('METHOD A — sentence_window (sentence boundaries + sentence overlap)', 'METHOD A — sentence_window (문장 경계 + 문장 overlap)'),
    ('METHOD B — fixed_words (sliding word windows; may cut mid-sentence)', 'METHOD B — fixed_words (슬라이딩 단어 윈도우; 문장 중간 절단 가능)'),
    ('METHOD C — heading_aware (split on heading-like lines, then fixed windows per section)', 'METHOD C — heading_aware (제목형 줄 분할 후 섹션별 fixed window)'),
    ('Sensitivity — fixed_words SMALL (80/10)', '민감도 — fixed_words SMALL (80/10)'),
    ('Sensitivity — fixed_words LARGE (160/30)', '민감도 — fixed_words LARGE (160/30)'),
    ('Sensitivity — heading_aware SMALL (max_words=100)', '민감도 — heading_aware SMALL (max_words=100)'),
    ('Sensitivity — heading_aware LARGE (max_words=180)', '민감도 — heading_aware LARGE (max_words=180)'),
    (' (inner chunk_words)', ' (inner chunk_words)'),
    ('  -> n_chunks=', '  -> n_chunks='),
    ('  |  words/chunk: min=', '  |  words/chunk: min='),
    ('  avg=', '  avg='),
    ('  max=', '  max='),
    ('\\n  --- Preview chunk ', '\\n  --- Chunk 미리보기 '),
    (' words) ---', ' words) ---'),
    ('\\n  ... (', '\\n  ... ('),
    (' more chunks not shown; increase preview_max in the call.)', '개 chunk 더 있음; 호출에서 preview_max를 늘리세요.)'),
]
