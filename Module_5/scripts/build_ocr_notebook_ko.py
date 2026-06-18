#!/usr/bin/env python3
"""Generate Korean translation of Module_2 OCR notebook."""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "Module_2_OCR_Text_Extraction_Course_Colab.ipynb"
DST = Path(__file__).resolve().parents[1] / "Module_2_OCR_Text_Extraction_Course_Colab_KO.ipynb"

MARKDOWN_KO = {
    0: """# OCR를 이용한 텍스트 추출: 단계별 실습 과정

환영합니다! 이 노트북은 OCR(Optical Character Recognition, 광학 문자 인식)을 이해하고 실습하여 텍스트를 추출하는 실습형 미니 과정입니다.

## 학습 목표
이 노트북을 마치면 다음을 할 수 있습니다:
1. OCR이 무엇이며 어디에 사용되는지 설명할 수 있습니다.
2. 다양한 OCR 접근 방식과 도구를 이해할 수 있습니다.
3. **Tesseract**와 **EasyOCR**로 OCR을 실행할 수 있습니다.
4. **TrOCR**을 이용한 추가 **딥러닝 OCR** 예제를 시도할 수 있습니다.
5. 이미지 전처리(preprocessing)로 OCR 결과를 개선할 수 있습니다.
6. 서로 다른 OCR 기법의 출력을 비교할 수 있습니다.
7. 재사용 가능한 소규모 OCR 파이프라인을 구축할 수 있습니다.
8. 무료 데모 모드로 **Cloud OCR API**를 호출할 수 있습니다(별도 API 키 등록 불필요).
9. 입력 이미지 위에 바운딩 박스와 라벨로 OCR 결과를 **시각화**할 수 있습니다.

## 과정 구성
- Part 1: OCR 개념과 유형
- Part 2: 환경 설정
- (Part 3 초반) OCR 시각화 헬퍼 — 이미지 위 박스 + 라벨
- Part 3: PDF 읽기 및 페이지를 이미지로 변환
- Part 4: Tesseract OCR
- Part 5: EasyOCR
- Part 5.1 (선택): TrOCR 딥러닝 OCR
- Part 6: 전처리 기법
- Part 7: 나란히 비교
- Part 8: 미니 파이프라인
- Part 9: Cloud OCR API (무료 데모 모드)
- 마무리 노트 + 연습 문제
""",
    1: """## Part 1 - OCR 기초와 유형

### OCR이란?
OCR(Optical Character Recognition, 광학 문자 인식)은 이미지(사진, 스캔 문서, 스크린샷) 안의 텍스트를 기계가 읽을 수 있는 문자열로 변환하는 기술입니다.

### OCR의 일반적인 활용 사례
- 송장·영수증 처리
- 신분증/여권 및 양식 디지털화
- 차량 번호판 인식
- 아카이브 디지털화(도서/신문)
- 접근성(이미지 속 텍스트 읽기)

### 주요 OCR 접근 방식
1. **전통적 OCR (Traditional OCR)**
   - 이미지 처리 + 패턴 매칭 + 언어 모델을 사용합니다.
   - 예: **Tesseract**
   - 빠르고 가볍지만, 이미지 품질에 민감합니다.

2. **딥러닝 OCR (Deep Learning OCR)**
   - 신경망으로 텍스트 검출과 인식을 수행합니다.
   - 예: **EasyOCR** (내부적으로 딥러닝 모델 사용)
   - 어려운 이미지에서 보통 더 좋지만, 리소스 부담이 큽니다.

3. **Cloud OCR API**
   - 클라우드 제공업체의 관리형 서비스입니다.
   - 성능이 강력하고 다국어 지원이 우수합니다.
   - 인터넷, API 키, 유료 사용이 필요한 경우가 많습니다.

이번 수업에서는 **Tesseract**와 **EasyOCR**을 이용한 로컬 OCR에 집중합니다.
""",
    2: """## Part 2 - 환경 설정 (먼저 실행)

아래 셀을 순서대로 실행하세요. Python 라이브러리와 Tesseract OCR 엔진을 함께 설치합니다.

> 참고:
> - `pytesseract`는 Python 래퍼일 뿐이며, 시스템에 **Tesseract 실행 파일**도 필요합니다.
> - **Google Colab / Linux:** 다음 셀에서 `apt-get`으로 Tesseract를 설치합니다.
> - **로컬 conda (권장):** 활성 환경에서 `conda install -c conda-forge tesseract` 실행 후 커널을 재시작하세요.
> - **Windows:** [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)에서 설치하고, 필요하면 아래 `tesseract_cmd` 경로를 설정하세요.
""",
    6: """### Tesseract 경로 설정

아래 셀은 PATH 또는 Python 실행 파일과 같은 폴더(conda 환경에서 흔함)에서 Tesseract를 자동으로 찾습니다.

여전히 `TesseractNotFoundError`가 발생하면:
- Tesseract 설치 후 Jupyter 커널을 재시작하세요.
- Windows에서는 `tesseract.exe` 경로의 주석을 해제하고 설정하세요. 예: `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`
""",
    8: """## Part 3 - PDF 읽기 및 OCR용 이미지 변환

실제 OCR 프로젝트에서는 입력이 미리 만들어진 이미지가 아니라 **PDF**인 경우가 많습니다.
학습을 쉽게 하기 위해 이 파트는 작은 실행 단계로 나눕니다.

### 단계 개요
1. PDF 경로 설정 및 유효성 검사
2. PDF 페이지를 이미지로 변환
3. 페이지 이미지 시각화
4. 기본 전처리 적용
5. **전체 페이지 OCR** (타일 분할 전): 텍스트 추출 및 페이지 이미지에 **단어 박스 + 라벨** 그리기
6. (선택) **Part 3.1**: 페이지를 **제어 가능한 격자(grid)** 타일로 분할, 각 타일 OCR, 텍스트 병합, 스티치 — 3.1b에서 3.1a와 **동일한 타일** 사용(두 번째 분할 없음)

이 섹션은 Tesseract, EasyOCR, Cloud OCR API에 전달할 이미지 데이터를 준비합니다.
""",
    11: """### Step 2 - PDF 페이지를 이미지로 변환

이 셀을 실행하면 PDF의 모든 페이지가 PNG 파일로 렌더링됩니다.

참고:
- OCR 가독성을 위해 `zoom=2.0`이 좋은 기본값입니다.
- 작은 글자를 OCR이 놓치면 `zoom`을 높이세요(예: 2.5 또는 3.0).
- zoom이 높을수록 처리 시간과 메모리 사용량도 증가합니다.
""",
    13: """### Step 3 - 페이지 이미지 시각화 및 선택적 스트레스 테스트 이미지 생성

이 단계는 OCR 전에 입력 품질을 확인하도록 돕습니다.

또한 노이즈가 있고 약간 회전된 복사본(`noisy_path`)을 생성하여 어려운 실제 스캔을 시뮬레이션합니다.
이후 파트에서 쉬운 입력과 어려운 입력의 OCR 결과를 직접 비교할 수 있습니다.
""",
    15: """### Step 4 - OCR 전 전처리 적용

전처리는 특히 노이즈가 많은 스캔에서 OCR 정확도를 높이는 데 효과적입니다.

이 단계에서:
- 데이터 단순화를 위해 그레이스케일 변환
- 무작위 아티팩트 억제를 위한 노이즈 제거(denoising)
- 텍스트/배경 대비 강화를 위한 적응형 이진화(adaptive thresholding)

이 단계의 출력 파일(`preprocessed_pdf_path`)은 OCR에 바로 사용할 수 있습니다.
""",
    17: """### Step 5 — 분할 전 전체 페이지 OCR (텍스트 + 이미지 위 박스)

**전체 렌더링 페이지**(`clean_path`)에 **Tesseract**를 실행합니다 — 아직 **한 장의 이미지**, 타일 없음.

추출된 문자열을 출력하고, **단어 수준 박스**와 **라벨**이 있는 시각화 결과를 저장합니다(`pytesseract.image_to_data` 사용).

이 단계는 *타일로 자르기 전에 OCR이 전체 페이지에서 무엇을 보는지* 확인하는 데 답합니다.
""",
    19: """많은 경우, 이미지 크기를 크게 유지하면 작은 글자 일부가 인식되지 않는 것을 확인할 수 있습니다.
""",
    20: """### Part 3.1 (선택) OCR 전 매우 큰 이미지 분할

큰 페이지 이미지를 왜 분할해야 할까요?

1. **메모리와 속도**: 매우 고해상도 페이지 이미지는 처리 비용이 큽니다.
2. **인식 안정성**: 일부 OCR 엔진은 거대한 전체 페이지보다 작은 영역에서 더 잘 동작합니다.
3. **작은 글자 복구**: 전체 페이지 OCR이 놓치는 아주 작은 글꼴의 디테일을 타일링으로 보존할 수 있습니다.
4. **실패 격리**: 한 타일이 실패해도 다른 타일은 계속 처리할 수 있습니다.

트레이드오프:
- 타일이 너무 작으면 읽기 순서와 문맥 재구성이 어려워질 수 있습니다.
- 타일 경계 근처의 텍스트 잘림을 줄이기 위해 작은 `overlap`을 사용합니다.

페이지 크기가 크거나 전체 페이지 OCR 품질이 불안정할 때만 이 단계를 사용하세요.

### Part 3.1 개요 (아래 셀을 순서대로 실행)

Part 3 개요의 **Step 6**과 대응합니다:

| 섹션 | 수행 내용 |
|--------|-------------|
| **3.1a** | 페이지를 타일로 분할, crop 저장, 원본 이미지에 **타일 경계** 그리기 |
| **3.1b** | **각 타일에 OCR** 실행(Tesseract, `pytesseract` 경유), 읽기 순서로 **텍스트 병합** |
| **3.1c** | 타일 이미지를 전체 크기 캔버스에 **스티치**하고 원본과 **비교** |

> Part 4에서 `ocr_tesseract`를 정의하기 **전에** 타일 OCR이 동작하도록 여기서 `pytesseract`를 사용합니다.
""",
    22: """### Part 3.1b — 각 타일 OCR 및 텍스트 병합

**Part 3.1a의 동일한 `tile_records`를 재사용**합니다(두 번째 분할 없음). 3.1a에서 격자를 변경했다면, 이 셀 전에 3.1a를 다시 실행하세요.

각 타일에 **Tesseract**(`ocr_tile_tesseract`)를 실행합니다.

**읽기 순서:** `(y, x)` 기준 정렬(행 우선, row-major).

타일 **갤러리**의 `gallery_cols`는 분할이 아니라 matplotlib 레이아웃에만 사용됩니다.

OCR 모델이 텍스트를 제대로 추출하지 못하면 **Part 3.1a**의 **N_ROWS**와 **N_COLS** 값을 수정해 보세요.
""",
    24: """결과가 좋지 않다면(전체 텍스트가 추출되지 않는다면) 그 이유를 알고 있나요?

개선 방안을 공유해 보세요.

수업 내용을 계속 탐색한 뒤, 제안한 방법을 검증해 보세요.
""",
    25: """### Part 3.1c — 타일을 다시 전체 이미지로 스티치

원본 페이지와 같은 높이·너비의 **캔버스**를 다시 만들고, 각 타일을 `(y, x)` 위치에 붙입니다.

**시각적 확인:** **원본** vs **재구성**을 나란히 비교합니다. 단순 덮어쓰기 규칙 때문에 overlap 영역은 약간 다르게 보일 수 있습니다.

저장 파일: `data/part31c_stitched.png`.
""",
    27: """## Part 4 - Tesseract OCR

Tesseract는 텍스트가 선명하고, 대비가 높으며, 정렬이 잘 되어 있을 때 가장 잘 동작합니다.

### 주요 옵션
- `lang='eng'`: 영어 언어 모델 사용
- `--psm`: 페이지 분할 모드(page segmentation mode)
  - `6`: 균일한 텍스트 블록으로 가정
  - 레이아웃에 따라 다른 모드가 더 적합할 수 있습니다.
""",
    29: """## Part 5 - EasyOCR

EasyOCR은 딥러닝 기반 텍스트 검출과 인식을 포함합니다.
노이즈, 회전, 복잡한 레이아웃에서 전통적 OCR보다 잘 동작하는 경우가 많습니다.

첫 실행은 모델 가중치 다운로드로 인해 느릴 수 있습니다.
""",
    32: """EasyOCR 딥러닝 모델을 사용하면 결과가 개선되었습니다. 하지만 매우 큰 이미지에서는 여전히 한계가 있습니다.

이미지 분할 단계를 반복하여 텍스트를 추출하고 결과를 확인해 보세요.
""",
    33: """### Part 5.1 — EasyOCR 선택적 타일링 (Part 3.1과 동일 구조)

**Part 3.1a / 3.1b / 3.1c**와 같은 **격자 분할 → 타일별 OCR → 스티치 + 전체 캔버스에 모든 검출 결과 그리기** 흐름이지만, OCR은 **EasyOCR**(`reader.readtext`)을 사용합니다.

**사전 조건:** `split_image_grid`, `stitch_tiles_to_canvas`, `draw_tile_boxes_on_image`를 정의하는 **Part 3.1a** 코드 셀을 실행하세요. `reader`와 `draw_easyocr_overlay_bgr`를 위해 **Part 5** 셀도 실행하세요.

| 섹션 | 수행 내용 |
|--------|-------------|
| **5.1a** | `EZ_N_ROWS` × `EZ_N_COLS` 설정, `clean_path` 분할, `data/tiles_51a_easy/`에 타일 저장, 타일 경계 그리기 |
| **5.1b** | 5.1a의 `ez_tile_records` 재사용(**두 번째 분할 없음**), 타일별 EasyOCR + 텍스트 병합, 선택적 타일별 오버레이 갤러리 |
| **5.1c** | 타일 스티치, 모든 EasyOCR 검출을 **페이지 좌표**에 그리기, `data/part51c_easyocr_stitched_overlay.png` 저장 |
""",
    35: """### Part 5.1b — 각 타일 EasyOCR 및 텍스트 병합

**Part 5.1a의 `ez_tile_records`를 재사용**합니다(두 번째 분할 없음). 읽기 순서: `(y, x)` 기준 정렬.

matplotlib **갤러리**의 `gallery_cols_ez`는 레이아웃에만 사용됩니다.
""",
    37: """### Part 5.1c — 타일 스티치 및 전체 이미지에 EasyOCR 텍스트 그리기

`ez_tile_records`로 페이지를 재구성한 뒤, 타일별 EasyOCR을 실행하고 **각 polygon을 타일 원점만큼 offset**하여 스티치 캔버스에 라벨을 배치합니다. 저장 파일: `data/part51c_easyocr_stitched_overlay.png`.
""",
    39: """### Part 5.2 (선택) TrOCR 딥러닝 OCR

이 선택 섹션에서는 **TrOCR**만 다룹니다.

TrOCR이란?
- TrOCR은 Microsoft의 transformer 기반 OCR 모델입니다.
- vision encoder + text decoder 아키텍처를 사용합니다.
- 인쇄체 인식에 강하며 다양한 문서 스타일에 잘 일반화됩니다.

이 섹션이 선택인 이유:
- 추가 딥러닝 의존성이 필요합니다.
- 첫 실행 시 모델 가중치를 다운로드하므로 느릴 수 있습니다.
- CPU 추론은 가능하지만, 가벼운 OCR 엔진보다 느립니다.

환경이 제한적이면 이 섹션을 건너뛰고 나머지 노트북을 계속 진행하세요.
""",
    41: """코드 — TrOCR 로드 및 실행

다음 코드 셀을 실행하여:
1. TrOCR model/processor 로드,
2. `clean_path`와 `noisy_path`에서 OCR 실행,
3. 비교를 위해 선택적으로 `preprocessed_pdf_path` 테스트.

의존성이 없으면 위의 선택 설치 셀을 사용한 뒤 다시 실행하세요.
""",
    43: """TrOCR은 매우 큰 이미지에서는 어려움을 겪지만, 작은 이미지에서는 좋은 결과를 냅니다.

###**연습: TrOCR 사용 전에 이미지를 더 작은 부분으로 나누세요.** (이전 섹션과 유사)###
""",
    44: """#### TrOCR 참고 및 튜닝 팁

출력 품질 해석 방법:
- clean 이미지는 좋지만 noisy 이미지가 나쁘면, TrOCR 전에 더 강한 전처리를 추가하세요.
- 텍스트가 잘리면 `ocr_trocr(...)`의 `max_new_tokens`를 늘리세요.
- OCR이 느리면 모델을 한 번만 로드하고 여러 이미지를 루프로 처리하세요.

학습자를 위한 권장 실험:
1. `clean_path`, `noisy_path`, `prep_path`에서 TrOCR 결과 비교
2. 다른 checkpoint 시도(예: 손글씨 입력이면 손글씨 특화 모델)
3. 여러 페이지 이미지를 배치 처리하고 결과를 `.txt` 파일에 저장하는 헬퍼 작성
""",
    46: """## Part 6 - 전처리로 OCR 개선

전처리는 실무에서 OCR 품질을 가장 크게 향상시키는 방법 중 하나입니다.

일반적인 방법:
- 그레이스케일 변환
- 노이즈 제거(denoising)
- 이진화(binarization, thresholding)
- 기울기 보정(deskewing) / 회전 보정(de-rotation)
- 대비(contrast) 향상

아래에서는 간단한 전처리 파이프라인을 만들고 Tesseract로 테스트합니다.
""",
    48: """## Part 7 - OCR 출력 비교

이 섹션은 OCR 동작을 체계적으로 살펴보도록 돕습니다.

비교 항목:
1. 원본 noisy 이미지에서 Tesseract
2. 전처리된 이미지에서 Tesseract
3. 원본 noisy 이미지에서 EasyOCR

어떤 방법이 올바른 텍스트를 더 일관되게 추출하는지 시각적으로 확인할 수 있습니다.
""",
    50: """## Part 8 - 재사용 가능한 OCR 파이프라인 함수 구축

이제 실무에서 사용할 수 있도록 모든 기능을 하나의 헬퍼 함수로 묶습니다.

함수 지원:
- `method='tesseract'` 또는 `method='easyocr'`
- 선택적 전처리(`preprocess=True`)

실제 프로젝트에서 하는 방식과 유사합니다.
""",
    52: """## Part 9 - Cloud OCR API (무료 데모, API 키 수동 가입 불필요)

이 섹션에서는 **OCR.space**를 이용한 클라우드 OCR 서비스를 테스트합니다.

### 이 옵션을 선택하는 이유
- 학습용 공개 **데모 키**(`helloworld`)가 있습니다.
- 체험만 하려면 계정을 만들 필요가 **없습니다**.
- 강의/데모 워크플로에 적합합니다.

### 중요 참고
- 클라우드 OCR이므로 인터넷 연결이 필요합니다.
- 공개 데모 키는 제한이 엄격하며, 과부하 시 실패할 수 있습니다.
- 프로덕션에서는 자체 API 키를 사용하고 제공업체 제한/개인정보 정책을 따르세요.
""",
    54: """### Part 9.1 (선택) 자체 API 키를 사용하는 Cloud OCR API

이 하위 섹션은 **선택**입니다.

API 키가 없으면 Part 9.1의 모든 셀을 건너뛰고 다음 섹션으로 진행하세요.

예제를 셀별로 나눈 이유:
- 제공업체마다 endpoint, 인증 방식, 응답 스키마가 다릅니다.
- 학습자가 한 번에 하나의 제공업체만 테스트할 수 있습니다.
- 오류가 격리되어 디버깅이 쉽습니다.

모범 사례:
- 노트북에 API 키를 하드코딩하지 마세요.
- 환경 변수에서 키를 불러오세요.
""",
    56: """#### 선택 제공업체 예제 1 - Mistral OCR

`MISTRAL_API_KEY`가 있을 때 사용하세요.

참고:
- API 버전과 payload 스키마는 시간이 지나며 변경될 수 있습니다.
- 프로덕션 사용 전 공식 제공업체 문서를 반드시 확인하세요.
- 이 셀은 빠른 디버깅을 위해 상태와 짧은 응답 미리보기를 출력합니다.
""",
    58: """#### 선택 제공업체 예제 2 - Google Cloud Vision API

`GOOGLE_VISION_API_KEY`가 있을 때 사용하세요.

참고:
- 이 예제는 base64 인코딩된 이미지에 `TEXT_DETECTION`을 사용합니다.
- 응답 JSON은 클 수 있으므로 짧은 미리보기만 출력합니다.
- 실제 프로젝트에서는 `textAnnotations`를 파싱하여 구조화된 출력을 만듭니다.
""",
    60: """#### 선택 제공업체 예제 3 - Azure AI Document Intelligence

다음 두 값이 모두 있을 때 사용하세요:
- `AZURE_DOCINTEL_ENDPOINT`
- `AZURE_DOCINTEL_KEY`

참고:
- 이 API는 먼저 `202 Accepted`를 반환하는 경우가 많습니다.
- 최종 OCR 결과를 받으려면 보통 `operation-location`으로 두 번째 polling 요청이 필요합니다.
- 이 학습 셀에서는 상태와 헤더만 출력합니다.
""",
    62: """## 마무리 노트 및 실무 팁

### Tesseract를 선택할 때
- 가볍고 빠른 로컬 OCR 엔진이 필요할 때
- 문서가 대부분 깨끗한 스캔이나 인쇄체일 때

### EasyOCR을 선택할 때
- 이미지에 노이즈, 회전, 복잡한 레이아웃이 있을 때
- 수동 튜닝을 줄이면서 강한 기본 성능을 원할 때

### Cloud OCR API를 시도할 때
- 로컬 OCR 실행 파일 의존성 없이 빠르게 설정하고 싶을 때
- 확장 가능한 원격 처리가 필요할 때
- 인터넷 의존성과 외부 서비스로 이미지 데이터 전송을 수용할 수 있을 때

### 일반적인 OCR 프로젝트 워크플로
1. 대표적인 이미지 샘플 수집
2. 동일 데이터셋에서 로컬 OCR과 클라우드 OCR 벤치마크
3. 실패 패턴에 따라 전처리 추가
4. 지표(CER/단어 정확도)로 평가
5. 오류 처리를 포함한 견고한 파이프라인으로 래핑

## 학습자를 위한 연습 문제
1. Tesseract, EasyOCR, OCR.space 데모의 OCR 품질 비교
2. Tesseract에서 서로 다른 `--psm` 값 시도 및 품질 비교
3. 맞춤법 교정 후처리 추가
4. 손글씨 텍스트에서 OCR 품질 평가
5. 텍스트 + confidence + method name을 반환하는 함수 작성

수고하셨습니다! 이제 end-to-end OCR 학습 노트북을 완료했습니다.
""",
}

