import tkinter as tk
from tkcalendar import Calendar


class ReportStore:
    def __init__(self):
        self._reports_main = {}
        self._categories = {}
        self._location = {}
        self._attendees = {}

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

        self.text = tk.Text(self.right, height=10)
        self.text.pack(fill="both", expand=True)

        self.btn = tk.Button(self.right, text="보고서 저장", command=self.save_report)
        self.btn.pack()

    def on_date_select(self, event):
        date = self.cal.get_date()
        self.text.delete("1.0", tk.END)
        if self.store.has_main(date):
            self.text.insert(tk.END, self.store.get_main(date))
            
    def save_report(self):
        date = self.cal.get_date()
        content = self.text.get("1.0", tk.END).strip()
        self.store.save(date, content)
        self.cal.calevent_create(date, "memo", "memo")
        self.cal.tag_config("memo", background="#FFD966")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ReportApp()
    app.run()