import tkinter as tk
from tkcalendar import Calendar


class ReportStore:
    def __init__(self):
        self._reports_main = {}
        self._categories = {}
        self._location = {}
        self._attendees = {}

    def has_main(self, date):
        return date in self._reports_main

    def get_main(self, date):
        return self._reports_main.get(date, "")

    def save_main(self, date, text):
        self._reports_main[date] = text
    
    def save_category(self, date, category):
        self._categories[date] = category

    def get_category(self, date):
        return self._categories.get(date)

    def save_location(self, date, location):
        self._location[date] = location
    
    def get_location(self, date):
        return self._location.get(date)
    
    def save_attendees(self, date, attendees):
        self._attendees[date] = attendees

    def get_attendees(self, date):
        return self._attendees.get(date)


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
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

        self.right = tk.Frame(self.root)
        self.right.pack(side="right", fill="both", expand=True)

        # Category
        self.cat_label = tk.Label(self.right, text="카테고리")
        self.cat_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.cat_entry = tk.Entry(self.right)
        self.cat_entry.pack(fill="x", padx=6)

        # Location
        self.loc_label = tk.Label(self.right, text="장소")
        self.loc_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.loc_entry = tk.Entry(self.right)
        self.loc_entry.pack(fill="x", padx=6)

        # Attendees
        self.att_label = tk.Label(self.right, text="참석자")
        self.att_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.att_entry = tk.Entry(self.right)
        self.att_entry.pack(fill="x", padx=6)

        # Main text area
        self.att_label = tk.Label(self.right, text="보고서 내용")
        self.att_label.pack(anchor="nw", padx=6, pady=(6, 0))
        self.text = tk.Text(self.right, height=10)
        self.text.pack(fill="both", expand=True, padx=6, pady=6)

        # Save button
        self.btn = tk.Button(self.right, text="보고서 저장", command=self.save_report)
        self.btn.pack(padx=6, pady=(0,6))

    def on_date_select(self, event):
        date = self.cal.get_date()
        self.text.delete("1.0", tk.END)
        # populate main text
        if self.store.has_main(date):
            self.text.insert(tk.END, self.store.get_main(date))

        # populate category, location, attendees
        cat = self.store.get_category(date) or ""
        loc = self.store.get_location(date) or ""
        att = self.store.get_attendees(date) or ""

        self.cat_entry.delete(0, tk.END)
        self.cat_entry.insert(0, cat)

        self.loc_entry.delete(0, tk.END)
        self.loc_entry.insert(0, loc)

        self.att_entry.delete(0, tk.END)
        self.att_entry.insert(0, att)

    def save_report(self):
        date = self.cal.get_date()
        content = self.text.get("1.0", tk.END).strip()
        self.store.save_main(date, content)
        # save additional fields
        category = self.cat_entry.get().strip()
        location = self.loc_entry.get().strip()
        attendees = self.att_entry.get().strip()

        if category:
            self.store.save_category(date, category)
        if location:
            self.store.save_location(date, location)
        if attendees:
            self.store.save_attendees(date, attendees)
        self.cal.calevent_create(date, "memo", "memo")
        self.cal.tag_config("memo", background="#FFD966")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ReportApp()
    app.run()