PRINT_REPLACEMENTS = [
    ("print('Tesseract not found on PATH.')", "print('PATH에서 Tesseract를 찾을 수 없습니다.')"),
    ("print('Install it once in your conda env, then restart the kernel:')", "print('conda 환경에 한 번 설치한 뒤 커널을 재시작하세요:')"),
    ("print('Imports completed successfully.')", "print('import가 성공적으로 완료되었습니다.')"),
    ("print('Tesseract detected:', version)", "print('Tesseract 감지됨:', version)"),
    ("print('Using:', pytesseract.pytesseract.tesseract_cmd)", "print('사용 경로:', pytesseract.pytesseract.tesseract_cmd)"),
    ("print('Tesseract not detected yet. Install it, restart the kernel, and re-run Part 2.')", "print('Tesseract가 아직 감지되지 않았습니다. 설치 후 커널을 재시작하고 Part 2를 다시 실행하세요.')"),
    ("print('Error:', e)", "print('오류:', e)"),
    ("print('PDF path is valid:', pdf_path)", "print('PDF 경로가 유효합니다:', pdf_path)"),
    ("print(f'Converted {len(page_image_paths)} pages from PDF to images.')", "print(f'PDF에서 {len(page_image_paths)}개 페이지를 이미지로 변환했습니다.')"),
    ("print('Main OCR page:', clean_path)", "print('주 OCR 페이지:', clean_path)"),
    ("print('Optional degraded test page:', noisy_path)", "print('선택적 저하 테스트 페이지:', noisy_path)"),
    ("print('Step 5 | Full-page OCR (clean_path, no tiles yet)\\n')", "print('Step 5 | 전체 페이지 OCR (clean_path, 아직 타일 없음)\\n')"),
    ("print(f'3.1a | Grid {N_ROWS}x{N_COLS} => {len(tile_records)} tiles  |  Page (H,W): {page_hw}')", "print(f'3.1a | 격자 {N_ROWS}x{N_COLS} => {len(tile_records)}개 타일  |  페이지 (H,W): {page_hw}')"),
    ("print('3.1b | Using', len(demo_records), 'tiles from Part 3.1a')", "print('3.1b | Part 3.1a의 타일', len(demo_records), '개 사용')"),
    ("print('MERGED OCR (all tiles, reading order)')", "print('병합 OCR (모든 타일, 읽기 순서)')"),
    ("print('Saved:', stitch_path)", "print('저장됨:', stitch_path)"),
    ("print('Tesseract result (clean image):\\n')", "print('Tesseract 결과 (clean 이미지):\\n')"),
    ("print('Tesseract result (noisy image):\\n')", "print('Tesseract 결과 (noisy 이미지):\\n')"),
    ("print('EasyOCR result (clean image):\\n')", "print('EasyOCR 결과 (clean 이미지):\\n')"),
    ("print('EasyOCR result (noisy image):\\n')", "print('EasyOCR 결과 (noisy 이미지):\\n')"),
    ("print('Saved:', part5_clean_overlay_path)", "print('저장됨:', part5_clean_overlay_path)"),
    ("print('Saved:', part5_noisy_overlay_path)", "print('저장됨:', part5_noisy_overlay_path)"),
    ("print(f'5.1a | EasyOCR tiling grid {EZ_N_ROWS}x{EZ_N_COLS} => {len(ez_tile_records)} tiles  |  Page (H,W): {ez_page_hw}')", "print(f'5.1a | EasyOCR 타일링 격자 {EZ_N_ROWS}x{EZ_N_COLS} => {len(ez_tile_records)}개 타일  |  페이지 (H,W): {ez_page_hw}')"),
    ("print('No tiles to show.')", "print('표시할 타일이 없습니다.')"),
    ("print('5.1b | EasyOCR on', len(demo_ez), 'tiles from Part 5.1a')", "print('5.1b | Part 5.1a의 타일', len(demo_ez), '개에 EasyOCR 실행')"),
    ("print('MERGED EasyOCR (all tiles, reading order)')", "print('병합 EasyOCR (모든 타일, 읽기 순서)')"),
    ("print('Saved:', part51c_path)", "print('저장됨:', part51c_path)"),
    ("print(f'Trying TrOCR model: {model_name}')", "print(f'TrOCR 모델 시도 중: {model_name}')"),
    ("print(f'  -> failed: {inner_e}')", "print(f'  -> 실패: {inner_e}')"),
    ("print(f'\\nSelected TrOCR model: {trocr_selected_model}')", "print(f'\\n선택된 TrOCR 모델: {trocr_selected_model}')"),
    ("print('TrOCR result (clean image):\\n')", "print('TrOCR 결과 (clean 이미지):\\n')"),
    ("print('TrOCR result (noisy image):\\n')", "print('TrOCR 결과 (noisy 이미지):\\n')"),
    ("print('\\nSaved outputs (clean):', clean_txt, clean_json, clean_img)", "print('\\n저장된 출력 (clean):', clean_txt, clean_json, clean_img)"),
    ("print('Saved outputs (noisy):', noisy_txt, noisy_json, noisy_img)", "print('저장된 출력 (noisy):', noisy_txt, noisy_json, noisy_img)"),
    ("print('TrOCR example skipped or failed.')", "print('TrOCR 예제가 건너뛰어졌거나 실패했습니다.')"),
    ("print('Tips:')", "print('팁:')"),
    ("print('- Install optional dependencies in the previous cell.')", "print('- 이전 셀에서 선택 의존성을 설치하세요.')"),
    ("print('- Ensure internet is available for first model download.')", "print('- 첫 모델 다운로드를 위해 인터넷 연결을 확인하세요.')"),
    ("print('- Retry after restarting kernel if memory is low.')", "print('- 메모리가 부족하면 커널 재시작 후 다시 시도하세요.')"),
    ("print('TrOCR result (preprocessed image):\\n')", "print('TrOCR 결과 (전처리 이미지):\\n')"),
    ("print('Preprocessed TrOCR run skipped or failed:', e)", "print('전처리 TrOCR 실행이 건너뛰어졌거나 실패했습니다:', e)"),
    ("print('Part 7 note: TrOCR inference failed, skip TrOCR in this section:', e)", "print('Part 7 참고: TrOCR 추론 실패, 이 섹션에서 TrOCR 건너뜀:', e)"),
    ("print('Part 7 note: TrOCR model not loaded in memory, skip TrOCR in this section.')", "print('Part 7 참고: TrOCR 모델이 메모리에 로드되지 않음, 이 섹션에서 TrOCR 건너뜀.')"),
    ("print('--- Tesseract (clean) ---')", "print('--- Tesseract (clean) ---')"),
    ("print('\\n--- Tesseract (noisy) ---')", "print('\\n--- Tesseract (noisy) ---')"),
    ("print('\\n--- EasyOCR (clean) ---')", "print('\\n--- EasyOCR (clean) ---')"),
    ("print('\\n--- EasyOCR (noisy) ---')", "print('\\n--- EasyOCR (noisy) ---')"),
    ("print('\\n--- TrOCR (clean) ---')", "print('\\n--- TrOCR (clean) ---')"),
    ("print('\\n--- TrOCR (noisy) ---')", "print('\\n--- TrOCR (noisy) ---')"),
    ("print('\\nSaved Part 7 overlay images:')", "print('\\nPart 7 오버레이 이미지 저장됨:')"),
    ("print('Pipeline demo:')", "print('파이프라인 데모:')"),
    ("print('\\n[Tesseract + preprocessing]\\n')", "print('\\n[Tesseract + 전처리]\\n')"),
    ("print('\\n[EasyOCR without preprocessing]\\n')", "print('\\n[전처리 없는 EasyOCR]\\n')"),
    ("print('Cloud OCR (OCR.space demo key) result:\\n')", "print('Cloud OCR (OCR.space 데모 키) 결과:\\n')"),
    ("print('Cloud OCR request failed.')", "print('Cloud OCR 요청이 실패했습니다.')"),
    ("print('Possible reasons: no internet, demo limit reached, temporary API issue.')", "print('가능한 원인: 인터넷 없음, 데모 한도 초과, 일시적 API 문제.')"),
    ("print('Optional provider key availability:')", "print('선택 제공업체 키 사용 가능 여부:')"),
    ("print('\\nIf all are False, skip Part 9.1.')", "print('\\n모두 False이면 Part 9.1을 건너뛰세요.')"),
    ("print('Skip: MISTRAL_API_KEY not found.')", "print('건너뜀: MISTRAL_API_KEY를 찾을 수 없습니다.')"),
    ("print('[Mistral OCR] status:', code)", "print('[Mistral OCR] 상태:', code)"),
    ("print('Skip: GOOGLE_VISION_API_KEY not found.')", "print('건너뜀: GOOGLE_VISION_API_KEY를 찾을 수 없습니다.')"),
    ("print('[Google Vision] status:', code)", "print('[Google Vision] 상태:', code)"),
    ("print('Skip: AZURE_DOCINTEL_ENDPOINT and/or AZURE_DOCINTEL_KEY not found.')", "print('건너뜀: AZURE_DOCINTEL_ENDPOINT 및/또는 AZURE_DOCINTEL_KEY를 찾을 수 없습니다.')"),
    ("print('[Azure Document Intelligence] status:', code)", "print('[Azure Document Intelligence] 상태:', code)"),
    ("print('Response headers:', headers)", "print('응답 헤더:', headers)"),
    ("print('Skip: OCRSPACE_API_KEY not found.')", "print('건너뜀: OCRSPACE_API_KEY를 찾을 수 없습니다.')"),
    ("print('[OCR.space personal key] result preview:\\n')", "print('[OCR.space 개인 키] 결과 미리보기:\\n')"),
    ("print('OCR.space personal key example failed:', e)", "print('OCR.space 개인 키 예제 실패:', e)"),
    ("print('--- Local: Tesseract (preprocessed) ---')", "print('--- 로컬: Tesseract (전처리됨) ---')"),
    ("print('\\n--- Local: EasyOCR ---')", "print('\\n--- 로컬: EasyOCR ---')"),
    ("print('\\n--- Cloud: OCR.space (demo key) ---')", "print('\\n--- 클라우드: OCR.space (데모 키) ---')"),
    ("print('Cloud OCR unavailable right now:', e)", "print('현재 Cloud OCR을 사용할 수 없습니다:', e)"),
]


def to_source_lines(text: str) -> list[str]:
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return lines or [""]


def apply_print_replacements(source: str) -> str:
    for old, new in PRINT_REPLACEMENTS:
        source = source.replace(old, new)
    return source


def main() -> None:
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    out = json.loads(SRC.read_text(encoding="utf-8"))

    for idx, cell in enumerate(out["cells"]):
        if cell["cell_type"] == "markdown" and idx in MARKDOWN_KO:
            cell["source"] = to_source_lines(MARKDOWN_KO[idx])
        elif cell["cell_type"] == "code":
            src = "".join(cell.get("source", []))
            cell["source"] = to_source_lines(apply_print_replacements(src))

    out["metadata"]["language_info"] = dict(out.get("metadata", {}).get("language_info", {}))
    out["metadata"]["language_info"]["name"] = "python"

    DST.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {DST}")


if __name__ == "__main__":
    main()
