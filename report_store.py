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
