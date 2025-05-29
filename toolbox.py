import numpy as np


def state_global_index(x, x1, x2, n_x2):
    """
    Wyznaczenie globalnego indeksu w macierzy stanu na podstawie wartości stanu X.

    Argumenty:
        x (array-like): stan X [kąt, prędkość kątowa]
        x1 (array-like): lista możliwych wartości stanu kąta
        x2 (array-like): lista możliwych wartości stanu prędkości kątowej
        n_x2 (int): Liczba wartości x2

    Zwraca:
        int: Globalny indeks
    """
    import numpy as np

    x = np.asarray(x)
    x1 = np.asarray(x1)
    x2 = np.asarray(x2)

    ip = np.argmin((x[0] - x1) ** 2)
    jp = np.argmin((x[1] - x2) ** 2)
    indeks = n_x2 * ip + jp

    return indeks


def normalize_fi(fi):
    """
    Normalize angle fi to the range [-pi, pi).

    Reconsider using np.arctan2(np.sin(fi), np.cos(fi))

    Args:
        fi (float): Angle in radians.

    Returns:
        float: Normalized angle in radians.
    """
    if fi >= np.pi:
        fi = -np.pi + (fi - np.pi)
    elif fi < -np.pi:
        fi = np.pi - (-np.pi - fi)
    return fi


def rk_4(rhs, dt, x, u):
    """
    Runge-Kutta 4th order integrator.

    Args:
        rhs (callable): Function rhs(x, u) returning dx/dt.
        dt (float): Time step.
        x (array-like): Current state.
        u (array-like): Input/control.

    Returns:
        array-like: Next state after time step dt.
    """
    import numpy as np

    x = np.asarray(x)
    k1 = rhs(x, u)
    k2 = rhs(x + dt/2 * k1, u)
    k3 = rhs(x + dt/2 * k2, u)
    k4 = rhs(x + dt * k3, u)
    xn = x + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    return xn


def aw_matrices_AB(RHS, x, t, u, n, m):
    """
    Numeryczna aproksymacja macierzy A i B dla układu nieliniowego.
    RHS: funkcja prawej strony (RHS(x, u))
    x: wektor stanu (1D array)
    t: czas (nieużywany, dla zgodności)
    u: wektor sterowania (1D array)
    n: liczba zmiennych stanu
    m: liczba sterowań
    """
    x = np.asarray(x).flatten()
    u = np.asarray(u).flatten()
    delta = 1.0e-6

    f0 = RHS(x, u)

    A = np.zeros((n, n))
    for j in range(n):
        dx = np.zeros(n)
        dx[j] = delta
        A[:, j] = (RHS(x + dx, u) - f0) / delta

    B = np.zeros((n, m))
    for j in range(m):
        du = np.zeros(m)
        du[j] = delta
        B[:, j] = (RHS(x, u + du) - f0) / delta

    return A, B