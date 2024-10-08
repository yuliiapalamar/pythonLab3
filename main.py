import collections
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps


def find_trams_at_stop(stop_name, tram_routes):
    """
    Знаходить трамваї, що проходять через вказану зупинку.

    Параметри:
    - stop_name: назва зупинки для пошуку

    Повертає:
    - рядок з результатами пошуку
    """
    trams = []
    for tram, directions in tram_routes.items():
        for direction, stops in directions.items():
            if stop_name in stops:
                trams.append(tram)
    if trams:
        return f"Трамваї, які проходять через зупинку '{stop_name}': {', '.join(sorted(list(set(trams))))}"
    return f"Зупинка '{stop_name}' не знайдена в жодному маршруті."


def calculate_stops_and_transfers(start_stop, end_stop, tram_routes):
    """
    Обчислює кількість зупинок та пересадок між двома зупинками.

    Параметри:
    - start_stop: початкова зупинка
    - end_stop: кінцева зупинка

    Повертає:
    - рядок з результатами обчислень
    """
    if start_stop == end_stop:
        return 'Початкова і кінцева зупинки однакові.'
    queue = collections.deque([(start_stop, 0, None, [])])
    visited = set()

    while queue:
        current_stop, transfers, current_tram, path = queue.popleft()

        if current_stop == end_stop:
            total_transfers = transfers - 1
            total_stops = 0
            current_stop_index = tram_routes[path[0].split(',')[0]][path[0].split(',')[1]].index(start_stop)
            for item in path:
                tram_number = item.split(',')[0]
                direction = item.split(',')[1]
                next_stop = item.split(',')[2]
                total_stops += tram_routes[tram_number][direction].index(next_stop) - current_stop_index
                current_stop_index = tram_routes[tram_number][direction].index(next_stop)
            return f"Кількість зупинок: {total_stops}, кількість пересадок: {total_transfers}"

        if current_stop in visited:
            continue
        visited.add(current_stop)

        for tram, directions in tram_routes.items():
            for direction, stops in directions.items():
                if current_stop in stops:
                    stop_index = stops.index(current_stop)

                    for i in range(stop_index + 1, len(stops)):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'{tram},{direction},{next_stop}']))

                    for i in range(stop_index - 1, -1, -1):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'{tram},{direction},{next_stop}']))

    return "Маршруту не існує"


def find_trams_through_all_stops(*stops, tram_routes):
    """
    Знаходить трамваї, що проходять через всі вказані зупинки.

    Параметри:
    - stops: список зупинок для пошуку

    Повертає:
    - рядок з результатами пошуку
    """
    valid_trams = set(tram_routes.keys())

    for stop in stops:
        trams_at_stop = set()
        found = False
        for tram, directions in tram_routes.items():
            for direction, stops_list in directions.items():
                if stop in stops_list:
                    trams_at_stop.add(tram)
                    found = True

        if not found:
            return f"Зупинку '{stop}' не знайдено в жодному маршруті."

        valid_trams &= trams_at_stop

        if not valid_trams:
            return "Жоден маршрут не проходить через всі зазначені зупинки."

    if valid_trams:
        return f"Трамваї, які проходять через всі зупинки {', '.join(stops)}: {', '.join(valid_trams)}"
    return "Маршрутів, які проходять через всі зупинки, не знайдено."


def find_routes_between_stops(start_stop, end_stop, tram_routes):
    """
    Планує маршрут між двома вказаними зупинками.

    Параметри:
    - start_stop: початкова зупинка
    - end_stop: кінцева зупинка

    Повертає:
    - рядок з результатами маршруту
    """
    if start_stop == end_stop:
        return 'Початкова і кінцева зупинки однакові.'
    queue = collections.deque([(start_stop, 0, None, [])])
    visited = set()

    while queue:
        current_stop, transfers, current_tram, path = queue.popleft()

        if current_stop == end_stop:
            return f"Потрібний шлях:\n{' '.join(path)}\nПотрібна кількість пересадок: {transfers - 1}"

        if current_stop in visited:
            continue
        visited.add(current_stop)

        for tram, directions in tram_routes.items():
            for direction, stops in directions.items():
                if current_stop in stops:
                    stop_index = stops.index(current_stop)

                    for i in range(stop_index + 1, len(stops)):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'Сісти на трамвай номер {tram} який прямує до кінцевої зупинки "{stops[-1]}" та вийти на зупинці "{next_stop}"']))

                    for i in range(stop_index - 1, -1, -1):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'Сісти на трамвай номер {tram} який прямує до кінцевої зупинки "{stops[-1]}" та вийти на зупинці "{next_stop}"']))

    return "Маршруту не існує"


