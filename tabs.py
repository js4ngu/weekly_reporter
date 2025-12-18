import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime


class ReportTab:
    """보고서 입력/관리 탭"""
    def __init__(self, parent, store):
        self.store = store
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.current_index = None
        self.current_date = None
        self._build_ui()

    def _build_ui(self):
        # Top: report list for the selected date (compact)
        self.list_frame = tk.Frame(self.frame)
        self.list_frame.pack(side="top", fill="x", expand=False)

        self.list_label = tk.Label(self.list_frame, text="보고서 목록")
        self.list_label.pack(anchor="nw", padx=6, pady=(6, 0))

        self.report_listbox = tk.Listbox(self.list_frame, height=3)
        self.report_listbox.pack(side="left", fill="both", expand=True, padx=(6,0), pady=6)
        self.list_scroll = tk.Scrollbar(self.list_frame, command=self.report_listbox.yview)
        self.list_scroll.pack(side="left", fill="y", pady=6)
        self.report_listbox.config(yscrollcommand=self.list_scroll.set)
        self.report_listbox.bind("<<ListboxSelect>>", self.on_report_select)

        btns_frame = tk.Frame(self.list_frame)
        btns_frame.pack(side="left", padx=6)
        self.new_btn = tk.Button(btns_frame, text="새보고서 작성", command=self.create_new_report)
        self.new_btn.pack(fill="x")
        self.save_btn = tk.Button(btns_frame, text="보고서 저장", command=self.save_report)
        self.save_btn.pack(fill="x", pady=(6,0))
        self.del_btn = tk.Button(btns_frame, text="보고서 삭제", command=self.delete_report, state='disabled')
        self.del_btn.pack(fill="x", pady=(6,0))

        # Bottom: input area (category/location/attendees/text/save)
        self.input_frame = tk.Frame(self.frame)
        self.input_frame.pack(side="top", fill="both", expand=True)

        # Date with calendar picker
        self.date_label = tk.Label(self.input_frame, text="날짜")
        self.date_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.date_entry = tk.Entry(self.input_frame, width=20)
        self.date_entry.pack(fill="x", padx=6)
        # 기본값: 오늘 날짜
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

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
        self.text = tk.Text(self.input_frame, height=5)
        self.text.pack(fill="both", expand=True, padx=6, pady=6)

    def get_frame(self):
        """탭에 추가될 프레임 반환"""
        return self.frame

    def set_date(self, date):
        """날짜 선택 시 보고서 목록 새로고침"""
        self.current_date = date
        # Entry에 직접 입력
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date)
        self.refresh_report_list(date)
        self.current_index = None
        self.clear_inputs()
        self.report_listbox.selection_clear(0, tk.END)
        self.del_btn.config(state='disabled')
        if self.store.has_reports(date):
            self.report_listbox.selection_set(0)
            self.report_listbox.event_generate("<<ListboxSelect>>")
        self.current_index = None
        self.clear_inputs()
        self.report_listbox.selection_clear(0, tk.END)
        self.del_btn.config(state='disabled')
        if self.store.has_reports(date):
            self.report_listbox.selection_set(0)
            self.report_listbox.event_generate("<<ListboxSelect>>")

    def save_report(self):
        new_date = self.date_entry.get().strip()
        if not new_date:
            return

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
            # 새 보고서 추가
            self.current_index = self.store.add_report(new_date, report)
        else:
            # 보고서 수정 - 날짜가 변경되었으면 이동, 아니면 업데이트
            old_date = self.current_date
            if old_date != new_date:
                # 날짜 변경: 기존 날짜에서 삭제, 새 날짜에 추가
                self.current_index = self.store.move_report(old_date, new_date, self.current_index, report)
                self.current_date = new_date
            else:
                # 같은 날짜: 그냥 업데이트
                self.store.update_report(new_date, self.current_index, report)

        self.refresh_report_list(new_date)
        self.report_listbox.selection_clear(0, tk.END)
        self.report_listbox.selection_set(self.current_index)
        self.report_listbox.see(self.current_index)

        self.cat_entry['values'] = self.store.list_categories()
        
        # JSON 파일에 저장
        self.store.save_to_json()

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
            self.del_btn.config(state='disabled')
            return
        index = sel[0]
        self.current_index = index
        date = self.date_entry.get().strip()
        if not date:
            return

        # 현재 날짜 저장 (나중에 수정할 때 이전 날짜와 비교하기 위함)
        self.current_date = date

        try:
            r = self.store.get_report(date, index)
        except Exception:
            return

        self.cat_entry['values'] = self.store.list_categories()
        self.cat_entry.set(r.get("category", ""))
        self.loc_entry.delete(0, tk.END)
        self.loc_entry.insert(0, r.get("location", ""))
        self.att_entry.delete(0, tk.END)
        self.att_entry.insert(0, r.get("attendees", ""))
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, r.get("content", ""))
        
        # Enable delete button
        self.del_btn.config(state='normal')

    def load_for_edit(self):
        """보고서 수정 모드 진입 (폼에 이미 로드됨)"""
        # 현재 폼이 이미 선택된 보고서로 로드됨
        # 여기서는 특별한 처리 필요 없음 (이미 on_report_select에서 로드됨)
        pass

    def new_report(self):
        date = self.date_entry.get_date().strftime("%Y-%m-%d")
        if not date:
            return

        self.current_index = self.store.add_report(date, None)
        self.refresh_report_list(date)
        self.report_listbox.selection_clear(0, tk.END)
        self.report_listbox.selection_set(self.current_index)
        self.report_listbox.event_generate("<<ListboxSelect>>")

    def create_new_report(self):
        """새로운 빈 보고서 폼 생성"""
        # 현재 날짜가 설정되지 않았으면 오늘 날짜로 설정
        current_date = self.date_entry.get().strip()
        if not current_date:
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, today)
            self.current_date = today
        else:
            self.current_date = current_date
        
        self.current_index = None
        self.clear_inputs()
        self.report_listbox.selection_clear(0, tk.END)
        self.del_btn.config(state='disabled')

    def delete_report(self):
        date = self.date_entry.get().strip()
        if not date:
            return

        sel = self.report_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.store.delete_report(date, idx)
        self.refresh_report_list(date)
        self.current_index = None
        self.clear_inputs()
        self.del_btn.config(state='disabled')
        
        # JSON 파일에 저장
        self.store.save_to_json()

    def clear_inputs(self):
        self.cat_entry.set("")
        self.loc_entry.delete(0, tk.END)
        self.att_entry.delete(0, tk.END)
        self.text.delete("1.0", tk.END)


class SearchTab:
    """검색 탭"""
    def __init__(self, parent, store):
        self.store = store
        self.parent = parent
        self.frame = tk.Frame(parent)
        self._build_ui()

    def _build_ui(self):
        label = tk.Label(self.frame, text="검색 기능 (준비 중)", font=("Arial", 14))
        label.pack(expand=True)

    def get_frame(self):
        return self.frame


class StatisticsTab:
    """통계 탭"""
    def __init__(self, parent, store):
        self.store = store
        self.parent = parent
        self.frame = tk.Frame(parent)
        self._build_ui()

    def _build_ui(self):
        label = tk.Label(self.frame, text="통계 분석 (준비 중)", font=("Arial", 14))
        label.pack(expand=True)

    def get_frame(self):
        return self.frame


class SettingsTab:
    """설정 탭"""
    def __init__(self, parent, store):
        self.store = store
        self.parent = parent
        self.frame = tk.Frame(parent)
        self._build_ui()

    def _build_ui(self):
        label = tk.Label(self.frame, text="설정 (준비 중)", font=("Arial", 14))
        label.pack(expand=True)

    def get_frame(self):
        return self.frame
