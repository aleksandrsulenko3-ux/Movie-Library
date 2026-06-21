import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library — Личная кинотека")
        self.data_file = "movies.json"
        self.movies = []
        self.load_data()

        self.setup_ui()

    def setup_ui(self):
        # --- Форма ввода ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить фильм", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Название
        tk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Жанр
        tk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", pady=5)
        self.genre_entry = tk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        # Год выпуска
        tk.Label(input_frame, text="Год выпуска:").grid(row=2, column=0, sticky="w", pady=5)
        self.year_entry = tk.Entry(input_frame, width=30)
        self.year_entry.grid(row=2, column=1, padx=5, pady=5)

        # Рейтинг
        tk.Label(input_frame, text="Рейтинг (0–10):").grid(row=3, column=0, sticky="w", pady=5)
        self.rating_entry = tk.Entry(input_frame, width=30)
        self.rating_entry.grid(row=3, column=1, padx=5, pady=5)

        # Кнопка добавления
        add_btn = tk.Button(input_frame, text="Добавить фильм", bg="#4CAF50", fg="white", command=self.add_movie)
        add_btn.grid(row=4, column=0, columnspan=2, pady=15)

        # --- Таблица ---
        table_frame = ttk.LabelFrame(self.root, text="Библиотека фильмов", padding=10)
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("title", width=200)
        self.tree.column("genre", width=100)
        self.tree.column("year", width=80, anchor="center")
        self.tree.column("rating", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # --- Фильтрация ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Фильтр по жанру
        tk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.genre_filter = ttk.Combobox(filter_frame, values=[], state="readonly")
        self.genre_filter.grid(row=0, column=1, padx=5, pady=5)
        btn_filter_genre = tk.Button(filter_frame, text="Фильтровать по жанру", command=self.filter_by_genre)
        btn_filter_genre.grid(row=0, column=2, padx=5, pady=5)

        # Фильтр по году
        tk.Label(filter_frame, text="Год:").grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.year_filter = tk.Entry(filter_frame, width=10)
        self.year_filter.grid(row=0, column=4, padx=5, pady=5)
        btn_filter_year = tk.Button(filter_frame, text="Фильтровать по году", command=self.filter_by_year)
        btn_filter_year.grid(row=0, column=5, padx=5, pady=5)

        btn_clear = tk.Button(filter_frame, text="Сбросить фильтры", command=self.show_all)
        btn_clear.grid(row=0, column=6, padx=10, pady=5)

        # Обновление списка жанров в фильтре
        self.update_genre_filter()

        # Настройка растягивания окна
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def update_genre_filter(self):
        genres = sorted(list(set(movie["genre"] for movie in self.movies)))
        self.genre_filter["values"] = genres

    def validate_input(self, title, genre, year_str, rating_str):
        if not title or not genre:
            messagebox.showerror("Ошибка ввода", "Поля «Название» и «Жанр» обязательны.")
            return False
        
        try:
            year = int(year_str)
            if year < 1888 or year > 2026:
                messagebox.showerror("Ошибка ввода", "Год должен быть в диапазоне от 1888 до 2026.")
                return False
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Год должен быть числом.")
            return False

        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка ввода", "Рейтинг должен быть от 0 до 10.")
                return False
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Рейтинг должен быть числом.")
            return False
        
        return True

    def add_movie(self):
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year_str = self.year_entry.get().strip()
        rating_str = self.rating_entry.get().strip()

        if self.validate_input(title, genre, year_str, rating_str):
            movie = {
                "title": title,
                "genre": genre,
                "year": int(year_str),
                "rating": float(rating_str)
            }
            self.movies.append(movie)
            self.save_data()
            self.update_table()
            self.update_genre_filter()
            self.clear_form()
            messagebox.showinfo("Успех", "Фильм успешно добавлен!")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)

    def update_table(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        display_data = data if data is not None else self.movies
        for movie in display_data:
            self.tree.insert("", "end", values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))

    def filter_by_genre(self):
        selected_genre = self.genre_filter.get()
        if not selected_genre:
            messagebox.showwarning("Внимание", "Выберите жанр из списка.")
            return
        filtered = [m for m in self.movies if m["genre"].lower() == selected_genre.lower()]
        self.update_table(filtered)

    def filter_by_year(self):
        year_str = self.year_filter.get().strip()
        if not year_str:
            messagebox.showwarning("Внимание", "Введите год для фильтрации.")
            return
        try:
            year = int(year_str)
            filtered = [m for m in self.movies if m["year"] == year]
            self.update_table(filtered)
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом.")

    def show_all(self):
        self.update_table()
        self.genre_filter.set("")
        self.year_filter.delete(0, tk.END)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.movies = []
                messagebox.showwarning("Предупреждение", "Файл данных поврежден или пуст. Создан новый.")
        else:
            self.movies = []

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, indent=4, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()
