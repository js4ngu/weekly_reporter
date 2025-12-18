import json
import os
from pathlib import Path


class ReportStore:
    def __init__(self, json_file=None):
        # store reports per date as a list of report dicts
        # { date_str: [ {content, category, location, attendees}, ... ] }
        self._reports = {}
        
        # JSON 파일 경로 설정
        if json_file is None:
            script_dir = Path(__file__).parent
            json_file = script_dir / "output" / "personal_report.json"
        
        self.json_file = Path(json_file)
        self.json_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 기존 JSON 파일이 있으면 로드
        self.load_from_json()

    def list_reports(self, date):
        return list(self._reports.get(date, []))

    def find_reports_for_date(self, date_str):
        """주어진 날짜(date_str)가 포함되는 모든 보고서를 (orig_date, index, report) 형태로 반환
        date_str: 'YYYY-MM-DD'
        """
        results = []
        try:
            from datetime import datetime as _dt
            target = _dt.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            return results

        for orig_date, reports in self._reports.items():
            for idx, r in enumerate(reports):
                # Determine start and end
                s = r.get("start_date") or orig_date
                e = r.get("end_date") or s
                try:
                    s_date = _dt.strptime(s, "%Y-%m-%d").date()
                    e_date = _dt.strptime(e, "%Y-%m-%d").date()
                except Exception:
                    continue

                if s_date <= target <= e_date:
                    results.append((orig_date, idx, r))

        return results

    def add_report(self, date, report=None):
        if report is None:
            report = {"content": "", "category": "", "location": "", "attendees": ""}
        self._reports.setdefault(date, []).append(report)
        return len(self._reports[date]) - 1

    def get_report(self, date, index):
        return self._reports.get(date, [])[index]

    def update_report(self, date, index, report):
        self._reports.setdefault(date, [])
        self._reports[date][index] = report

    def move_report(self, old_date, new_date, index, report):
        """보고서를 다른 날짜로 이동"""
        # 기존 날짜에서 삭제
        if old_date in self._reports and 0 <= index < len(self._reports[old_date]):
            del self._reports[old_date][index]
        # 새 날짜에 추가
        self._reports.setdefault(new_date, []).append(report)
        return len(self._reports[new_date]) - 1

    def delete_report(self, date, index):
        if date in self._reports and 0 <= index < len(self._reports[date]):
            del self._reports[date][index]

    def has_reports(self, date):
        return bool(self._reports.get(date))

    def list_categories(self):
        cats = set()
        for reports in self._reports.values():
            for r in reports:
                if r.get("category"):
                    cats.add(r["category"])
        return sorted(cats)

    def save_to_json(self):
        """모든 보고서를 JSON 파일로 저장"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self._reports, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"JSON 저장 실패: {e}")

    def load_from_json(self):
        """JSON 파일에서 보고서 로드"""
        if not self.json_file.exists():
            return
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self._reports = json.load(f)
        except Exception as e:
            print(f"JSON 로드 실패: {e}")
            self._reports = {}