class TramRoutesApp:
    button_style = {
        "bg": "#D49FB6",
        "width": 25,
        "activebackground": "#D49FB6"
    }

    def __init__(self, root):
        """
        Конструктор класу TramRoutesApp - ініціалізує основне вікно програми.
        Викликає метод для завантаження трамвайних зупинок.

        Параметри:
         - root: головне вікно Tkinter

        """
        self.root = root
        self.root.title("TramsRoutes")
        self.root.geometry("650x450")
        self.root.configure(bg="#E9DADA")
        self.load_tram_stops()

        tk.Label(self.root, text="TramsRoutes", font=("Helvetica", 26), bg="#E9DADA").pack(pady=20)

        header_frame = tk.Frame(root, bg="#E9DADA")
        header_frame.pack(pady=10)
        tk.Label(header_frame, text="Оберіть необхідний функціонал", font=("Helvetica", 14), bg="#E9DADA").pack(
            side=tk.LEFT)

        icon_image = Image.open("icon.png")
        icon_image = icon_image.resize((20, 20))
        self.icon_photo = ImageTk.PhotoImage(icon_image)

        instruction_button = tk.Button(header_frame, image=self.icon_photo, command=self.show_instruction,
                                       bg="#E9DADA", borderwidth=0)
        instruction_button.pack(side=tk.LEFT, padx=(10, 0))

        button_frame = tk.Frame(self.root, bg="#E9DADA")
        button_frame.pack(pady=20)

        button_texts = ["Пошук трамваїв за зупинкою", "Кількість зупинок і пересадок",
                        "Трамваї через кілька зупинок", "Скласти маршрут"]

        for i, text in enumerate(button_texts):
            row = i // 2
            column = i % 2
            button = tk.Button(button_frame, text=text,
                               command=[self.open_find_trams_at_stop_window,
                                        self.open_calculate_stops_and_transfers_window,
                                        self.open_find_trams_through_all_stops_window,
                                        self.open_route_planning_window][i],
                               **self.button_style)
            button.grid(row=row, column=column, padx=10, pady=10)

        exit_button = tk.Button(self.root, text="Вийти", command=self.root.quit,
                                **self.button_style)
        exit_button.pack(side=tk.BOTTOM, pady=(0, 30))

    def load_tram_stops(self):
        """
        Завантажує дані про зупинки трамваїв з файлу TramStops.json.

        """
        with open('TramStops.json', 'r', encoding='utf8') as file:
            self.tram_stops = json.load(file)
            self.all_stops = set()
            for stops in self.tram_stops.values():
                self.all_stops.update(stops['forward'])
                self.all_stops.update(stops['backward'])
            self.all_stops = sorted(self.all_stops)

    def show_instruction(self):
        """
        Відображає інструкції з використання програми в діалоговому вікні.

        """
        instruction_text = (
            "Доступні функції програми:\n"
            " - Пошук трамваїв за зупинкою: дозволяє знайти трамваї, які проходять через зазначену зупинку.\n"
            " - Кількість зупинок і пересадок: надає інформацію про кількість зупинок та необхідних пересадок для обраного маршруту.\n"
            " - Трамваї через кілька зупинок: дозволяє знайти трамваї, які зупиняються на кількох вказаних зупинках.\n"
            " - Скласти маршрут: допомагає побудувати маршрут з початкової до кінцевої зупинки.\n\n"
            "Як користуватися програмою:\n"
            "1. Для початку роботи потрібно запустити файл main.py.\n"
            "2. Після запуску програми з'явиться вікно з заголовком TramsRoutes.\n"
            "3. Оберіть необхідний функціонал, натиснувши на відповідну кнопку:\n"
            "    - Пошук трамваїв за зупинкою\n"
            "    - Кількість зупинок і пересадок\n"
            "    - Трамваї через кілька зупинок\n"
            "    - Скласти маршрут\n"
            "4. У відповідному полі введіть назви зупинок, з якими хочете працювати.\n"
            "5. Натисніть кнопку Пошук, щоб отримати результати.\n"
            "6. Щоб повернутися на головне вікно натисніть кнопку Назад.\n"
            "7. Для виходу з програми натисніть кнопку Вийти."
        )
        messagebox.showinfo("Інструкція", instruction_text)

    def open_find_trams_at_stop_window(self):
        """
        Відкриває вікно для пошуку трамваїв за вказаною зупинкою.

        """
        self.root.withdraw()
        window = tk.Toplevel(self.root)
        window.geometry("650x450")
        window.title("Пошук трамваїв за зупинкою")
        window.configure(bg="#E9DADA")

        tk.Label(window, text="Пошук трамваїв за зупинкою", font=("Helvetica", 16), bg="#E9DADA").pack(pady=10)

        tk.Label(window, text="Оберіть зупинку:", bg="#E9DADA", font=("Helvetica", 12)).pack(pady=10)

        stop_combobox = ttk.Combobox(window, values=self.all_stops)
        stop_combobox.pack(pady=10)

        result_text = tk.Text(window, height=5, width=60, bg="#E9DADA", font=("Helvetica", 12))
        result_text.pack(pady=10)

        def search_trams():
            """
            Викликає метод пошуку трамваїв, що проходять через обрану зупинку.

            """
            stop_name = stop_combobox.get()
            result = find_trams_at_stop(stop_name, self.tram_stops)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, result)

        button_frame = tk.Frame(window, bg="#E9DADA")
        button_frame.pack(side=tk.BOTTOM, pady=(0, 30))

        tk.Button(window, text="Пошук", command=search_trams, **self.button_style).pack(pady=20)
        tk.Button(button_frame, text="Назад", command=lambda: self.close_window(window), **self.button_style).pack(side=tk.LEFT,
                                                                                                padx=(10, 0))
        tk.Button(button_frame, text="Вийти", command=self.root.quit, **self.button_style).pack(side=tk.LEFT,
                                                                                                padx=(10, 0))

    def open_calculate_stops_and_transfers_window(self):
        """
        Відкриває вікно для обчислення кількості зупинок та пересадок між двома зупинками.

        """
        self.root.withdraw()
        window = tk.Toplevel(self.root)
        window.geometry("650x450")
        window.title("Кількість зупинок і пересадок")
        window.configure(bg="#E9DADA")

        tk.Label(window, text="Кількість зупинок і пересадок", font=("Helvetica", 16), bg="#E9DADA").pack(pady=10)

        select_frame = tk.Frame(window, bg="#E9DADA")
        select_frame.pack(pady=10)

        tk.Label(select_frame, text="Оберіть початкову зупинку", bg="#E9DADA", font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
        start_combobox = ttk.Combobox(select_frame, values=self.all_stops)
        start_combobox.grid(row=1, column=0, padx=5)

        tk.Label(select_frame, text="Оберіть кінцеву зупинку", bg="#E9DADA", font=("Helvetica", 12)).grid(row=0, column=1, padx=5)
        end_combobox = ttk.Combobox(select_frame, values=self.all_stops)
        end_combobox.grid(row=1, column=1, padx=5)

        result_text = tk.Text(window, height=10, width=60, bg="#E9DADA", font=("Helvetica", 12))
        result_text.pack(pady=10)

        def calculate_stops():
            """
            Викликає метод обчислення кількості зупинок та пересадок між двома вказаними зупинками.

            """
            start_stop = start_combobox.get()
            end_stop = end_combobox.get()
            result = calculate_stops_and_transfers(start_stop, end_stop, self.tram_stops)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, result)

        button_frame = tk.Frame(window, bg="#E9DADA")
        button_frame.pack(side=tk.BOTTOM, pady=(0, 30))

        tk.Button(window, text="Пошук", command=calculate_stops, **self.button_style).pack(pady=20)
        tk.Button(button_frame, text="Назад", command=lambda: self.close_window(window), **self.button_style).pack(side=tk.LEFT,
                                                                                                padx=(10, 0))
        tk.Button(button_frame, text="Вийти", command=self.root.quit, **self.button_style).pack(side=tk.LEFT,
                                                                                                padx=(10, 0))

    def open_find_trams_through_all_stops_window(self):
        """
        Відкриває вікно для пошуку трамваїв через кілька зупинок.
        """
        self.root.withdraw()
        window = tk.Toplevel(self.root)
        window.geometry("650x450")
        window.title("Трамваї через кілька зупинок")
        window.configure(bg="#E9DADA")

        tk.Label(window, text="Трамваї через кілька зупинок", font=("Helvetica", 16), bg="#E9DADA").pack(pady=10)

        tk.Label(window, text="Оберіть зупинки:", bg="#E9DADA", font=("Helvetica", 12)).pack(pady=10)

        stop_listbox = tk.Listbox(window, selectmode=tk.MULTIPLE, height=5, bg="#E9DADA", font=("Helvetica", 12))
        for stop in self.all_stops:
            stop_listbox.insert(tk.END, stop)
        stop_listbox.pack(pady=10)

        result_text = tk.Text(window, height=5, width=60, bg="#E9DADA", font=("Helvetica", 12))
        result_text.pack(pady=10)

        def search_trams():
            """
            Викликає метод пошуку трамваїв, що проходять через всі вказані зупинки.
            """
            selected_indices = stop_listbox.curselection()
            selected_stops = [stop_listbox.get(i) for i in selected_indices]

            if not selected_stops:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Будь ласка, оберіть хоча б одну зупинку.")
                return

            result = find_trams_through_all_stops(*selected_stops[:-1], tram_routes=self.tram_stops)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, result)

        button_frame = tk.Frame(window, bg="#E9DADA")
        button_frame.pack(side=tk.BOTTOM, pady=(0, 30))

        tk.Button(window, text="Пошук", command=search_trams, **self.button_style).pack(pady=20)
        tk.Button(button_frame, text="Назад", command=lambda: self.close_window(window), **self.button_style).pack(
            side=tk.LEFT, padx=(10, 0))
        tk.Button(button_frame, text="Вийти", command=self.root.quit, **self.button_style).pack(side=tk.LEFT,
                                                                                                padx=(10, 0))

    def open_route_planning_window(self):
        """
        Відкриває вікно для планування маршруту між двома зупинками.

        """
        self.root.withdraw()
        window = tk.Toplevel(self.root)
        window.geometry("650x450")
        window.title("Скласти маршрут")
        window.configure(bg="#E9DADA")

        tk.Label(window, text="Скласти маршрут", font=("Helvetica", 16), bg="#E9DADA").pack(pady=10)

        tk.Label(window, text="Оберіть початкову зупинку", bg="#E9DADA", font=("Helvetica", 12)).pack(pady=10)
        start_combobox = ttk.Combobox(window, values=self.all_stops)
        start_combobox.pack(pady=10)

        tk.Label(window, text="Оберіть кінцеву зупинку", bg="#E9DADA", font=("Helvetica", 12)).pack(pady=10)
        end_combobox = ttk.Combobox(window, values=self.all_stops)
        end_combobox.pack(pady=10)

        result_text = tk.Text(window, height=5, width=60, bg="#E9DADA", font=("Helvetica", 12))
        result_text.pack(pady=10)

        def plan_route():
            """
            Викликає метод пошуку маршруту між двома вказаними зупинками.

            """
            start_stop = start_combobox.get()
            end_stop = end_combobox.get()
            result = find_routes_between_stops(start_stop, end_stop, self.tram_stops)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, result)

        button_frame = tk.Frame(window, bg="#E9DADA")
        button_frame.pack(side=tk.BOTTOM, pady=(0, 30))

        tk.Button(window, text="Пошук", command=plan_route, **self.button_style).pack(pady=20)
        tk.Button(button_frame, text="Назад", command=lambda: self.close_window(window), **self.button_style).pack(side=tk.LEFT,
                                                                                                padx=(10, 0))
        tk.Button(button_frame, text="Вийти", command=self.root.quit, **self.button_style).pack(side=tk.LEFT,
                                                                                                padx=(10, 0))

    def close_window(self, window):
        """
        Закриває поточне вікно та відновлює головне вікно.

        Параметри:
        - window: вікно, яке потрібно закрити

        """
        window.destroy()
        self.root.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    app = TramRoutesApp(root)
    root.mainloop()
