# Weekly Reporter

간단한 개인/공통/주간 보고서 GUI 툴입니다.

**파일 구조**
- `main.py`: 앱 실행 진입점
- `app.py`: 애플리케이션 윈도우, 캘린더, 탭을 초기화하는 `ReportApp` 클래스
- `tabs.py`: 각 탭 UI와 컨트롤러 클래스들 (`PersonalTab`, `SharedTab`, `WeeklyTab`, `SpareTab`)
- `report_store.py`: 데이터 모델 및 JSON 기반 영구 저장을 담당하는 `ReportStore` 클래스
- `config.json`: (선택) 색상 및 출력 경로 설정
- `output/`: 저장된 JSON 파일들

**클래스 구조 (요약)**
- `ReportStore` (`report_store.py`)
  - 역할: 보고서 추가/조회/수정/삭제, JSON 직렬화/역직렬화
  - 주요 메서드: `add_report()`, `list_reports()`, `find_reports_for_date()`, `save_to_json()`, `load_from_json()`

- `ReportApp` (`app.py`)
  - 역할: Tkinter 윈도우 및 레이아웃 구성, 캘린더 하이라이팅, 탭 인스턴스 관리
  - 주요 속성:
    - `personal_tab`: 개인업무 탭 인스턴스 (`PersonalTab`)
    - `shared_tab`: 공통업무 탭 인스턴스 (`SharedTab`)
    - `weekly_tab`: 개인주간업무보고 탭 인스턴스 (`WeeklyTab`)
    - `spare_tab`: 예비 탭 인스턴스 (`SpareTab`)
  - 주요 메서드: `go_to_today()`, `on_date_select()`, `run()`

- 탭 클래스들 (`tabs.py`)
  - `PersonalTab`: 개인업무 입력/수정/삭제 UI
  - `SharedTab`: 공통업무/검색 UI
  - `WeeklyTab`: 주간 통계/보고서 집계 뷰
  - `SpareTab`: 설정 화면

**간단 사용법**
1. 가상환경에서 의존 패키지 설치 (`tkcalendar` 필요)

```bash
pip install tkcalendar
```

2. 앱 실행

```bash
python main.py
```

원하시면 README에 더 자세한 클래스 다이어그램이나 예시 스크린샷도 추가해 드리겠습니다.
