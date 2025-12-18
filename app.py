import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime

import report_store
from tabs import ReportTab, SearchTab, StatisticsTab, SettingsTab


class ReportApp:
    def __init__(self):
        self.store = report_store.ReportStore()
        self.root = tk.Tk()
        self.root.geometry("1200x500")

        # top toolbar (above tabs and calendar)
        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(side="top", fill="x")
        # top toolbar (kept for future controls). Today button moved to calendar bottom-left.

        # left container for calendar + controls
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.cal = Calendar(
            self.left_frame,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            firstweekday="sunday",
            showweeknumbers=False
        )
        self.cal.pack(fill="both", expand=True)

        # bottom bar inside left_frame for controls (Today 버튼을 왼쪽 하단에 배치)
        self.left_bottom_bar = tk.Frame(self.left_frame)
        self.left_bottom_bar.pack(side="bottom", fill="x")
        try:
            tb_today = tk.Button(self.left_bottom_bar, text="오늘", command=self.go_to_today)
            tb_today.pack(side="left", padx=6, pady=6)
        except Exception:
            pass

        # highlight this week and following weeks
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")

        # tag for this week (Mon-Fri) - shaded background
        monday = today - datetime.timedelta(days=today.weekday())
        for i in range(5):
            d = monday + datetime.timedelta(days=i)
            try:
                self.cal.calevent_create(d, "week", "thisweek")
            except Exception:
                self.cal.calevent_create(d.strftime("%Y-%m-%d"), "week", "thisweek")
        self.cal.tag_config("thisweek", background="#E6E6E6")

        # next week (Mon-Fri) - light blue
        next_monday = monday + datetime.timedelta(days=7)
        for i in range(5):
            d = next_monday + datetime.timedelta(days=i)
            try:
                self.cal.calevent_create(d, "week_next", "nextweek")
            except Exception:
                self.cal.calevent_create(d.strftime("%Y-%m-%d"), "week_next", "nextweek")
        self.cal.tag_config("nextweek", background="#7FBFFF", foreground="#7FBFFF")

        # week after next (Mon-Fri) - deeper blue
        nextnext_monday = monday + datetime.timedelta(days=14)
        for i in range(5):
            d = nextnext_monday + datetime.timedelta(days=i)
            try:
                self.cal.calevent_create(d, "week_nextnext", "nextnextweek")
            except Exception:
                self.cal.calevent_create(d.strftime("%Y-%m-%d"), "week_nextnext", "nextnextweek")
        self.cal.tag_config("nextnextweek", background="#3F8BFF", foreground="#3F8BFF")

        # tag for today (yellow text, adjusted for contrast)
        try:
            self.cal.calevent_create(today, "today", "today")
        except Exception:
            self.cal.calevent_create(today_str, "today", "today")
        self.cal.tag_config("today", foreground="#FFAA00")

        # make selected day visually distinct: red text only (no background change)
        try:
            self.cal.configure(selectforeground="#FF0000")
        except Exception:
            pass
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

        # Notebook (tabs) for the right side
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side="right", fill="both", expand=True)

        # Initialize tab instances
        self.report_tab_obj = ReportTab(self.notebook, self.store)
        self.search_tab_obj = SearchTab(self.notebook, self.store)
        self.statistics_tab_obj = StatisticsTab(self.notebook, self.store)
        self.settings_tab_obj = SettingsTab(self.notebook, self.store)

        # Add tabs to notebook
        self.notebook.add(self.report_tab_obj.get_frame(), text="개인보고서")
        self.notebook.add(self.search_tab_obj.get_frame(), text="검색")
        self.notebook.add(self.statistics_tab_obj.get_frame(), text="통계")
        self.notebook.add(self.settings_tab_obj.get_frame(), text="설정")

        # keyboard shortcuts: 't' and Ctrl+T
        try:
            self.root.bind('<Key-t>', lambda e: self.go_to_today())
            self.root.bind('<Control-t>', lambda e: self.go_to_today())
        except Exception:
            pass

    def on_date_select(self, event):
        date = self.cal.get_date()
        # update report tab with selected date
        self.report_tab_obj.set_date(date)

    def go_to_today(self):
        today = datetime.date.today()
        # attempt to set selection; support both date object and string
        try:
            self.cal.selection_set(today)
        except Exception:
            try:
                self.cal.selection_set(today.strftime("%Y-%m-%d"))
            except Exception:
                pass
        # trigger tab update
        try:
            self.report_tab_obj.set_date(today.strftime("%Y-%m-%d"))
        except Exception:
            pass

    def run(self):
        self.root.mainloop()
        # 프로그램 종료 시 JSON 저장
        self.store.save_to_json()

    # Deprecated methods kept for backward compatibility if needed
    def save_report(self):
        pass

    def refresh_report_list(self, date):
        pass

    def on_report_select(self, event):
        pass

    def new_report(self):
        pass

    def delete_report(self):
        pass

    def clear_inputs(self):
        pass
