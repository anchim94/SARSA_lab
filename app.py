import tkinter as tk
from tkinter import filedialog, messagebox
import os
import multiprocessing
import traceback

from learning import air_qlearn
from simulation import air_simul


def qlearn_worker(workdir):
    try:
        os.chdir(workdir)
        air_qlearn()
        # Nie wywołuj messagebox.showinfo tutaj, bo to inny proces!
    except Exception:
        with open("qlearn_error.log", "a", encoding="utf-8") as f:
            f.write("=== Nowy błąd podczas uczenia ===\n")
            f.write(traceback.format_exc())
            f.write("\n")


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Laboratorium 3 - Q-learning")
        self.geometry("500x300")
        self.resizable(False, False)

        # Katalog roboczy
        self.workdir = tk.StringVar(value=os.getcwd())
        tk.Label(self, text="Katalog roboczy:").pack(
            anchor="w", padx=10, pady=(10, 0))
        frame_dir = tk.Frame(self)
        frame_dir.pack(fill="x", padx=10)
        tk.Entry(frame_dir, textvariable=self.workdir, width=50).pack(
            side="left", fill="x", expand=True)
        tk.Button(frame_dir, text="Wybierz...",
                  command=self.choose_dir).pack(side="left", padx=5)

        # Przycisk uruchamiający uczenie
        tk.Button(self, text="Uruchom uczenie (air_qlearn)",
                  command=self.run_qlearn,
                  bg="#d0ffd0").pack(fill="x", padx=10, pady=(15, 5))

        # Wybór pliku do symulacji
        self.sim_file = tk.StringVar()
        tk.Label(self, text="Plik do symulacji:").pack(
            anchor="w", padx=10, pady=(10, 0))
        frame_file = tk.Frame(self)
        frame_file.pack(fill="x", padx=10)
        tk.Entry(frame_file, textvariable=self.sim_file, width=50).pack(
            side="left", fill="x", expand=True)
        tk.Button(frame_file, text="Wybierz plik...",
                  command=self.choose_file).pack(side="left", padx=5)

        # Przycisk uruchamiający symulację
        tk.Button(self, text="Uruchom symulację (air_simul)",
                  command=self.run_simul,
                  bg="#d0d0ff").pack(fill="x", padx=10, pady=(15, 5))

        # Przycisk zamykający aplikację
        tk.Button(self, text="Zamknij", command=self.destroy,
                  bg="#ffd0d0").pack(fill="x", padx=10, pady=(20, 10))

    def choose_dir(self):
        dirname = filedialog.askdirectory(initialdir=self.workdir.get())
        if dirname:
            self.workdir.set(dirname)
            os.chdir(dirname)

    def choose_file(self):
        filename = filedialog.askopenfilename(
            initialdir=self.workdir.get(), filetypes=[
                ("Pliki pickle", "*.pkl"), ("Wszystkie pliki", "*.*")])
        if filename:
            self.sim_file.set(filename)

    def run_qlearn(self):
        os.chdir(self.workdir.get())
        p = multiprocessing.Process(
            target=qlearn_worker, args=(self.workdir.get(),))
        p.start()
        messagebox.showinfo(
            "Info", "Uwaga! Możesz uruchomić kolejne przypadki równolegle.")

    def run_simul(self):
        os.chdir(self.workdir.get())
        if self.sim_file.get():
            try:
                air_simul(self.sim_file.get(), parent=self)
                messagebox.showinfo("Info", "Symulacja zakończona.")
            except Exception as e:
                messagebox.showerror(
                    "Błąd", f"Wystąpił błąd podczas symulacji:\n{e}")
        else:
            messagebox.showwarning("Uwaga", "Wybierz plik do symulacji.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MainApp()
    app.mainloop()
