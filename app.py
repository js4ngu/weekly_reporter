import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime

import report_store
from tabs import PersonalTab, SharedTab, WeeklyTab, SpareTab


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

        # Initialize tab instances (named to match tab labels)
        self.personal_tab = PersonalTab(self.notebook, self.store)
        self.shared_tab = SharedTab(self.notebook, self.store)
        self.weekly_tab = WeeklyTab(self.notebook, self.store)
        self.spare_tab = SpareTab(self.notebook, self.store)

        # Add tabs to notebook (labels kept in Korean)
        self.notebook.add(self.personal_tab.get_frame(), text="개인업무")
        self.notebook.add(self.shared_tab.get_frame(), text="공통업무")
        self.notebook.add(self.weekly_tab.get_frame(), text="개인주간업무보고")
        self.notebook.add(self.spare_tab.get_frame(), text="예비")

        # keyboard shortcuts: 't' and Ctrl+T
        try:
            self.root.bind('<Key-t>', lambda e: self.go_to_today())
            self.root.bind('<Control-t>', lambda e: self.go_to_today())
        except Exception:
            pass

        # initialize tabs with today's date so shared/personal both have data loaded
        try:
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.personal_tab.set_date(today)
            self.shared_tab.set_date(today)
        except Exception:
            pass

    def on_date_select(self, event):
        date = self.cal.get_date()
        # update both personal and shared tabs with selected date
        try:
            self.personal_tab.set_date(date)
        except Exception:
            pass
        try:
            self.shared_tab.set_date(date)
        except Exception:
            pass

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
            self.personal_tab.set_date(today.strftime("%Y-%m-%d"))
            self.shared_tab.set_date(today.strftime("%Y-%m-%d"))
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
