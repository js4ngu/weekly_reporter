import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime


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


class ReportApp:
    def __init__(self):
        self.store = ReportStore()
        self.root = tk.Tk()
        self.root.geometry("800x400")

        self.cal = Calendar(
            self.root,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            firstweekday="sunday",
            showweeknumbers=False
        )
        self.cal.pack(side="left", fill="both", expand=True)

        # highlight this week and following weeks
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")

        # tag for this week (Mon-Fri) - shaded background
        monday = today - datetime.timedelta(days=today.weekday())
        for i in range(5):
            d = monday + datetime.timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            try:
                self.cal.calevent_create(d_str, "week", "thisweek")
            except Exception:
                self.cal.calevent_create(d, "week", "thisweek")
        self.cal.tag_config("thisweek", background="#E6E6E6")

        # next week (Mon-Fri) - light blue
        next_monday = monday + datetime.timedelta(days=7)
        for i in range(5):
            d = next_monday + datetime.timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            try:
                self.cal.calevent_create(d_str, "week_next", "nextweek")
            except Exception:
                self.cal.calevent_create(d, "week_next", "nextweek")
            self.cal.tag_config("nextweek", background="#7FBFFF", foreground="#7FBFFF")

        # week after next (Mon-Fri) - deeper blue
        nextnext_monday = monday + datetime.timedelta(days=14)
        for i in range(5):
            d = nextnext_monday + datetime.timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            try:
                self.cal.calevent_create(d_str, "week_nextnext", "nextnextweek")
            except Exception:
                self.cal.calevent_create(d, "week_nextnext", "nextnextweek")
            self.cal.tag_config("nextnextweek", background="#2190FF", foreground="#2190FF")

        # tag for today (yellow text, adjusted for contrast)
        try:
            self.cal.calevent_create(today_str, "today", "today")
        except Exception:
            self.cal.calevent_create(today, "today", "today")
        # use a slightly darker yellow for better visibility on white
        self.cal.tag_config("today", foreground="#FFAA00")

        # make selected day visually distinct: red text only (no background change)
        try:
            self.cal.configure(selectforeground="#FF0000")
        except Exception:
            pass
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

        self.right = tk.Frame(self.root)
        self.right.pack(side="right", fill="both", expand=True)

        # Top: report list for the selected date
        self.list_frame = tk.Frame(self.right)
        self.list_frame.pack(side="top", fill="x")

        self.list_label = tk.Label(self.list_frame, text="보고서 목록")
        self.list_label.pack(anchor="nw", padx=6, pady=(6, 0))

        self.report_listbox = tk.Listbox(self.list_frame, height=6)
        self.report_listbox.pack(side="left", fill="x", expand=True, padx=(6,0), pady=6)
        self.list_scroll = tk.Scrollbar(self.list_frame, command=self.report_listbox.yview)
        self.list_scroll.pack(side="left", fill="y", pady=6)
        self.report_listbox.config(yscrollcommand=self.list_scroll.set)
        self.report_listbox.bind("<<ListboxSelect>>", self.on_report_select)

        btns_frame = tk.Frame(self.list_frame)
        btns_frame.pack(side="left", padx=6)
        self.new_btn = tk.Button(btns_frame, text="새 보고서", command=self.new_report)
        self.new_btn.pack(fill="x")
        self.del_btn = tk.Button(btns_frame, text="삭제", command=self.delete_report)
        self.del_btn.pack(fill="x", pady=(6,0))

        # Bottom: input area (category/location/attendees/text/save)
        self.input_frame = tk.Frame(self.right)
        self.input_frame.pack(side="top", fill="both", expand=True)

        # Category
        self.cat_label = tk.Label(self.input_frame, text="카테고리")
        self.cat_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.cat_entry = ttk.Combobox(self.input_frame, values=self.store.list_categories(), state='normal')
        self.cat_entry.pack(fill="x", padx=6)

        # Location
        self.loc_label = tk.Label(self.input_frame, text="장소")
        self.loc_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.loc_entry = tk.Entry(self.input_frame)
        self.loc_entry.pack(fill="x", padx=6)

        # Attendees
        self.att_label = tk.Label(self.input_frame, text="참석자")
        self.att_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.att_entry = tk.Entry(self.input_frame)
        self.att_entry.pack(fill="x", padx=6)

        # Main text area
        self.att_label = tk.Label(self.input_frame, text="보고서 내용")
        self.att_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.text = tk.Text(self.input_frame, height=10)
        self.text.pack(fill="both", expand=True, padx=6, pady=6)

        # Save button
        self.btn = tk.Button(self.input_frame, text="보고서 저장", command=self.save_report)
        self.btn.pack(padx=6, pady=(0,6))

        # track current selected report index for the date
        self.current_index = None

    def on_date_select(self, event):
        date = self.cal.get_date()
        # refresh report list for selected date
        self.refresh_report_list(date)

        # clear selection and fields
        self.current_index = None
        self.clear_inputs()
        # if there are reports, select the first
        if self.store.has_reports(date):
            self.report_listbox.selection_set(0)
            self.report_listbox.event_generate("<<ListboxSelect>>")

    def save_report(self):
        date = self.cal.get_date()
        content = self.text.get("1.0", tk.END).strip()
        category = self.cat_entry.get().strip()
        location = self.loc_entry.get().strip()
        attendees = self.att_entry.get().strip()

        report = {
            "content": content,
            "category": category,
            "location": location,
            "attendees": attendees,
        }

        if self.current_index is None:
            # create new report for this date
            self.current_index = self.store.add_report(date, report)
        else:
            # update existing
            self.store.update_report(date, self.current_index, report)

        # refresh list and keep selection
        self.refresh_report_list(date)
        self.report_listbox.selection_clear(0, tk.END)
        self.report_listbox.selection_set(self.current_index)
        self.report_listbox.see(self.current_index)

        # refresh combobox values
        self.cat_entry['values'] = self.store.list_categories()
        self.cal.calevent_create(date, "memo", "memo")
        self.cal.tag_config("memo", background="#FFD966")

    def run(self):
        self.root.mainloop()

    # helper methods for list management
    def refresh_report_list(self, date):
        self.report_listbox.delete(0, tk.END)
        reports = self.store.list_reports(date)
        for i, r in enumerate(reports):
            preview = r.get("content", "").splitlines()[0][:40]
            label = f"{i+1}. [{r.get('category','')}] {preview}"
            self.report_listbox.insert(tk.END, label)

    def on_report_select(self, event):
        sel = self.report_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        self.current_index = index
        date = self.cal.get_date()
        try:
            r = self.store.get_report(date, index)
        except Exception:
            return
        # populate inputs
        self.cat_entry['values'] = self.store.list_categories()
        self.cat_entry.set(r.get("category", ""))
        self.loc_entry.delete(0, tk.END)
        self.loc_entry.insert(0, r.get("location", ""))
        self.att_entry.delete(0, tk.END)
        self.att_entry.insert(0, r.get("attendees", ""))
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, r.get("content", ""))

    def new_report(self):
        date = self.cal.get_date()
        self.current_index = self.store.add_report(date, None)
        self.refresh_report_list(date)
        self.report_listbox.selection_clear(0, tk.END)
        self.report_listbox.selection_set(self.current_index)
        self.report_listbox.event_generate("<<ListboxSelect>>")

    def delete_report(self):
        date = self.cal.get_date()
        sel = self.report_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.store.delete_report(date, idx)
        self.refresh_report_list(date)
        self.current_index = None
        self.clear_inputs()

    def clear_inputs(self):
        self.cat_entry.set("")
        self.loc_entry.delete(0, tk.END)
        self.att_entry.delete(0, tk.END)
        self.text.delete("1.0", tk.END)


if __name__ == "__main__":
    app = ReportApp()
    app.run()