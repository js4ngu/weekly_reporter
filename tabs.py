import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime


class PersonalTab:
    """개인업무 입력/관리 탭 (이전 ReportTab)"""
    def __init__(self, parent, store, owner="personal"):
        self.store = store
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.owner = owner
        self.current_index = None
        self.current_orig_date = None
        self.current_date = None
        self._visible_reports = []  # list of (owner, orig_date, idx)
        self._build_ui()

    def _build_ui(self):
        # Top: report list for the selected date (compact)
        self.list_frame = tk.Frame(self.frame)
        self.list_frame.pack(side="top", fill="x", expand=False)

        # label text depends on owner (personal/shared)
        label_text = "보고서 목록"
        try:
            if getattr(self, 'owner', None) == 'shared':
                label_text = "공통업무 목록"
            elif getattr(self, 'owner', None) == 'personal':
                label_text = "개인업무 목록"
        except Exception:
            label_text = "보고서 목록"
        self.list_label = tk.Label(self.list_frame, text=label_text)
        self.list_label.pack(anchor="nw", padx=6, pady=(6, 0))

        self.report_listbox = tk.Listbox(self.list_frame, height=3)
        self.report_listbox.pack(side="left", fill="both", expand=True, padx=(6,0), pady=6)
        self.list_scroll = tk.Scrollbar(self.list_frame, command=self.report_listbox.yview)
        self.list_scroll.pack(side="left", fill="y", pady=6)
        self.report_listbox.config(yscrollcommand=self.list_scroll.set)
        self.report_listbox.bind("<<ListboxSelect>>", self.on_report_select)

        btns_frame = tk.Frame(self.list_frame)
        btns_frame.pack(side="left", padx=6)
        self.new_btn = tk.Button(btns_frame, text="새업무", command=self.create_new_report)
        self.new_btn.pack(fill="x")
        self.save_btn = tk.Button(btns_frame, text="업무저장", command=self.save_report)
        self.save_btn.pack(fill="x", pady=(6,0))
        self.del_btn = tk.Button(btns_frame, text="업무삭제", command=self.delete_report, state='disabled')
        self.del_btn.pack(fill="x", pady=(6,0))

        # Bottom: input area (category/location/attendees/text/save)
        self.input_frame = tk.Frame(self.frame)
        self.input_frame.pack(side="top", fill="both", expand=True)

        # NOTE: single-period input handled below (start_entry / optional end_entry)

        # Period: start_date ~ end_date with checkbox to enable end_date
        time_frame = tk.Frame(self.input_frame)
        time_frame.pack(anchor="nw", fill="x", padx=6, pady=(6, 0))
        time_label = tk.Label(time_frame, text="기간 (YYYY-MM-DD)")
        time_label.pack(side="left")
        self.start_entry = tk.Entry(time_frame, width=12)
        self.start_entry.pack(side="left", padx=(6, 0))
        tilde = tk.Label(time_frame, text=" ~ ")
        tilde.pack(side="left")
        self.end_entry = tk.Entry(time_frame, width=12, state='disabled')
        self.end_entry.pack(side="left")
        self.end_var = tk.BooleanVar(value=False)
        self.end_check = tk.Checkbutton(time_frame, text="종료일 사용", variable=self.end_var, command=self._toggle_end)
        self.end_check.pack(side="left", padx=6)

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
        # Set period start to selected date and refresh list
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, date)
        self.refresh_report_list(date)
        self.current_index = None
        self.clear_inputs()
        self.report_listbox.selection_clear(0, tk.END)
        self.del_btn.config(state='disabled')
        if self.store.has_reports(date, owner=self.owner):
            self.report_listbox.selection_set(0)
            self.report_listbox.event_generate("<<ListboxSelect>>")

    def _toggle_end(self):
        if self.end_var.get():
            # enable end entry and default it to start value if empty
            self.end_entry.config(state='normal')
            try:
                start_val = self.start_entry.get().strip()
            except Exception:
                start_val = ''
            if not self.end_entry.get().strip():
                if start_val:
                    self.end_entry.delete(0, tk.END)
                    self.end_entry.insert(0, start_val)
        else:
            # keep start_entry intact; only clear end
            self.end_entry.delete(0, tk.END)
            self.end_entry.config(state='disabled')

    def save_report(self):
        selected_date = self.start_entry.get().strip()
        if not selected_date:
            return

        content = self.text.get("1.0", tk.END).strip()
        category = self.cat_entry.get().strip()
        location = self.loc_entry.get().strip()
        attendees = self.att_entry.get().strip()

        # determine start/end dates
        start_date = self.start_entry.get().strip() or selected_date
        end_date = self.end_entry.get().strip() if self.end_var.get() else start_date

        report = {
            "content": content,
            "category": category,
            "location": location,
            "attendees": attendees,
            "start_date": start_date,
            "end_date": end_date,
        }

        key_date = start_date

        if self.current_index is None:
            # 새 보고서 추가 (저장 키는 시작일)
            self.current_index = self.store.add_report(key_date, report, owner=self.owner)
            self.current_orig_date = key_date
        else:
            # 보고서 수정 - 실제로 저장된 원래 키(orig_date)를 사용
            old_date = self.current_orig_date or selected_date
            if old_date != key_date:
                # 날짜 변경: 기존 날짜에서 삭제, 새 날짜에 추가
                self.current_index = self.store.move_report(old_date, key_date, self.current_index, report, owner=self.owner)
                self.current_orig_date = key_date
            else:
                # 같은 원래 키: 업데이트
                self.store.update_report(key_date, self.current_index, report, owner=self.owner)

        # 새로고침 후, visible list에서 방금 저장된 항목의 인덱스를 찾아 선택
        self.refresh_report_list(selected_date)
        self.report_listbox.selection_clear(0, tk.END)
        sel_idx = None
        for i, (ow, orig, idx) in enumerate(self._visible_reports):
            if orig == (self.current_orig_date or key_date) and idx == self.current_index:
                sel_idx = i
                break
        if sel_idx is not None:
            self.report_listbox.selection_set(sel_idx)
            self.report_listbox.see(sel_idx)

        self.cat_entry['values'] = self.store.list_categories()
        
        # JSON 파일에 저장
        self.store.save_to_json()

    def refresh_report_list(self, date):
        self.report_listbox.delete(0, tk.END)
        found = self.store.find_reports_for_date(date, owner=self.owner)
        self._visible_reports = []
        for i, (ow, orig_date, idx, r) in enumerate(found):
            preview = r.get("content", "").splitlines()[0][:40]
            start = r.get("start_date", orig_date)
            end = r.get("end_date", start)
            if start == end:
                time_str = f"[{start}] "
            else:
                time_str = f"[{start}~{end}] "
            label = f"{i+1}. {time_str}[{r.get('category','')}] {preview}"
            self.report_listbox.insert(tk.END, label)
            self._visible_reports.append((ow, orig_date, idx))

    def on_report_select(self, event):
        sel = self.report_listbox.curselection()
        if not sel:
            self.del_btn.config(state='disabled')
            return
        index = sel[0]
        # map visible index -> (owner, orig_date, idx)
        try:
            ow, orig_date, orig_idx = self._visible_reports[index]
        except Exception:
            self.del_btn.config(state='disabled')
            return

        self.current_orig_date = orig_date
        self.current_index = orig_idx

        try:
            r = self.store.get_report(orig_date, orig_idx, owner=ow)
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
        # load period
        start = r.get("start_date", "")
        end = r.get("end_date", "")
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, start)
        if end and end != start:
            self.end_var.set(True)
            self.end_entry.config(state='normal')
            self.end_entry.delete(0, tk.END)
            self.end_entry.insert(0, end)
        else:
            self.end_var.set(False)
            self.end_entry.delete(0, tk.END)
            self.end_entry.config(state='disabled')
        
        # Enable delete button
        self.del_btn.config(state='normal')

    def load_for_edit(self):
        """보고서 수정 모드 진입 (폼에 이미 로드됨)"""
        # 현재 폼이 이미 선택된 보고서로 로드됨
        # 여기서는 특별한 처리 필요 없음 (이미 on_report_select에서 로드됨)
        pass

    def new_report(self):
        date = self.start_entry.get().strip()
        if not date:
            return

        # add empty report under the selected date
        self.current_index = self.store.add_report(date, {"content":"", "category":"", "location":"", "attendees":"", "start_date":date, "end_date":""}, owner=self.owner)
        self.current_orig_date = date
        self.refresh_report_list(date)
        self.report_listbox.selection_clear(0, tk.END)
        # select the last visible item if matches
        for i, (ow, orig, idx) in enumerate(self._visible_reports):
            if orig == self.current_orig_date and idx == self.current_index:
                self.report_listbox.selection_set(i)
                self.report_listbox.event_generate("<<ListboxSelect>>")
                break

    def create_new_report(self):
        """새로운 빈 보고서 폼 생성"""
        # 현재 날짜가 설정되지 않았으면 오늘 날짜로 설정
        current_date = self.start_entry.get().strip()
        if not current_date:
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.start_entry.delete(0, tk.END)
            self.start_entry.insert(0, today)
            self.current_date = today
        else:
            self.current_date = current_date
        
        self.current_index = None
        self.current_orig_date = None
        self.clear_inputs()
        self.report_listbox.selection_clear(0, tk.END)
        self.del_btn.config(state='disabled')

    def delete_report(self):
        sel = self.report_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        try:
            ow, orig_date, orig_idx = self._visible_reports[idx]
        except Exception:
            return
        self.store.delete_report(orig_date, orig_idx, owner=ow)
        self.refresh_report_list(self.start_entry.get().strip())
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
        # clear period inputs
        # default start date to selected date or today
        sel = self.start_entry.get().strip()
        if sel:
            self.start_entry.delete(0, tk.END)
            self.start_entry.insert(0, sel)
        else:
            self.start_entry.delete(0, tk.END)
            self.start_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.end_entry.delete(0, tk.END)
        self.end_entry.config(state='disabled')
        self.end_var.set(False)


class SharedTab(PersonalTab):
    """공통업무(Shared) 탭 — PersonalTab UI/동작을 공유합니다."""
    def __init__(self, parent, store):
        super().__init__(parent, store, owner="shared")


# 호환을 위해 CommonTab 별칭 유지
CommonTab = SharedTab


class WeeklyTab:
    """개인주간업무보고 탭 (이전 StatisticsTab)"""
    def __init__(self, parent, store):
        self.store = store
        self.parent = parent
        self.frame = tk.Frame(parent)
        self._build_ui()

    def _build_ui(self):
        label = tk.Label(self.frame, text="(준비 중)", font=("Arial", 14))
        label.pack(expand=True)

    def get_frame(self):
        return self.frame


class SpareTab:
    """예비 탭 (이전 SettingsTab)"""
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
