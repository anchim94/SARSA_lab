import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, Tk


class QLearnDialog(tk.Tk):
    def __init__(self, tasks_names, controls_names):
        super().__init__()
        self.withdraw()
        self.dialog = simpledialog.Toplevel(self)
        self.dialog.title("Dane wejściowe")
        self.entries = {}
        self.options = {
            "Nazwa zadania": tasks_names,
            "Typ sterowania": controls_names,
        }
        self.defaults = {
            "Etykieta Rozwiązania": "Run 0",
            "Nazwa zadania": tasks_names[0],
            "Typ sterowania": controls_names[0],
            "u_max": "1.0",
            "epsil": "0.5",
            "alfa": "0.99",
            "Qx1": "1.0",
            "Qx2": "0.25",
            "Ru1": "0.0",
            "Maksymalna liczba iteracji": "1000",
            "gamma": "0.9",
            "epsilDecay": "1.0",
            "Krok Czasowy": "0.1",
            "Maksymalna liczba epizodów": "15000",
        }
        self.result = None
        self._build()

    def _on_ok(self):
        self.result = []
        for key in self.defaults:
            widget = self.entries[key]
            if isinstance(widget, ttk.Combobox):
                self.result.append(widget.get())
            else:
                self.result.append(widget.get())
        self.dialog.destroy()

    def _build(self):
        row = 0
        for key, default in self.defaults.items():
            tk.Label(self.dialog, text=key).grid(row=row, column=0, sticky="w")
            if key in self.options:
                if isinstance(self.options[key][0], bool):
                    var = tk.BooleanVar(value=bool(default))
                    cb = ttk.Checkbutton(self.dialog, variable=var)
                    cb.grid(row=row, column=1)
                    self.entries[key] = var
                else:
                    cb = ttk.Combobox(self.dialog, values=self.options[key], width=34)
                    cb.set(default)
                    cb.grid(row=row, column=1)
                    self.entries[key] = cb
            else:
                ent = tk.Entry(self.dialog)
                ent.insert(0, default)
                ent.grid(row=row, column=1)
                self.entries[key] = ent
            row += 1
        ok_btn = tk.Button(self.dialog, text="OK", command=self._on_ok)
        ok_btn.grid(row=row, column=0, columnspan=2)
        self.dialog.wait_window()
        self.destroy()


class SimulDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Dane wejściowe")
        self.entries = {}
        self.options = {
            "Sterowanie LQR": [True, False],
            "Trwały slad na wykresie stanu": [True, False],
        }
        self.defaults = {
            "Sterowanie LQR": False,
            "fi_0": "180.0",
            "om_0": "0.0",
            "dt": "0.1",
            "dt_delay": "0.05",
            "maxit": "20000",
            "Trwały slad na wykresie stanu": False,
        }
        self.result = None
        self._build()

    def _on_ok(self):
        self.result = []
        for key in self.defaults:
            widget = self.entries[key]
            if isinstance(widget, ttk.Combobox):
                self.result.append(widget.get())
            elif isinstance(widget, tk.BooleanVar):
                self.result.append(widget.get())
            else:
                self.result.append(widget.get())
        self.destroy()

    def _build(self):
        row = 0
        for key, default in self.defaults.items():
            tk.Label(self, text=key).grid(row=row, column=0, sticky="w")
            if key in self.options:
                if isinstance(self.options[key][0], bool):
                    var = tk.BooleanVar(value=bool(default))
                    cb = ttk.Checkbutton(self, variable=var, onvalue=True, offvalue=False)
                    cb.grid(row=row, column=1)
                    self.entries[key] = var
                else:
                    cb = ttk.Combobox(self, values=self.options[key])
                    cb.set(default)
                    cb.grid(row=row, column=1)
                    self.entries[key] = cb
            else:
                ent = tk.Entry(self)
                ent.insert(0, default)
                ent.grid(row=row, column=1)
                self.entries[key] = ent
            row += 1
        ok_btn = tk.Button(self, text="OK", command=self._on_ok)
        ok_btn.grid(row=row, column=0, columnspan=2)
        self.wait_window()


def enter_interface(tasks_names, controls_names):
    dialog = QLearnDialog(tasks_names, controls_names)
    return dialog.result


def enter_interface_simulation(parent=None):
    own_root = None
    if parent is None:
        own_root = tk.Tk()
        own_root.withdraw()
        parent = own_root
    dialog = SimulDialog(parent)
    result = dialog.result
    if own_root is not None:
        own_root.destroy()
    return result
