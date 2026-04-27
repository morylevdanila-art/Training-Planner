import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ---------- Файл для хранения данных ----------
DATA_FILE = "workouts.json"


# ---------- Класс приложения ----------
class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        # Данные
        self.workouts = []
        self.load_data()

        # Типы тренировок для выпадающего списка
        self.workout_types = ["Бег", "Плавание", "Велосипед", "Йога", "Силовая", "Футбол", "Теннис", "Другое"]

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table()

        # Отобразить все тренировки
        self.refresh_table()

    # ---------- Загрузка / сохранение JSON ----------
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.workouts = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.workouts = []
        else:
            self.workouts = []

    def save_data(self):
        """Сохранение данных в JSON файл"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.workouts, f, ensure_ascii=False, indent=4)

    # ---------- Форма добавления тренировки ----------
    def create_input_frame(self):
        """Создание формы для добавления тренировок"""
        frame = tk.LabelFrame(self.root, text="Добавить тренировку", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = tk.Entry(frame, width=15, font=("Arial", 10))
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Подсказка с текущей датой

        # Тип тренировки
        tk.Label(frame, text="Тип тренировки:", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=self.workout_types, width=15,
                                       font=("Arial", 10))
        self.type_combo.grid(row=0, column=3, padx=5)
        self.type_combo.set("Выберите тип")

        # Длительность
        tk.Label(frame, text="Длительность (мин):", font=("Arial", 10)).grid(row=0, column=4, sticky="w", padx=5)
        self.duration_entry = tk.Entry(frame, width=10, font=("Arial", 10))
        self.duration_entry.grid(row=0, column=5, padx=5)

        # Кнопка добавления
        tk.Button(frame, text="➕ Добавить тренировку", command=self.add_workout,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10).grid(row=0, column=6, padx=20)

    # ---------- Проверка корректности ввода ----------
    def validate_date(self, date_str):
        """Проверка формата даты (ГГГГ-ММ-ДД)"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        """Проверка длительности (положительное число)"""
        try:
            duration = float(duration_str)
            if duration > 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def validate_workout_data(self, date, workout_type, duration_str):
        """Полная проверка всех полей"""
        if not date or not workout_type or not duration_str:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return False

        if workout_type == "Выберите тип":
            messagebox.showerror("Ошибка", "Выберите тип тренировки!")
            return False

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД (например, 2024-12-25)")
            return False

        if not self.validate_duration(duration_str):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом (в минутах)!")
            return False

        return True

    def add_workout(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        workout_type = self.type_var.get().strip()
        duration_str = self.duration_entry.get().strip()

        if not self.validate_workout_data(date, workout_type, duration_str):
            return

        duration = float(duration_str)

        workout = {
            "date": date,
            "type": workout_type,
            "duration": duration
        }

        self.workouts.append(workout)
        self.save_data()
        self.refresh_table()

        # Очистка полей (кроме даты - оставляем текущую)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_combo.set("Выберите тип")
        self.duration_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", "Тренировка добавлена!")

    # ---------- Фильтрация ----------
    def create_filter_frame(self):
        """Создание панели фильтрации"""
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Фильтр по типу:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(frame, textvariable=self.filter_type_var,
                                              values=["Все"] + self.workout_types, width=15, font=("Arial", 10))
        self.filter_type_combo.grid(row=0, column=1, padx=5)
        self.filter_type_combo.set("Все")

        tk.Label(frame, text="Фильтр по дате:", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.filter_date_entry = tk.Entry(frame, width=15, font=("Arial", 10))
        self.filter_date_entry.grid(row=0, column=3, padx=5)
        self.filter_date_entry.insert(0, "ГГГГ-ММ-ДД")

        # Очистка подсказки при клике
        def on_date_click(event):
            if self.filter_date_entry.get() == "ГГГГ-ММ-ДД":
                self.filter_date_entry.delete(0, tk.END)

        self.filter_date_entry.bind("<FocusIn>", on_date_click)

        tk.Button(frame, text="🔍 Применить фильтр", command=self.refresh_table,
                  bg="#2196F3", fg="white", font=("Arial", 10)).grid(row=0, column=4, padx=10)
        tk.Button(frame, text="❌ Сбросить фильтр", command=self.clear_filter,
                  bg="#FF9800", fg="white", font=("Arial", 10)).grid(row=0, column=5, padx=5)

    def clear_filter(self):
        """Сброс всех фильтров"""
        self.filter_type_combo.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.filter_date_entry.insert(0, "ГГГГ-ММ-ДД")
        self.refresh_table()

    def get_filtered_workouts(self):
        """Получение отфильтрованного списка тренировок"""
        type_filter = self.filter_type_var.get()
        date_filter = self.filter_date_entry.get().strip()

        filtered = self.workouts[:]

        # Фильтр по типу
        if type_filter and type_filter != "Все":
            filtered = [w for w in filtered if w["type"] == type_filter]

        # Фильтр по дате
        if date_filter and date_filter != "ГГГГ-ММ-ДД":
            if self.validate_date(date_filter):
                filtered = [w for w in filtered if w["date"] == date_filter]
            else:
                if date_filter:  # Если дата невалидна, показываем предупреждение
                    messagebox.showwarning("Предупреждение",
                                           f"Дата '{date_filter}' в фильтре недействительна. Фильтр по дате не применён.")

        return filtered

    # ---------- Таблица для отображения ----------
    def create_table(self):
        """Создание таблицы для отображения тренировок"""
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)

        # Настройка заголовков и ширины колонок
        self.tree.heading("Дата", text="📅 Дата")
        self.tree.heading("Тип тренировки", text="🏃 Тип тренировки")
        self.tree.heading("Длительность (мин)", text="⏱ Длительность (мин)")

        self.tree.column("Дата", width=120, anchor="center")
        self.tree.column("Тип тренировки", width=150, anchor="center")
        self.tree.column("Длительность (мин)", width=130, anchor="center")

        # Скроллбар
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Добавление возможности удаления двойным кликом
        self.tree.bind("<Double-1>", self.delete_workout)

    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очистить таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered_workouts = self.get_filtered_workouts()

        if not filtered_workouts:
            # Показываем сообщение, если нет данных
            self.tree.insert("", "end", values=("Нет данных", "Добавьте тренировку", ""))
        else:
            for workout in filtered_workouts:
                self.tree.insert("", "end", values=(
                    workout["date"],
                    workout["type"],
                    f"{workout['duration']:.1f}"
                ))

        # Обновление статуса
        total_workouts = len(filtered_workouts)
        total_duration = sum(w["duration"] for w in filtered_workouts)
        self.update_status_bar(total_workouts, total_duration)

    def update_status_bar(self, count, total_duration):
        """Обновление строки состояния"""
        # Удаляем старый статус-бар, если есть
        for widget in self.root.pack_slaves():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'is_status_bar'):
                widget.destroy()

        # Создаём новый статус-бар
        status_frame = tk.Frame(self.root, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
        status_frame.is_status_bar = True
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        status_text = f"📊 Всего тренировок: {count} | ⏱ Общая длительность: {total_duration:.1f} мин"
        status_label = tk.Label(status_frame, text=status_text, bg="#f0f0f0", font=("Arial", 9))
        status_label.pack(padx=5, pady=3)

    def delete_workout(self, event):
        """Удаление тренировки по двойному клику"""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        # Получаем значения выбранной строки
        values = self.tree.item(selected_item[0])['values']
        if values[0] == "Нет данных":
            return

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение",
                               f"Удалить тренировку?\nДата: {values[0]}\nТип: {values[1]}\nДлительность: {values[2]} мин"):
            # Находим и удаляем из списка
            for i, workout in enumerate(self.workouts):
                if (workout["date"] == values[0] and
                        workout["type"] == values[1] and
                        f"{workout['duration']:.1f}" == values[2]):
                    del self.workouts[i]
                    break

            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Тренировка удалена!")


# ---------- Запуск приложения ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
