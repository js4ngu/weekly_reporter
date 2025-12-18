class ReportStore:
    def __init__(self):
        # store reports per date as a list of report dicts
        # { date_str: [ {content, category, location, attendees}, ... ] }
        self._reports = {}

    def list_reports(self, date):
        return list(self._reports.get(date, []))

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
