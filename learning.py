import numpy as np
import time
import matplotlib.pyplot as plt
import pickle
from matplotlib.widgets import Button


from dynamics import (
    dynamics0,
    dynamics1,
    dynamics2,
    dynamics3,
    dynamics4,
    dynamics5,
    dynamics6,
    dynamics7,
    dynamicsS,
)

from toolbox import (
    state_global_index,
    normalize_fi,
    rk_4
)

from interface import enter_interface

tasks = {
    'Wahadło proste': dynamics0,
    'Wahadło z tarciem suchym': dynamics1,
    'Wahadło z nieliniową sprężyną skrętną': dynamics2,
    'Wahadło z luzem': dynamics3,
    'Wahadło z odbojnikami': dynamics4,
    'Wahadło ze zmienną masą': dynamics5,
    'Wahadło z zaburzeniami losowymi': dynamics6,
    'Wahadło ze zmienną długością': dynamics7,
    'Huśtawka': dynamicsS,
}

tasks_names = list(tasks.keys())

controls = {
    'Bang-bang': np.array([-1, 1]),
    'Bang-zero-bang': np.array([0, -1, 1]),
    'Dyskretne 5': np.array([-1, -0.5, 0, 0.5, 1]),
    'Dyskretne 21': np.linspace(-1, 1, 21)
}

controls_names = list(controls.keys())

# Globalny sygnał zatrzymania
Stop = False


def Stop_Callback(event):
    global Stop
    Stop = True


