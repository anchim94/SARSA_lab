import numpy as np


def dynamics0(x, u):
    """
    Wahadło proste
    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u.

    Parametry:
        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]
    """
    x = np.asarray(x)

    m = 1.0
    g = 1.0
    L = 1.0

    theta = x[0]
    theta_dot = x[1]

    theta_ddot = (g / L) * np.sin(theta) + u / (m * L**2)

    return np.array([theta_dot, theta_ddot])


def dynamics1(x, u):
    """
    Wahadło z tarciem suchym

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z dodatkowym oporem.

    Parametry:
        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]
    """
    x = np.asarray(x)
    m = 1.0
    g = 1.0
    L = 1.0
    xdot2 = g / L * np.sin(x[0]) - 0.05 * np.sign(x[1])
    xdot = np.array([x[1], xdot2 + u / (m * L**2)])
    return xdot


def dynamics2(x, u):
    """
    Wahadło z nieliniową sprężyną skrętną

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z dodatkowym nieliniowym oporem.

    Parametry:
        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]

    """
    x = np.asarray(x)
    m = 1.0
    g = 1.0
    L = 1.0
    xdot = np.array([
        x[1],
        g / L * np.sin(x[0]) + (-0.1 * x[0]**3) + u / (m * L**2)
    ])
    return xdot


def dynamics3(x, u):
    """
    Wahadło z luzem

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z warunkiem braku grawitacji przy małych kątach.

    Parametry:
        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]
    """
    x = np.asarray(x)
    m = 1.0
    g = 1.0
    L = 1.0
    if abs(x[0]) < 0.7:
        g = 0.0
    xdot = np.array([
        x[1],
        g / L * np.sin(x[0]) + u / (m * L**2)
    ])
    return xdot


def dynamics4(x, u):
    """
    Wahadło z odbojnikami

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z dodatkowym oporem przy przekroczeniu pewnych kątów.

    Parametry:
        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)
    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]
    """
    x = np.asarray(x)
    m = 1.0
    g = 1.0
    L = 1.0
    xdot2 = 0.0
    if x[0] < 0.7 and x[0] > 0.0:
        xdot2 = 1.0 * (0.7 - x[0])
    if x[0] > -0.7 and x[0] < 0.0:
        xdot2 = 1.0 * (-0.7 - x[0])
    xdot = np.array([
        x[1],
        g / L * np.sin(x[0]) + xdot2 + u / (m * L**2)
    ])
    return xdot


def dynamics5(x, u):
    """
    Wahadło ze zmienną masą

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z różną masą przy małych kątach.

    Parametry:
        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]
    """
    x = np.asarray(x)
    m = 1.0
    g = 1.0
    L = 1.0
    if abs(x[0]) < 0.7:
        m = 10.0
    xdot = np.array([
        x[1],
        g / L * np.sin(x[0]) + u / (m * L**2)
    ])
    return xdot


def dynamics6(x, u):
    """
    Wahadło z zaburzeniami losowymi

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z dodatkowym szumem.

    Parametry:

        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]

    """
    x = np.asarray(x)
    m = 1.0
    g = 1.0
    L = 1.0
    noise = 1.0 * np.random.randn()
    xdot = np.array([
        x[1],
        g / L * np.sin(x[0]) + u / (m * L**2) + noise
    ])
    return xdot


def dynamics7(x, u):
    """
    Wahadło ze zmienną długością

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z różną długością wahadła przy dużych kątach.

    Parametry:

        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]
    """
    x = np.asarray(x)
    m = 1.0
    g = 1.0
    L = 1.0
    if x[0] > 0.7:
        L = 0.5
    elif x[0] < -0.7:
        L = 0.5
    xdot = np.array([
        x[1],
        g / L * np.sin(x[0]) + u / (m * L**2)
    ])
    return xdot


def dynamicsS(x, u):
    """
    Huśtawka

    Funkcja oblicza pochodną stanu dla prostego wahadła z momentem u,
    z dodatkowym oporem i zmienną długością wahadła.

    Parametry:
        x : iterable (theta, theta_dot)
            Aktualny stan (kąt i prędkość kątowa)
        u : float
            Moment siły (sterowanie)

    Zwraca:
        xdot : ndarray
            Pochodna stanu [theta_dot, theta_ddot]
    """
    x = np.asarray(x)
    m = 1.0  # noqa TODO: sprawdzić, czy m jest potrzebne
    g = 1.0
    L = 1.0 + 0.5 * u
    xdot = np.array([
        x[1],
        g / L * np.sin(x[0]) - 0.005 * x[1]
    ])
    return xdot
