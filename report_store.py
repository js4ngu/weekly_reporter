import json
from pathlib import Path


class ReportStore:
    def __init__(self, json_file=None):
        # store reports separated by owner ('personal' / 'shared')
        # { owner: { date_str: [ {content, category, location, attendees, start_date, end_date}, ... ] } }
        self._reports = {"personal": {}, "shared": {}}

        # JSON 파일 경로 설정
        if json_file is None:
            script_dir = Path(__file__).parent
            # prefer config.json inside the data folder if present (user requested)
            default_dir = "data"
            cfg_in_data = script_dir / default_dir / "config.json"
            cfg_root = script_dir / "config.json"
            output_dir = default_dir
            try:
                import json as _json
                # prefer config inside data folder
                if cfg_in_data.exists():
                    with open(cfg_in_data, 'r', encoding='utf-8') as _f:
                        cfg = _json.load(_f)
                        if isinstance(cfg, dict) and cfg.get("data_dir"):
                            output_dir = cfg.get("data_dir")
                elif cfg_root.exists():
                    with open(cfg_root, 'r', encoding='utf-8') as _f:
                        cfg = _json.load(_f)
                        if isinstance(cfg, dict) and cfg.get("data_dir"):
                            output_dir = cfg.get("data_dir")
            except Exception:
                pass
            json_file = script_dir / output_dir / "data.json"

        self.json_file = Path(json_file)
        self.json_file.parent.mkdir(parents=True, exist_ok=True)

        # 기존 JSON 파일이 있으면 로드
        self.load_from_json()

    def list_reports(self, date):
        # default to personal namespace for backward compatibility
        return list(self._reports.get("personal", {}).get(date, []))

    def list_reports_for(self, date, owner="personal"):
        return list(self._reports.get(owner, {}).get(date, []))

    def find_reports_for_date(self, date_str, owner=None):
        """주어진 날짜(date_str)가 포함되는 모든 보고서를
        (owner, orig_date, index, report) 형태로 반환
        date_str: 'YYYY-MM-DD'
        owner: 'personal'|'shared' 또는 None (둘 다 검색)
        """
        results = []
        try:
            from datetime import datetime as _dt
            target = _dt.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            return results

        owners = [owner] if owner else list(self._reports.keys())
        for ow in owners:
            reports_map = self._reports.get(ow, {})
            for orig_date, reports in reports_map.items():
                for idx, r in enumerate(reports):
                    s = r.get("start_date") or orig_date
                    e = r.get("end_date") or s
                    try:
                        s_date = _dt.strptime(s, "%Y-%m-%d").date()
                        e_date = _dt.strptime(e, "%Y-%m-%d").date()
                    except Exception:
                        continue

                    if s_date <= target <= e_date:
                        results.append((ow, orig_date, idx, r))

        return results

    def add_report(self, date, report=None, owner="personal"):
        if report is None:
            report = {"content": "", "category": "", "location": "", "attendees": "", "start_date": date, "end_date": ""}
        self._reports.setdefault(owner, {})
        self._reports[owner].setdefault(date, []).append(report)
        return len(self._reports[owner][date]) - 1

    def get_report(self, date, index, owner="personal"):
        return self._reports.get(owner, {}).get(date, [])[index]

    def update_report(self, date, index, report, owner="personal"):
        self._reports.setdefault(owner, {})
        self._reports[owner].setdefault(date, [])
        self._reports[owner][date][index] = report

    def move_report(self, old_date, new_date, index, report, owner="personal", new_owner=None):
        """보고서를 같은 owner 내에서 다른 날짜로 이동하거나 owner를 바꿔 이동"""
        if new_owner is None:
            new_owner = owner
        # 기존 날짜에서 삭제
        if old_date in self._reports.get(owner, {}) and 0 <= index < len(self._reports[owner][old_date]):
            try:
                del self._reports[owner][old_date][index]
            except Exception:
                pass
        # 새 날짜에 추가
        self._reports.setdefault(new_owner, {})
        self._reports[new_owner].setdefault(new_date, []).append(report)
        return len(self._reports[new_owner][new_date]) - 1

    def delete_report(self, date, index, owner="personal"):
        if date in self._reports.get(owner, {}) and 0 <= index < len(self._reports[owner][date]):
            del self._reports[owner][date][index]

    def has_reports(self, date, owner="personal"):
        return bool(self._reports.get(owner, {}).get(date))

    def list_categories(self):
        cats = set()
        for owner_map in self._reports.values():
            for reports in owner_map.values():
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
                data = json.load(f)
                # backward compatibility: older format was a flat date->list mapping
                if isinstance(data, dict) and ("personal" in data or "shared" in data):
                    # assume new format
                    self._reports = data
                else:
                    # old format: treat as personal
                    self._reports = {"personal": data or {}, "shared": {}}
        except Exception as e:
            print(f"JSON 로드 실패: {e}")
            self._reports = {"personal": {}, "shared": {}}
