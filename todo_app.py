import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime

class TodoApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Планировщик задач")
        self.window.geometry("700x700")
        self.window.configure(bg='#f0f0f0')
        
        self.tasks = self.load_tasks()
        self.current_filter = "Все"
        self.sort_by = "priority"
        self.selected_task = None
        
        self.setup_styles()
        self.create_widgets()
        self.update_task_list()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TLabelframe', background='#f0f0f0', font=('Arial', 10, 'bold'))
        self.style.configure('TLabelframe.Label', background='#f0f0f0', font=('Arial', 10, 'bold'))
        self.style.configure('TButton', font=('Arial', 9))
        self.style.configure('TEntry', font=('Arial', 10))
    
    def load_tasks(self):
        try:
            if getattr(sys, 'frozen', False):
                app_dir = os.path.join(os.environ['USERPROFILE'], 'Documents', 'TodoApp')
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            os.makedirs(app_dir, exist_ok=True)
            self.data_file = os.path.join(app_dir, 'tasks.json')
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_tasks(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.window, text="ПЛАНИРОВЩИК ЗАДАЧ",
                        font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2e7d32')
        title.pack(pady=10)
        
        # Дата
        self.date_label = tk.Label(self.window, text="", font=('Arial', 9),
                                  bg='#f0f0f0', fg='#666666')
        self.date_label.pack()
        self.update_date()
        
        # Добавление задачи
        add_frame = tk.LabelFrame(self.window, text="Добавить задачу",
                                 bg='white', fg='#333333', padx=10, pady=10)
        add_frame.pack(fill='x', padx=20, pady=10)
        
        # Текст задачи
        row1 = tk.Frame(add_frame, bg='white')
        row1.pack(fill='x', pady=(0, 5))
        tk.Label(row1, text="Задача:", bg='white').pack(side='left')
        self.task_entry = tk.Entry(row1, font=('Arial', 11), relief='solid', bd=1)
        self.task_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        # Приоритет, категория, срок
        row2 = tk.Frame(add_frame, bg='white')
        row2.pack(fill='x')
        
        tk.Label(row2, text="Приоритет:", bg='white').pack(side='left')
        self.priority_var = tk.StringVar(value="Средний")
        p = ttk.Combobox(row2, textvariable=self.priority_var,
                        values=["Высокий", "Средний", "Низкий"],
                        state='readonly', width=10)
        p.pack(side='left', padx=(5, 15))
        
        tk.Label(row2, text="Категория:", bg='white').pack(side='left')
        self.cat_var = tk.StringVar(value="Общее")
        c = ttk.Combobox(row2, textvariable=self.cat_var,
                        values=["Общее", "Работа", "Личное", "Учеба", "Здоровье", "Покупки"],
                        state='readonly', width=10)
        c.pack(side='left', padx=(5, 15))
        
        tk.Label(row2, text="Срок:", bg='white').pack(side='left')
        self.deadline_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        d = tk.Entry(row2, textvariable=self.deadline_var, width=12,
                    font=('Arial', 10), relief='solid', bd=1)
        d.pack(side='left', padx=(5, 0))
        
        tk.Button(row2, text="Добавить", command=self.add_task,
                 bg='#4CAF50', fg='white', relief='flat',
                 font=('Arial', 9, 'bold'), padx=15).pack(side='right')
        
        # Фильтры
        filter_frame = tk.Frame(self.window, bg='#f0f0f0')
        filter_frame.pack(fill='x', padx=20, pady=(0, 5))
        
        for text in ["Все", "Активные", "Выполненные"]:
            tk.Button(filter_frame, text=text,
                     command=lambda t=text: self.set_filter(t),
                     relief='flat', padx=10, pady=3,
                     bg='#e0e0e0', font=('Arial', 9)).pack(side='left', padx=2)
        
        tk.Button(filter_frame, text="По приоритету",
                 command=lambda: self.set_sort("priority"),
                 relief='flat', padx=10, pady=3,
                 bg='#e0e0e0', font=('Arial', 9)).pack(side='right', padx=2)
        tk.Button(filter_frame, text="По дате",
                 command=lambda: self.set_sort("date"),
                 relief='flat', padx=10, pady=3,
                 bg='#e0e0e0', font=('Arial', 9)).pack(side='right', padx=2)
        
        # Список задач
        list_frame = tk.LabelFrame(self.window, text="Список задач",
                                  bg='white', padx=5, pady=5)
        list_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        canvas = tk.Canvas(list_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
        self.task_frame = tk.Frame(canvas, bg='white')
        self.task_frame.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.task_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(
            int(-1*(e.delta/120)), 'units'))
        
        # Кнопки действий
        btn_frame = tk.Frame(self.window, bg='#f0f0f0')
        btn_frame.pack(fill='x', padx=20, pady=5)
        
        actions = [
            ("Выполнить", '#4CAF50', self.toggle_selected),
            ("Изменить", '#2196F3', self.edit_selected),
            ("Удалить", '#f44336', self.delete_selected),
        ]
        for text, color, cmd in actions:
            tk.Button(btn_frame, text=text, command=cmd,
                     bg=color, fg='white', relief='flat',
                     font=('Arial', 9), padx=10).pack(side='left', padx=2)
        
        # Статистика
        self.stats_label = tk.Label(self.window, text="",
                                   bg='#e8e8e8', fg='#333333',
                                   font=('Arial', 9), pady=8)
        self.stats_label.pack(fill='x', padx=20, pady=5)
        
        self.progress = ttk.Progressbar(self.window, length=660, mode='determinate')
        self.progress.pack(padx=20, pady=(0, 10))
    
    def update_date(self):
        now = datetime.now()
        days = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}
        self.date_label.config(
            text=f"{days[now.weekday()]}, {now.strftime('%d.%m.%Y %H:%M')}")
        self.window.after(60000, self.update_date)
    
    def add_task(self):
        text = self.task_entry.get().strip()
        if not text:
            messagebox.showwarning("Ошибка", "Введите текст задачи!")
            return
        try:
            datetime.strptime(self.deadline_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return
        self.tasks.append({
            "id": datetime.now().timestamp(),
            "text": text,
            "priority": self.priority_var.get(),
            "category": self.cat_var.get(),
            "deadline": self.deadline_var.get(),
            "completed": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        self.save_tasks()
        self.task_entry.delete(0, 'end')
        self.update_task_list()
    
    def set_filter(self, f):
        self.current_filter = f
        self.update_task_list()
    
    def set_sort(self, s):
        self.sort_by = s
        self.update_task_list()
    
    def get_filtered(self):
        tasks = self.tasks.copy()
        if self.current_filter == "Активные":
            tasks = [t for t in tasks if not t['completed']]
        elif self.current_filter == "Выполненные":
            tasks = [t for t in tasks if t['completed']]
        if self.sort_by == "priority":
            order = {"Высокий": 0, "Средний": 1, "Низкий": 2}
            tasks.sort(key=lambda x: order.get(x['priority'], 3))
        else:
            tasks.sort(key=lambda x: x['deadline'])
        return tasks
    
    def update_task_list(self):
        for w in self.task_frame.winfo_children():
            w.destroy()
        tasks = self.get_filtered()
        if not tasks:
            tk.Label(self.task_frame, text="Задач нет",
                    bg='white', fg='#999').pack(pady=20)
        for task in tasks:
            self.create_task_row(task)
        self.update_stats()
    
    def create_task_row(self, task):
        overdue = (not task['completed'] and
                  task['deadline'] < datetime.now().strftime('%Y-%m-%d'))
        bg = '#fff0f0' if overdue else 'white'
        row = tk.Frame(self.task_frame, bg=bg, relief='solid', bd=1)
        row.pack(fill='x', pady=1, padx=2)
        
        var = tk.BooleanVar(value=task['completed'])
        cb = tk.Checkbutton(row, variable=var,
                           command=lambda t=task, v=var: self.toggle(t, v),
                           bg=bg, activebackground=bg)
        cb.pack(side='left', padx=5)
        
        symbols = {"Высокий": "🔴", "Средний": "🟡", "Низкий": "🟢"}
        color = '#aaa' if task['completed'] else ('red' if overdue else '#333')
        font = ('Arial', 10, 'overstrike') if task['completed'] else ('Arial', 10)
        txt = f"{symbols.get(task['priority'], '')} {task['text']}"
        if overdue:
            txt += ' ⚠'
        
        lbl = tk.Label(row, text=txt, bg=bg, fg=color, font=font, anchor='w')
        lbl.pack(side='left', fill='x', expand=True, padx=5)
        
        cat_lbl = tk.Label(row, text=f"[{task['category']}]",
                          bg=bg, fg='#888', font=('Arial', 8))
        cat_lbl.pack(side='left', padx=5)
        
        dl = tk.Label(row, text=f"📅 {task['deadline']}",
                     bg=bg, fg='#2196F3', font=('Arial', 8))
        dl.pack(side='right', padx=5)
        
        for w in (row, lbl, cat_lbl, dl):
            w.bind('<Button-1>', lambda e, t=task, r=row: self.select(t, r))
    
    def select(self, task, row):
        self.selected_task = task
        for w in self.task_frame.winfo_children():
            w.configure(bg='white')
            for c in w.winfo_children():
                try: c.configure(bg='white')
                except: pass
        row.configure(bg='#d0e8ff')
        for c in row.winfo_children():
            try: c.configure(bg='#d0e8ff')
            except: pass
    
    def toggle(self, task, var):
        task['completed'] = var.get()
        self.save_tasks()
        self.update_task_list()
    
    def toggle_selected(self):
        if self.selected_task:
            self.selected_task['completed'] = not self.selected_task['completed']
            self.save_tasks()
            self.update_task_list()
        else:
            messagebox.showinfo("Инфо", "Выберите задачу в списке!")
    
    def edit_selected(self):
        if not self.selected_task:
            messagebox.showinfo("Инфо", "Выберите задачу!")
            return
        t = self.selected_task
        win = tk.Toplevel(self.window)
        win.title("Изменить")
        win.geometry("350x200")
        win.configure(bg='white')
        win.transient(self.window)
        win.grab_set()
        tk.Label(win, text="Текст:", bg='white').pack(pady=(10, 0))
        e = tk.Entry(win, width=40)
        e.insert(0, t['text'])
        e.pack(pady=5)
        tk.Label(win, text="Срок:", bg='white').pack()
        d = tk.Entry(win, width=15)
        d.insert(0, t['deadline'])
        d.pack(pady=5)
        def save():
            t['text'] = e.get().strip()
            t['deadline'] = d.get()
            self.save_tasks()
            self.update_task_list()
            win.destroy()
        tk.Button(win, text="Сохранить", command=save,
                 bg='#4CAF50', fg='white').pack(pady=10)
    
    def delete_selected(self):
        if not self.selected_task:
            messagebox.showinfo("Инфо", "Выберите задачу!")
            return
        if messagebox.askyesno("Удалить?", f"Удалить '{self.selected_task['text']}'?"):
            self.tasks.remove(self.selected_task)
            self.selected_task = None
            self.save_tasks()
            self.update_task_list()
    
    def update_stats(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t['completed'])
        overdue = sum(1 for t in self.tasks
                     if not t['completed']
                     and t['deadline'] < datetime.now().strftime('%Y-%m-%d'))
        self.stats_label.config(
            text=f"Всего: {total}  |  Выполнено: {done}  |  Активных: {total-done}"
                 + (f"  |  Просрочено: {overdue}" if overdue else ""))
        self.progress['value'] = (done / total * 100) if total > 0 else 0
    
    def on_closing(self):
        self.save_tasks()
        self.window.destroy()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    TodoApp().run()