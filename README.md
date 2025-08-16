# 🗂️ TrandNavi_AI 프로젝트 구조 설명

이 문서는 **TrandNavi_AI 프로젝트**의 디렉토리 및 파일 구조를 설명합니다.  
Flask 기반의 웹 애플리케이션으로, AI 챗봇 기능을 중심으로 한 구조를 가지고 있습니다.

---

## 📁 프로젝트 구조

```plaintext
TrandNavi_AI/
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── admin.py
│   ├── templates/
│   │   ├── index.html
│   │   └── chat.html
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── utils/
│       ├── prompt_builder.py
│       └── vector_search.py
├── migrations/
│   └── ... (DB 마이그레이션 파일)
├── uploads/
│   └── ... (사용자 업로드 파일 저장소)
├── requirements.txt
├── run.py
└── test.py
```

---

## 📄 주요 파일 설명

### 🔸 `run.py`
- 애플리케이션 실행 진입점입니다.
- Flask 개발 서버를 실행합니다.

### 🔸 `requirements.txt`
- 프로젝트에 필요한 Python 의존성 패키지 목록이 들어 있습니다.

### 🔸 `alembic.ini`
- Alembic 데이터베이스 마이그레이션 설정 파일입니다.

---

## 📂 디렉토리 설명

### 📂 `app/`
웹 애플리케이션의 핵심 소스 코드가 위치합니다.

- `__init__.py` : Flask 앱 초기화 및 설정
- `main.py` : 앱 실행 및 엔트리 포인트
- `views/` : 라우트(컨트롤러) 모음
  - `chat.py` : 사용자-챗봇 대화 처리
  - `admin.py` : 관리자 전용 기능 처리
- `templates/` : HTML 템플릿 (Jinja2/Mako 기반)
  - `index.html` : 메인 페이지
  - `chat.html` : 챗봇 인터페이스
- `static/` : 정적 리소스 (CSS, JS, 이미지 등)
- `utils/` : 보조 기능
  - `prompt_builder.py` : LLM 프롬프트 구성
  - `vector_search.py` : 벡터 기반 검색 기능

### 📂 `migrations/`
- Alembic 기반 데이터베이스 마이그레이션 파일 관리.

### 📂 `uploads/`
- 사용자 업로드 파일 저장 디렉토리 (이미지, 음성 등).

---

## ✅ 정리

이 프로젝트는 **Flask 웹 프레임워크**를 기반으로 구성되어 있으며,  
MVC 아키텍처를 참고하여 `views`, `templates`, `static`, `utils` 폴더로 나뉘어 있습니다.  
또한 `migrations`와 `uploads` 디렉토리를 통해 실무적인 기능까지 고려한 구조를 갖추고 있습니다.