def air_qlearn():
    global Stop
    Stop = False

    try:
        answers = enter_interface(tasks_names, controls_names)
    except Exception as e:
        print(f"Błąd podczas wprowadzania danych: {e}")
        return

    StudInd = answers[0]
    DynamicsAct = tasks[answers[1]]
    DynamicsName = answers[1]
    u_max = float(answers[3])
    control = controls[answers[2]] * u_max
    epsil = float(answers[4])
    alpha = float(answers[5])
    Qx1 = float(answers[6])
    Qx2 = float(answers[7])
    Ru1 = float(answers[8])
    maxit = int(answers[9])
    gamma = float(answers[10])
    epsilDecay = float(answers[11])
    dt = float(answers[12])
    maxEpisodes = 15000  # liczba epizodów

    # Sprawdzenie poprawności danych wejściowych
    if not (0 < epsil <= 1):
        raise ValueError("Epsilon must be in the range (0, 1].")
    if not (0 < alpha <= 1):
        raise ValueError("Alpha must be in the range (0, 1].")
    if not (0 < gamma <= 1):
        raise ValueError("Gamma must be in the range (0, 1].")
    if not (0 <= Ru1):
        raise ValueError("Ru1 must be non-negative.")
    if not (0 < dt):
        raise ValueError("dt must be positive.")
    if not (maxit > 0):
        raise ValueError("maxit must be a positive integer.")
    if not (len(control) > 0):
        raise ValueError("Control array must not be empty.")
    if not (DynamicsName in tasks_names):
        raise ValueError(
            f"DynamicsName must be one of the predefined tasks: {tasks_names}.")
    if not (answers[2] in controls_names):
        raise ValueError(
            f"Control must be one of the predefined controls: "
            f"{controls_names}.")

    x_InitCond = [np.pi, 1.0 if DynamicsName == 'Huśtawka' else 0.0]

    m_u = len(control)  # liczba dysktretnych wartości sterowania

    # Dyskretyzacja przestrzeni stanu X
    # X1 - kąt
    # X2 - prędkość kątowa
    dx1 = 0.025
    dx2 = 0.05
    x1 = np.arange(-np.pi, np.pi + dx1, dx1)
    x2 = np.arange(-np.pi, np.pi + dx2, dx2)
    n_x1 = len(x1)  # liczba dyskretnych wartości kąta
    n_x2 = len(x2)  # liczba dyskretnych wartości prędkości kątowej

    # Funkcja nagrody
    rx = np.array([
        -(x1[i]**2 * Qx1 + x2[j]**2 * Qx2)
        for i in range(n_x1)
        for j in range(n_x2)
    ])
    ru = -Ru1 * control**2  # nagroda za sterowanie

    # Q-funkcja inicjalizacja (liczba stanów x liczba sterowań)
    Q = np.zeros((n_x1 * n_x2, m_u))
    V = np.zeros(n_x1 * n_x2)  # V-funkcja inicjalizacja (wektor liczba stanów)
    U = np.zeros(n_x1 * n_x2)  # Sterowanie (wektor liczba stanów)
    Vmean = []
    dVmean = []
    Qmean = []
    dQmean = []

    fig, axs = plt.subplots(2, 2, figsize=(10, 7))
    plt.subplots_adjust(wspace=0.35, hspace=0.35)
    fig.canvas.manager.set_window_title(f"Uczenie Q dla {DynamicsName}")

    # Dodaj przycisk Stop
    # [left, bottom, width, height]
    stop_ax = fig.add_axes([0.81, 0.025, 0.1, 0.04])
    stop_button = Button(stop_ax, 'Stop', color='red', hovercolor='tomato')
    stop_button.on_clicked(Stop_Callback)

    # Przechowuj referencje do colorbarów
    cbar1 = None
    cbar2 = None

    start_time = time.time()  # start pomiaru czasu

    for episode in range(maxEpisodes):
        x = np.copy(x_InitCond)  # inicjalizacja stanu

        # iterowanie -> uczenie
        for timestep in range(maxit):
            # wyznaczenie indeksu stanu
            k_x = state_global_index(x, x1, x2, n_x2)

            if np.random.rand() > epsil:
                # Eksploatacja
                # wybór sterowania na podstawie Q-funkcji
                k_u = np.argmax(Q[k_x])
            else:
                # Eksploracja
                k_u = np.random.randint(m_u)  # wybór sterowania losowo

            u = control[k_u]  # sterowanie
            x = rk_4(DynamicsAct, dt, x, u)  # rozwiązanie
            x[0] = normalize_fi(x[0])
            # wyznaczenie indeksu stanu po wykonaniu sterowania
            k1_x = state_global_index(x, x1, x2, n_x2)

            Q[k_x, k_u] += alpha * \
                (rx[k1_x] + ru[k_u] + gamma * np.max(Q[k1_x]) - Q[k_x, k_u])

            epsil *= epsilDecay

            if np.linalg.norm(x) < 0.01:
                break

        V = np.max(Q, axis=1)
        Vmean.append(np.sqrt(np.sum(V**2)))
        if episode > 1:
            dVmean.append((Vmean[-1] - Vmean[-2]) / Vmean[-1])

        Qmean.append(np.sqrt(np.sum(Q**2)))
        if episode > 1:
            dQmean.append((Qmean[-1] - Qmean[-2]) / Qmean[-1])

        for k in range(n_x1 * n_x2):
            U[k] = control[np.argmax(Q[k, :])]

        if episode % 10 == 0:
            with open(f'Learn_{StudInd}.pkl', 'wb') as f:
                pickle.dump({
                    'StudInd': StudInd,
                    'DynName': DynamicsName,
                    'DynamicsAct': DynamicsAct,
                    'U': U,
                    'dt': dt,
                    'maxit': maxit,
                    'u_max': u_max,
                    'x1': x1,
                    'x2': x2,
                    'control': control
                }, f)

            # Przekształcenie U i V do macierzy 2D dla wykresów
            U_2 = U.reshape((n_x1, n_x2)).T
            V_2 = V.reshape((n_x1, n_x2)).T

            # Aktualizacja wykresów
            fig.suptitle(
                f"Uczenie Q dla {DynamicsName} - "
                f"Epizod {episode}/{maxEpisodes}",
                fontsize=14
            )

            # Wykres Sterowania
            axs[0, 0].clear()
            cmap = plt.get_cmap('jet', len(control))
            axs[0, 0].set_prop_cycle(color=cmap(
                np.linspace(0, 1, len(control))))
            c1 = axs[0, 0].contourf(U_2, cmap=cmap)
            axs[0, 0].set_title('Sterowanie u(θ, dθ/dt)')
            axs[0, 0].set_xlabel('Kąt (θ) [rad]')
            axs[0, 0].set_ylabel('Prędkość kątowa (dθ/dt) [rad/s]')
            axs[0, 0].set_xticks([0, len(x1)//2, len(x1)-1])
            axs[0, 0].set_xticklabels(['-π', '0', 'π'])
            axs[0, 0].set_yticks([0, len(x2)//2, len(x2)-1])
            axs[0, 0].set_yticklabels(['-π', '0', 'π'])

            # Wykres V-funkcji
            axs[0, 1].clear()
            c2 = axs[0, 1].contourf(V_2, cmap='jet')
            axs[0, 1].set_title('Funkcja użyteczności V(θ, dθ/dt)')
            axs[0, 1].set_xlabel('Kąt (θ) [rad]')
            axs[0, 1].set_ylabel('Prędkość kątowa (dθ/dt) [rad/s]')
            axs[0, 1].set_xticks([0, len(x1)//2, len(x1)-1])
            axs[0, 1].set_xticklabels(['-π', '0', 'π'])
            axs[0, 1].set_yticks([0, len(x2)//2, len(x2)-1])
            axs[0, 1].set_yticklabels(['-π', '0', 'π'])

            # Odświeżanie colorbarów
            if cbar1 is not None:
                cbar1.remove()
            if cbar2 is not None:
                cbar2.remove()
            cbar1 = fig.colorbar(c1, ax=axs[0, 0])
            cbar2 = fig.colorbar(c2, ax=axs[0, 1])

            # Krzywa uczenia Vmean
            axs[1, 0].clear()
            axs[1, 0].plot(Vmean, 'b-')
            axs[1, 0].set_title('Krzywa uczenia Vmean')
            axs[1, 0].set_xlabel('Epizod')
            axs[1, 0].set_ylabel('Vmean')
            axs[1, 0].grid(True)

            # Czas obliczeń
            elapsed = int(time.time() - start_time)
            hh = elapsed // 3600
            mm = (elapsed % 3600) // 60
            ss = elapsed % 60
            elapsed_str = f"{hh:02}:{mm:02}:{ss:02}"

            # Panel tekstowy
            axs[1, 1].clear()
            axs[1, 1].axis('off')
            info_text = (
                f"Identyfikator: {StudInd}\n"
                f"Model testowany: {DynamicsName}\n"
                f"Epizod: {episode}/{maxEpisodes}\n"
                f"Czas obliczeń: {elapsed_str}\n"
                f"Q : {np.min(Q):.3f} <= Q <= {np.max(Q):.3f}\n"
                f"V : {np.min(V):.3f} <= Q <= {np.max(V):.3f}\n"
                f"dVmean: {0 if len(dVmean) == 0 else dVmean[-1]:.4E}\n"
                f"dQmean: {0 if len(dQmean) == 0 else dQmean[-1]:.4E}\n"
                f"Typ sterowania: {answers[2]}\n"
                f"u_max: {u_max:5.3f}\n"
                f"Alpha: {alpha:5.3f}\n"
                f"Gamma: {gamma:5.3f}\n"
                f"Epsilon: {epsil:.4f}\n"
                f"EpsilDecay: {epsilDecay:5.3f}\n"
                f"Nagroda (rx): {np.mean(rx):.3f}\n"
                f"Qx1: {Qx1:5.3f}\n"
                f"Qx2: {Qx2:5.3f}\n"
                f"Ru1: {Ru1:5.3f}\n"

            )
            axs[1, 1].text(0.05, 0.99, info_text, va='top',
                           ha='left', fontsize=10, family='monospace')

            plt.pause(0.01)

        if episode % 250 == 0:
            plt.savefig(f"Learn_{StudInd}.png")

        if Stop:
            plt.savefig(f"Learn_{StudInd}.png")
            break

    plt.close(fig)


if __name__ == "__main__":
    air_qlearn()
