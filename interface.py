import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, Tk


def enter_interface(tasks_names, controls_names):
    """
    Funkcja do wczytywania danych wejściowych z jednego okna dialogowego z możliwością wyboru z listy.
    """
    root = Tk()
    root.withdraw()

    # Tworzymy nowe okno dialogowe
    dialog = simpledialog.Toplevel(root)
    dialog.title("Dane wejściowe")
    # dialog.geometry("500x400")  # szerokość x wysokość w pikselach

    entries = {}
    options = {
        "Nazwa zadania": tasks_names,
        "Typ sterowania": controls_names,
    }
    defaults = {
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

    def on_ok():
        dialog.result = []
        for key in defaults:
            widget = entries[key]
            if isinstance(widget, ttk.Combobox):
                dialog.result.append(widget.get())
            else:
                dialog.result.append(widget.get())
        dialog.destroy()


    row = 0
    for key, default in defaults.items():
        tk.Label(dialog, text=key).grid(row=row, column=0, sticky="w")
        if key in options:
            # Jeśli chcesz użyć Checkbuttona dla wartości True/False:
            if isinstance(options[key][0], bool):
                var = tk.BooleanVar(value=bool(default))
                cb = ttk.Checkbutton(dialog, variable=var)
                cb.grid(row=row, column=1)
                entries[key] = var  # zapisz zmienną, nie widget!
            else:
                cb = ttk.Combobox(dialog, values=options[key], width=34)
                cb.set(default)
                cb.grid(row=row, column=1)
                entries[key] = cb
        else:
            # if isinstance(default, float) or isinstance(default, int):
            # # Jeśli to jest liczba, użyj Entry z domyślną wartością
            #     ent = tk.Scale(dialog, from_=0, to=10, orient=tk.HORIZONTAL, length=300)
            #     ent.set(float(default))
            #     ent.grid(row=row, column=1)
            # elif isinstance(default, str):
            ent = tk.Entry(dialog)
            ent.insert(0, default)
            ent.grid(row=row, column=1)
            entries[key] = ent
        row += 1

    ok_btn = tk.Button(dialog, text="OK", command=on_ok)
    ok_btn.grid(row=row, column=0, columnspan=2)

    dialog.wait_window()
    root.destroy()
    return dialog.result


def enter_interface_simulation():
    """
    Funkcja do wczytywania danych wejściowych z jednego okna dialogowego z możliwością wyboru z listy.
    """
    root = Tk()
    root.withdraw()

    # Tworzymy nowe okno dialogowe
    dialog = simpledialog.Toplevel(root)
    dialog.title("Dane wejściowe")

    entries = {}
    options = {
        "Sterowanie LQR": [True, False],
        "Trwały slad na wykresie stanu": [True, False],
    }
    defaults = {
        "Sterowanie LQR": False,
        "fi_0": "180.0",
        "om_0": "0.0",
        "dt": "0.1",
        "dt_delay": "0.05",
        "maxit": "20000",
        "Trwały slad na wykresie stanu": False,
    }

    def on_ok():
        dialog.result = []
        for key in defaults:
            widget = entries[key]
            if isinstance(widget, ttk.Combobox):
                dialog.result.append(widget.get())
            else:
                dialog.result.append(widget.get())
        dialog.destroy()


    row = 0
    for key, default in defaults.items():
        tk.Label(dialog, text=key).grid(row=row, column=0, sticky="w")
        if key in options:
            # Jeśli chcesz użyć Checkbuttona dla wartości True/False:
            if isinstance(options[key][0], bool):
                var = tk.BooleanVar(value=bool(default))
                cb = ttk.Checkbutton(dialog, variable=var)
                cb.grid(row=row, column=1)
                entries[key] = var  # zapisz zmienną, nie widget!
            else:
                cb = ttk.Combobox(dialog, values=options[key])
                cb.set(default)
                cb.grid(row=row, column=1)
                entries[key] = cb
        else:
            ent = tk.Entry(dialog)
            ent.insert(0, default)
            ent.grid(row=row, column=1)
            entries[key] = ent
        row += 1

    ok_btn = tk.Button(dialog, text="OK", command=on_ok)
    ok_btn.grid(row=row, column=0, columnspan=2)

    dialog.wait_window()
    root.destroy()
    return dialog.result
