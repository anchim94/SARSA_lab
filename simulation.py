import numpy as np
import matplotlib.pyplot as plt
import pickle
from matplotlib.widgets import Button
from scipy.linalg import solve_continuous_are as care

import sys
import os

from toolbox import (
    state_global_index,
    normalize_fi,
    rk_4,
    aw_matrices_AB,
)
from interface import enter_interface_simulation

# Globalne flagi
Stop = False
Pause = True
pause_button = None  # dodaj globalną referencję


def stop_callback(event):
    global Stop
    Stop = True


def pause_callback(event):
    global Pause, pause_button
    Pause = not Pause
    if Pause:
        pause_button.label.set_text('Run')
        pause_button.color = 'green'
        pause_button.hovercolor = 'lime'

    else:
        pause_button.label.set_text('Pause')
        pause_button.color = 'orange'
        pause_button.hovercolor = 'yellow'
    pause_button.ax.figure.canvas.draw_idle()


def air_simul(path_to_file=None, parent=None):
    """
    Funkcja do symulacji wahadła lub huśtawki na podstawie danych z pliku.
    Parametry:
        path_to_file (str): Ścieżka do pliku z danymi. Jeśli None, użyje
        domyślnego pliku 'Learn_TEST.pkl'.
        parent (tk.Tk): Rodzic okna, jeśli jest używane w aplikacji GUI.
    Zwraca:
        None
    """
    if path_to_file is None:
        path_to_file = 'Learn_TEST.pkl'  # Domyślna ścieżka do pliku
    if not os.path.exists(path_to_file):
        print(f"Plik {path_to_file} nie istnieje.")
        sys.exit(1)

    global Stop, Pause, pause_button
    Stop = False
    Pause = True

    try:
        answers = enter_interface_simulation(parent=parent)
    except Exception as e:
        print(f"Błąd podczas wprowadzania danych: {e}")
        sys.exit(1)

    controlLQR = bool(answers[0])
    fi_0 = float(answers[1]) * np.pi / 180.0
    om_0 = float(answers[2])
    dt1 = float(answers[3])
    dt_delay = float(answers[4])
    maxit = int(answers[5])
    trace = bool(answers[6])

    # --- Wczytaj dane z pliku ---
    with open(path_to_file, 'rb') as f:
        data = pickle.load(f)
    StudInd = data['StudInd']
    DynName = data['DynName']
    DynamicsAct = data['DynamicsAct']
    U = data['U']
    dt = data['dt']
    u_max = data['u_max']
    x1 = data['x1']
    x2 = data['x2']
    control = data['control']

    dt = dt1
    n1 = len(x1)
    n2 = len(x2)

    SwingProblem = 0
    if DynName == 'Huśtawka':
        SwingProblem = 1

    x_InitCond = [fi_0, om_0]
    U_2 = U.reshape((n1, n2)).T

    # --- Ustaw wykres ---
    fig = plt.figure(figsize=(8, 5))
    fig.patch.set_facecolor((0.9, 0.9, 0.9))
    ax_pend = plt.axes([0.03, 0.35, 0.3, 0.53])
    ax_pend.set_aspect('equal')
    ax_pend.set_xlim(-3, 3)
    ax_pend.set_ylim(-3, 3)
    ax_pend.axis('off')

    PendLen0 = 2.0

    # Wahadło
    f, = ax_pend.plot([0, 0], [0, 0], 'k', linewidth=1)
    ax_pend.plot(0.0, 0.15, 'vr', markersize=10, linewidth=1)
    # Siła
    f1, = ax_pend.plot([0, 0], [0, 0], 'b', linewidth=5)
    # Masa
    f2, = ax_pend.plot([0, 0], [0, 0], 'go',
                       markerfacecolor='black', linewidth=5)

    # Mapa sterowania
    ax_map = plt.axes([0.38, 0.25, 0.58, 0.60])
    # cmap = plt.get_cmap('jet', 10)
    cmap = plt.get_cmap('jet', len(control))
    ax_map.set_prop_cycle(color=cmap(np.linspace(0, 1, len(control))))
    map_img = ax_map.imshow(U_2*0 if controlLQR else U_2,
                            aspect='auto', cmap=cmap, origin='lower')
    plt.colorbar(map_img, ax=ax_map)
    ax_map.set_title(
        'Sterowanie u(θ, dθ/dt)' if not controlLQR else 'Sterowanie LQR')
    ax_map.set_xticks([0, n1//2, n1-1])
    ax_map.set_xticklabels(['-π', '0', 'π'])
    ax_map.set_yticks([0, n2//2, n2-1])
    ax_map.set_yticklabels(['-π', '0', 'π'])
    ax_map.set_xlabel('θ (rad)')
    ax_map.set_ylabel('dθ/dt (rad/s)')
    ax_map.set_xlim(0, n1-1)
    ax_map.set_ylim(0, n2-1)
    pathmap, = ax_map.plot([], [], '.w', markersize=10)
    pathx = []
    pathy = []

    # Przyciski
    stop_ax = plt.axes([0.7, 0.025, 0.07, 0.04])
    stop_button = Button(stop_ax, 'Stop', color='red', hovercolor='tomato')
    stop_button.on_clicked(stop_callback)

    pause_ax = plt.axes([0.6, 0.025, 0.07, 0.04])
    pause_button = Button(pause_ax, 'Run', color='green', hovercolor='lime')
    pause_button.on_clicked(pause_callback)

    # Tekst
    txt = ax_pend.text(-2, -5, '', fontsize=10, family='monospace')
    _ = ax_map.text(-0.1, -0.15, DynName, fontsize=10, fontweight='bold',
                    ha='left', va='top', transform=ax_map.transAxes)

    x = np.array(x_InitCond, dtype=float)
    t = 0.0

    for timestep in range(maxit):
        plt.pause(dt_delay)

        k_x = state_global_index(x, x1, x2, n2)
        u = U[int(k_x)]

        # LQR (opcjonalnie)
        if controlLQR:
            # Algorytm LQR - rozwiązanie równań Riccatiego
            # A, B, QQ, RR to macierze systemu
            A, B = aw_matrices_AB(DynamicsAct, x, t, u, 2, 1)
            RR = np.array([[1.0]])  # Macierz wag dla sterowania
            QQ = np.array([[1.0, 0.0], [0.0, 1.0]])  # Macierz wag dla stanu
            # Rozwiązanie równania Riccatiego:
            # A^T P + P A - P B R⁻¹ B^T P + Q = 0
            # Algorytm CARE (Continuous-time Algebraic Riccati Equation)
            P = care(A, B, QQ, RR)
            # Wyliczenie wzmocnienia sprzężenia zwrotnego: K = R⁻¹ B^T P
            K = np.linalg.inv(RR) @ B.T @ P
            u = -K @ x.T  # Sterowanie LQR
            u = np.clip(u[0], -u_max, u_max)
        else:
            # Normalne sterowanie z Q-funkcji
            u = U[int(k_x)]

        PendLen = PendLen0 + 0.5 * u * SwingProblem

        # Aktualizacja stanu
        if not Pause:
            x = rk_4(DynamicsAct, dt, x, u)
            x[0] = normalize_fi(x[0])

        # Rysowanie wahadła
        se = np.sin(x[0])
        ce = np.cos(x[0])
        f.set_data([0, -PendLen * se], [0, PendLen * ce])
        color = 'b' if u > 0 else 'r' if u < 0 else 'w'
        f1.set_color(color)
        f1.set_data([-PendLen * se, -PendLen * se
                     + u * ce * (1 - SwingProblem)],
                    [PendLen * ce, PendLen * ce
                     + u * se * (1 - SwingProblem)])
        f2.set_data([-PendLen * se, -PendLen * se],
                    [PendLen * ce, PendLen * ce])

        # Aktualizacja ścieżki na mapie
        k1_x = state_global_index(x, x1, x2, n2)
        newx, newy = np.unravel_index(indices=int(k1_x), shape=(n1, n2))
        pathx.append(newx)
        pathy.append(newy)

        if trace:
            # Rysowanie śladu na mapie
            pathmap.set_data(pathx, pathy)
        else:
            # Aktualizacja ścieżki na mapie z efektem blaknięcia
            N_fade = 50  # liczba punktów śladu, które mają być widoczne
            for coll in getattr(ax_map, '_fade_dots', []):
                coll.remove()
            ax_map._fade_dots = []
            n_points = len(pathx)
            for i in range(max(0, n_points - N_fade), n_points):
                alpha = (i - (n_points - N_fade)) / N_fade  # od 0 do 1
                dot = ax_map.plot(pathx[i], pathy[i],
                                  '.w', markersize=10, alpha=alpha)[0]
                ax_map._fade_dots.append(dot)

        # Aktualizacja tekstu
        txt.set_text(
            f'θ = {x[0]*180.0/np.pi:8.4f} [deg]\n'
            f'dθ/dt = {x[1]:8.4f} [rad/s]\n'
            f'u = {u:8.4f} [N]\n'
            f't = {t:8.4f} [s]'
        )

        # Aktualizacja czasu
        if not Pause:
            t += dt

        if Stop:
            plt.savefig(f"Simul_{StudInd}.png")
            plt.pause(1)
            break

    plt.close(fig)


if __name__ == "__main__":
    air_simul()
