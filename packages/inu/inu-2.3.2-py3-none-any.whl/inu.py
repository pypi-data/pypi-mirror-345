"""
Provide forward mechanization of inertial measurement unit sensor values
(accelerometer and gyroscope readings) to get position, velocity, and attitude
as well as inverse mechanization to get sensor values from position, velocity,
and attitude. Include tools to calculate velocity from geodetic position over
time, to estimate attitude from velocity, to estimate wind velocity from
ground-track velocity and yaw angle, and to generate navigation paths from
waypoints.

Constants
=========

# WGS84 constants (IS-GPS-200M and NIMA TR8350.2)
A_E = 6378137.0             # Earth's semi-major axis (m) (p. 109)
E2 = 6.694379990141317e-3   # Earth's eccentricity squared (ND) (derived)
W_EI = 7.2921151467e-5      # sidereal Earth rate (rad/s) (p. 106)

# gravity coefficients
GRAV_E = 9.7803253359       # gravity at equator (m/s^2)
GRAV_K = 1.93185265241e-3
GRAV_F = 3.35281066475e-3   # ellipsoidal flattening
GRAV_M = 3.44978650684e-3

Functions and methods
=====================

Support Functions
-----------------

class Baro:
    def __init__(self,
            baro_name: str | None = None,
            er_int: float = 0.0
        ) -> None:
    def reset(self,
            er_int: float = 0.0
        ) -> None:

def wrap(
        Y: float | np.ndarray
    ) -> float | np.ndarray:

def ned_enu(
        vec: np.ndarray
    ) -> np.ndarray:

def vanloan(
        F: np.ndarray,
        B: np.ndarray | None = None,
        Q: np.ndarray | None = None,
        T: float | None = None
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

Truth Generation
----------------

def path_box(
        seg_len: float,
        width: float = 2000.0,
        height: float = 2000.0,
        radius: float = 300.0,
        cycles: int = 3
    ) -> np.ndarray:

def path_circle(
        seg_len: float,
        radius: float = 1000.0,
        cycles: int = 5
    ) -> np.ndarray:

def path_clover(
        seg_len: float,
        radius: float = 10000.0,
        cycles: int = 3
    ) -> np.ndarray:

def path_grid(
        seg_len: float,
        spacing: float = 300.0,
        length: float = 1600.0,
        rows: int = 6
    ) -> np.ndarray:

def path_pretzel(
        K: int,
        radius: float = 1000.0,
        height: float = 100.0,
        cycles: float = 1.0,
        twists: int = 1
    ) -> np.ndarray:

def path_spiral(
        seg_len: float,
        spacing: float = 300.0,
        cycles: int = 3
    ) -> np.ndarray:

class waypoints:
    def __init__(self,
            points: np.ndarray,
            seg_len: float = 1.0,
            radius_min: float = 0.0,
            plot: bool = True,
            ax: axes= None,
            color: str = "tab:blue",
            warncolor: str = "tab:orange"
        ) -> None:

def llh_to_vne(
        llh_t: np.ndarray,
        T: float
    ) -> np.ndarray:

def somigliana(
        llh: np.ndarray
    ) -> np.ndarray:

def vne_to_rpy(
        vne_t: np.ndarray,
        grav_t: np.ndarray,
        T: float,
        alpha: float = 0.06,
        wind: np.ndarray = None
    ) -> np.ndarray:

def llh_to_tva(
        llh_t: np.ndarray,
        T: float
    ) -> np.ndarray:

def noise_fogm(
        T: float,
        tau: float,
        var: float,
        K: int
    ) -> np.ndarray:

Inertial Mechanization
----------------------

def mech_inv(
        llh_t: np.ndarray,
        rpy_t: np.ndarray,
        T: float,
        grav_model: Callable[[np.ndarray], np.ndarray] = somigliana
    ) -> tuple[np.ndarray, np.ndarray]:

def mech(
        fbbi_t: np.ndarray,
        wbbi_t: np.ndarray,
        llh0: np.ndarray,
        vne0: np.ndarray,
        rpy0: np.ndarray,
        T: float,
        hae_t: np.ndarray | None = None,
        baro_name: str | None = None,
        grav_model: Callable[[np.ndarray], np.ndarray] = somigliana
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

def mech_step(
        fbbi: np.ndarray,
        wbbi: np.ndarray,
        llh: np.ndarray,
        vne: np.ndarray,
        Cnb: np.ndarray,
        hb: float | None = None,
        baro: Baro | None = None,
        grav_model: Callable[[np.ndarray], np.ndarray] = somigliana
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

def jacobian(
        fbbi: np.ndarray,
        llh: np.ndarray,
        vne: np.ndarray,
        Cnb: np.ndarray,
        baro: Baro | None = None
    ) -> np.ndarray:
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Callable
import warnings

import matplotlib.pyplot as plt
import numpy as np
import r3f

if TYPE_CHECKING:
    from matplotlib import axes
    from matplotlib.backend_bases import (
        CloseEvent, KeyEvent, MouseEvent, ResizeEvent, ScrollEvent)

# WGS84 constants (IS-GPS-200M and NIMA TR8350.2)
A_E = 6378137.0             # Earth's semi-major axis (m) (p. 109)
E2 = 6.694379990141317e-3   # Earth's eccentricity squared (ND) (derived)
W_EI = 7.2921151467e-5      # sidereal Earth rate (rad/s) (p. 106)

# gravity coefficients
GRAV_E = 9.7803253359       # gravity at equator (m/s^2)
GRAV_K = 1.93185265241e-3
GRAV_F = 3.35281066475e-3   # ellipsoidal flattening
GRAV_M = 3.44978650684e-3

# -----------------
# Support Functions
# -----------------

class Baro:
    """
    Barometric altitude aiding model.

    Attributes
    ----------
    name : str
        The name of the barometric altitude aiding model. This must be one of
        "savage", "rogers", "widnall", "silva", "iae", "ise", "itae", or "itse".
    K : list
        List of feedback coefficients.
    er : float
        Error between the mechanization algorithm's altitude and the barometric
        altitude (m).
    er_int : float
        Integral of the error between the mechanization algorithm's altitude and
        the barometric altitude (m s).
    """

    def __init__(self,
            baro_name: str | None = None,
            er_int: float = 0.0
        ) -> None:
        """
        Initialize the barometric altitude aiding model.

        Parameters
        ----------
        baro_name : str, default None
            The name of the barometric altitude aiding model. This must be one
            of "savage", "rogers", "widnall", "silva", "iae", "ise", "itae", or
            "itse".
        er_int : float, default 0.0
            The initial integral of integrated error, where error is defined as
            the integral of the error between the mechanization algorithm's
            altitude and the barometric altitude (m s).
        """

        # Dictionary of barometric altitude aiding coefficients
        K_dict = {
            "savage":   [3e-1, 3e-2, 1e-3],
            "rogers":   [3e-2, 4e-4, 2e-6],
            "widnall":  [1.003, 4.17e-3, 4.39e-6],
            "silva":    [1.46e-1, 1.84e-2, 4.46e-4],
            "iae":      [1.0, 1e-3, 1e-6],
            "ise":      [1.0, 5e-3, 1e-6],
            "itae":     [1.0, 1.0, 1e-6],
            "itse":     [1.0, 1e-3, 1e-6]}

        if baro_name in K_dict:
            self.name = baro_name
            self.K = np.array(K_dict[baro_name])
            self.er = 0.0
            self.er_int = er_int
        else:
            raise ValueError(f"{baro_name} is not a valid model name!")

    def reset(self,
            er_int: float = 0.0
        ) -> None:
        """ Reset the baro model's state. """

        self.er = 0.0
        self.er_int = er_int


def wrap(
        Y: float | np.ndarray
    ) -> float | np.ndarray:
    """ Wrap angles to a -pi to pi range. This function is vectorized. """
    return Y - np.round(Y/math.tau)*math.tau


def ned_enu(
        vec: np.ndarray
    ) -> np.ndarray:
    """
    Swap between North, East, Down (NED) orientation and East, North, Up (ENU)
    orientation. This operation changes the array in place.

    Parameters
    ----------
    vec : (3,) or (3, K) or (K, 3) np.ndarray
        Three-element vector or matrix of such vectors.

    Returns
    -------
    out : (3,) or (3, K) or (K, 3) np.ndarray
        Three-element vector or matrix of such vectors.
    """

    # Check input.
    if isinstance(vec, (list, tuple)):
        vec = np.array(vec)
    trs = (vec.ndim == 2 and vec.shape[0] != 3)

    # Transpose input.
    if trs:
        vec = vec.T

    # Initialize output.
    out = np.zeros_like(vec)

    # Flip sign of z axis.
    out[2] = -vec[2].copy()

    # Swap the x and y axes.
    out[1] = vec[0].copy()
    out[0] = vec[1].copy()

    # Transpose output.
    if trs:
        out = out.T

    return out


def vanloan(
        F: np.ndarray,
        B: np.ndarray | None = None,
        Q: np.ndarray | None = None,
        T: float | None = None
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Discretize the dynamics, stochastic matrices in the equation

        .                 .--
        x = F x + B u + `/ Q  w

    where `F` is the dynamics matrix, `B` is the input matrix, and `Q` is the
    noise covariance matrix.

    Parameters
    ----------
    F : 2D np.ndarray
        Continuous-domain dynamics matrix.
    B : 2D np.ndarray, default None
        Continuous-domain dynamics input matrix. To omit this input, provide
        `None`.
    Q : 2D np.ndarray, default None
        Continuous-domain dynamics noise covariance matrix. To omit this input,
        provide `None`.
    T : float, default 1.0
        Sampling period in seconds.

    Returns
    -------
    Phi : 2D np.ndarray
        Discrete-domain dynamics matrix.
    Bd : 2D np.ndarray
        Discrete-domain dynamics input matrix.
    Qd : 2D np.ndarray
        Discrete-domain dynamics noise covariance matrix.

    Notes
    -----
    The Van Loan method, named after Charles Van Loan, is one way of
    discretizing the matrices of a state-space system. Suppose that you have the
    following state-space system:

        .                 .--
        x = F x + B u + `/ Q  w

        y = C x + D u + R v

    where `x` is the state vector, `u` is the input vector, and `w` is a white,
    Gaussian noise vector with means of zero and variances of one. Then, to get
    the discrete form of this equation, we would need to find `Phi`, `Bd`, and
    `Qd` such that

                             .--
        x = Phi x + Bd u + `/ Qd w

        y = C x + D u + Rd v

    `Rd` is simply `R`. `C` and `D` are unaffected by the discretization
    process. We can find `Phi` and `Qd` by doing the following:

            .-      -.                    .-          -.
            | -F  Q  |                    |  M11  M12  |
        L = |        |    M = expm(L T) = |            |
            |  0  F' |                    |  M21  M22  |
            '-      -'                    '-          -'
        Phi = M22'        Qd = Phi M12 .

    Note that `F` must be square and `Q` must have the same size as `F`. To find
    `Bd`, we do the following:

            .-      -.                    .-         -.
            |  F  B  |                    |  Phi  Bd  |
        G = |        |    H = expm(G T) = |           |
            |  0  0  |                    |   0   I   |
            '-      -'                    '-         -'

    Note that for `Bd` to be calculated, `B` must have the same number of rows
    as `F`, but need not have the same number of columns. For `Qd` to be
    calculated, `F` and `Q` must have the same shape. If these conditions are
    not met, the function will fault.

    We can also express Phi, Bd, and Qd in terms of their infinite series:

                         1   2  2    1   3  3
        Phi = I + F T + --- F  T  + --- F  T  + ...
                         2!          3!

                    1       2    1   2    3    1   3    4
        Bd = B T + --- F B T  + --- F  B T  + --- F  B T  + ...
                    2!           3!            4!

                     2                      3
                    T  .-          T -.    T  .- 2           T      T 2 -.
        Qd = Q T + --- | F Q +  Q F   | + --- | F Q + 2 F Q F  + Q F     | + ...
                    2! '-            -'    3! '-                        -'

                            2
                 .-        T  .-          T -.       -.
           = Phi |  Q T + --- |  F Q + Q F   | + ...  |
                 '-        2  '-            -'       -'

    The forward Euler method approximations to these are

        Phi = I + F T
        Bd  = B T
        Qd  = Q T

    The bilinear approximation to Phi is

                                         -1/2
        Phi = (I + 0.5 A T) (I - 0.5 A T)

    References
    ----------
    .. [1]  C. Van Loan, "Computing Integrals Involving the Matrix Exponential,"
            1976.
    .. [2]  Brown, R. and Phil Hwang. "Introduction to Random Signals and
            Applied Kalman Filtering (4th ed.)" (2012).
    .. [3]  https://en.wikipedia.org/wiki/Discretization
    """

    import scipy as sp

    # Get Phi.
    N = F.shape[1] # number of states
    Phi = sp.linalg.expm(F*T)

    # Get Bd.
    if B is not None:
        M = B.shape[1] # number of inputs
        G = np.vstack(( np.hstack((F, B)), np.zeros((M, N + M)) ))
        H = sp.linalg.expm(G*T)
        Bd = H[0:N, N:(N + M)]
    else:
        Bd = None

    # Get Qd.
    if Q is not None:
        L = np.vstack((
            np.hstack((-F, Q)),
            np.hstack(( np.zeros((N, N)), F.T)) ))
        H = sp.linalg.expm(L*T)
        Qd = Phi @ H[0:N, N:(2*N)]
    else:
        Qd = None

    return Phi, Bd, Qd

# ----------------
# Truth Generation
# ----------------

def path_box(
        seg_len: float,
        width: float = 2000.0,
        height: float = 2000.0,
        radius: float = 300.0,
        cycles: int = 3
    ) -> np.ndarray:
    """
    Define a box navigation path. Take off and landing occur in the middle of
    the south side.

    Parameters
    ----------
    seg_len : float
        Length of each uniform line segment used to render the interpolated
        curves. This length should be equal to the product of velocity and the
        sampling period.
    width : float, default 1000.0
        Width (east-west direction) of the box pattern (m).
    height : float, default 1000.0
        Height (north-south direction) of the box pattern (m).
    radius : float, default 300.0
        Radius of each rounded corner (m).
    cycles : int, default 3
        Number of cycles of the box pattern.

    Returns
    -------
    p_t : (3, K) np.ndarray
        Matrix of columns of local-level coordinates of the navigation path for
        `K` samples.
    """

    # Check the validity of the inputs.
    if (width <= 5.66*radius) or (height <= 5.66*radius):
        raise ValueError("path_box: width and height must be "
            "greater than 5.66 times radius")

    # Define the template.
    SQ2 = np.sqrt(2)
    xa, xb, xc = 2*SQ2*radius, height - 2*SQ2*radius, height
    ya, yb = width/2 - 2*SQ2*radius, width/2
    xtmp = np.array([
        0.0, 0, xa,     xb, xc, xc,     # bottom right, top right
        xc, xc, xb,     xa, 0, 0])      # top left, bottom left
    ytmp = np.array([
        ya, yb, yb,     yb, yb, ya,     # bottom right, top right
        -ya, -yb, -yb,  -yb, -yb, -ya]) # top left, bottom left

    # Initialize the waypoints array.
    cycles = int(cycles)
    points = np.zeros((2, 2 + cycles*12))

    # Define the repeating pattern.
    for cycle in range(cycles):
        # Get the indices for this copy of the pattern.
        na = 1 + cycle*12
        nb = 1 + (cycle + 1)*12

        # Define the x and y coordinates for this copy of the pattern.
        points[0, na:nb] = xtmp
        points[1, na:nb] = ytmp

    # Convert waypoints to a path.
    return waypoints(points, seg_len, radius, plot=False).path


def path_circle(
        seg_len: float,
        radius: float = 1000.0,
        cycles: int = 5
    ) -> np.ndarray:
    """
    Define a circle pattern navigation path.

    Parameters
    ----------
    seg_len : float
        Length of each uniform line segment used to render the interpolated
        curve. This length should be equal to the product of velocity and the
        sampling period.
    radius : float, default 10000.0
        Radius of the circle (m).
    cycles : int, default 3
        Number of cycles of the spiral pattern.

    Returns
    -------
    p_t : (3, K) np.ndarray
        Matrix of columns of local-level coordinates of the navigation path for
        `K` samples.
    """

    # Get the array of angles.
    dtheta = seg_len/radius
    K = round(2*np.pi/dtheta * cycles) + 1
    theta = np.arange(K) * dtheta

    # Define the path.
    p_t = np.zeros((3, K))
    p_t[0] = radius * (1.0 - np.cos(theta))
    p_t[1] = radius * np.sin(theta)

    return p_t


def path_clover(
        seg_len: float,
        radius: float = 10000.0,
        cycles: int = 3
    ) -> np.ndarray:
    """
    Define a clover pattern navigation path.

    Parameters
    ----------
    seg_len : float
        Length of each uniform line segment used to render the interpolated
        curves. This length should be equal to the product of velocity and the
        sampling period.
    radius : float, default 10000.0
        Half-width and half-height of the clover pattern (m).
    cycles : int, default 3
        Number of cycles of the spiral pattern.

    Returns
    -------
    (3, K) np.ndarray
        Matrix of columns of local-level coordinates of the navigation path for
        `K` samples.
    """

    # Define the template.
    xtmp = np.array([0.0, 1, 1, -1, -1, 0,  0, -1, -1, 1,  1,  0])
    ytmp = np.array([1.0, 1, 0,  0,  1, 1, -1, -1,  0, 0, -1, -1])

    # Initialize the waypoints array.
    cycles = int(cycles)
    points = np.zeros((2, 2 + cycles*12))

    # Define the repeating pattern.
    for cycle in range(cycles):
        # Get the indices for this copy of the pattern.
        na = 1 + cycle*12
        nb = 1 + (cycle + 1)*12

        # Define the x and y coordinates for this copy of the pattern.
        points[0, na:nb] = xtmp * radius
        points[1, na:nb] = ytmp * radius

    return waypoints(points, seg_len, 0.01, plot=False).path


def path_grid(
        seg_len: float,
        spacing: float = 300.0,
        length: float = 1600.0,
        rows: int = 6
    ) -> np.ndarray:
    """
    Define a grid pattern navigation path.

    Parameters
    ----------
    seg_len : float
        Length of each uniform line segment used to render the interpolated
        curves. This length should be equal to the product of velocity and the
        sampling period.
    spacing : float, default 300.0
        Spacing between lines of the grid pattern (m).
    length : float, default 1600.0
        Length of grid lines (m).
    rows : int, default 6
        Number of rows of the grid pattern.

    Returns
    -------
    (3, K) np.ndarray
        Matrix of columns of local-level coordinates of the navigation path for
        `K` samples.
    """

    # Define key points.
    xT = length/2
    xt = length/2 - spacing
    yj = np.arange(2, 5) * spacing

    # Initialize the waypoints array.
    J = round(rows/2)
    points = np.zeros((2, 8 + 8*J))

    # Define the first four points.
    points[:, 1:4] = np.array([
        [0.0, 0.0, spacing],
        [spacing, 2*spacing, 2*spacing]])

    # Define the repeating pattern.
    for j in range(J):
        # Get the indices for this copy of the pattern.
        na = 4 + j*8
        nb = 4 + (j + 1)*8

        # Define the x and y coordinates for this copy of the pattern.
        points[0, na:nb] = np.array([xt, xT, xT, xt,
            -xt, -xT, -xT, -xt])
        points[1, na:nb] = np.array([yj[0], yj[0], yj[1], yj[1],
            yj[1], yj[1], yj[2], yj[2]])

        # Increment the y-axis coordinates.
        yj += 2*spacing

    # Define the last four points.
    points[0, -4:] = np.array([-spacing, 0.0, 0.0, 0.0])
    points[1, -4:] = np.array([yj[0], yj[0], yj[0] - spacing, 0.0])

    # Convert waypoints to a path.
    return waypoints(points, seg_len, 0.01, plot=False).path


def path_pretzel(
        K: int,
        radius: float = 1000.0,
        height: float = 100.0,
        cycles: float = 1.0,
        twists: int = 1
    ) -> np.ndarray:
    """
    Generate a fake flight path in the shape of a pretzel (figure eight for
    twists = 1). The flight starts by heading south east from the center of the
    pretzel. The radius `radius` is the half-length of the pretzel pattern.

    Parameters
    ----------
    K : int
        Number of samples.
    radius : float, default 1000.0
        Radius of pretzel path (m).
    height : float, default 100.0
        Change in height above ellipsoidal surface (m).
    cycles : float, default 1.0
        Number of times to repeat the pattern.
    twists : int, default 1
        Number of twists in the pattern. This must be a positive odd number.

    Returns
    -------
    p_t : (3, K) np.ndarray
        Matrix of columns of local-level position vectors (m, m, m).
    """

    # Define the parametric variable.
    K = int(K) # ensure an integer
    theta = np.linspace(0, 2*np.pi, K) * cycles

    # Define the half twists.
    twists = int(twists)
    if twists % 2 == 0:
        twists += 1
    g = np.ceil(twists/2)

    # Define the coordinates.
    p_t = np.zeros((3, K))
    p_t[0] = -radius/(4*g**2) * np.sin(2*g*theta)
    p_t[1] = radius * np.sin(theta)
    p_t[2] = height*(np.cos(theta) - 1.0)/2.0

    return p_t


def path_spiral(
        seg_len: float,
        spacing: float = 300.0,
        cycles: int = 3
    ) -> np.ndarray:
    """
    Define a spiral pattern navigation path.

    Parameters
    ----------
    seg_len : float
        Length of each uniform line segment used to render the interpolated
        curves. This length should be equal to the product of velocity and the
        sampling period.
    spacing : float, default 300.0
        Spacing between lines of the grid pattern (m).
    cycles : int, default 3
        Number of cycles of the spiral pattern.

    Returns
    -------
    (3, K) np.ndarray
        Matrix of columns of local-level coordinates of the navigation path for
        `K` samples.
    """

    # Define the corners.
    xtr = np.array([0.0, spacing, spacing])
    ytr = np.array([2*spacing, 2*spacing, spacing])
    xtl = np.array([spacing, spacing, 0.0])
    ytl = np.array([0.0, -spacing, -spacing])
    xbl = np.array([0.0, -spacing, -spacing])
    ybl = np.array([-spacing, -spacing, 0.0])
    xbr = np.array([-spacing, -spacing, 0.0])
    ybr = np.array([2*spacing, 3*spacing, 3*spacing])

    # Initialize the waypoints array.
    cycles = int(cycles)
    points = np.zeros((2, 6 + cycles*12))

    # Define the first two points.
    points[:, 1] = np.array([0.0, spacing])

    # Define the repeating pattern.
    for cycle in range(cycles):
        # Get the indices for this copy of the pattern.
        na = 2 + cycle*12
        nb = 2 + (cycle + 1)*12

        # Define the x and y coordinates for this copy of the pattern.
        points[0, na:nb] = np.concatenate((xtr, xtl, xbl, xbr))
        points[1, na:nb] = np.concatenate((ytr, ytl, ybl, ybr))

        # Increment the corner coordinates.
        xtr += spacing;     ytr += spacing
        xtl += spacing;     ytl -= spacing
        xbl -= spacing;     ybl -= spacing
        xbr -= spacing;     ybr += spacing

    # Define the last four points.
    points[0, -4:] = np.array([-spacing, 0.0, 0.0, 0.0])
    points[1, -4:] = np.array([ybr[0], ybr[0], ybr[0] - spacing, 0.0])

    # Convert waypoints to a path.
    return waypoints(points, seg_len, 0.01, plot=False).path


class waypoints:
    """
    Path generation using Bezier curves from waypoints. This will create an
    interactive plot with waypoints (control points) and Bezier curves. When the
    plot is closed, the returned object will include the full path joining the
    Bezier curves. This path will be defined such that the length of each
    connected line segement will be `seg_len`.

    Left click and drag a nearby control point to move it.
    Shift, left click (or middle click) and drag to pan.
    Scroll to zoom. Hold shift to zoom faster.
    Right click to add a control point.
    Shift, right click to delete a control point.

    Attributes
    ----------
    points : (2, Np) np.ndarray
        Modified control points in local-level x and y coordinates. These are
        modified through the interactive plot.
    path : (3, K) or (K, 3) np.ndarray
        Local-level xyz coordinates of Bezier paths.
    """

    def __init__(self,
            points: np.ndarray,
            seg_len: float = 1.0,
            radius_min: float = 0.0,
            plot: bool = True,
            ax: axes= None,
            color: str = "tab:blue",
            warncolor: str = "tab:orange"
        ) -> None:
        """
        Initialize the path and plot.

        Parameters
        ----------
        points : (2, Np) or (Np, 2) np.ndarray
            Control points in local-level x (north) and y (east) coordinate
            frame (m).
        seg_len : float, default 1.0
            Length of each uniform line segment used to render the interpolated
            concatenation of the Bezier curves. This length should be equal to
            the product of velocity and the sampling period.
        radius_min : float, default 0.0
            Minimum radius of curvature (m).
        plot : bool, default True
            Flag to make an interactive plot, versus to just calculate the
            Bezier curve.
        ax : axes, default None
            MatPlotLib axes object. If none is provided, one will be generated.
        color : str, default "tab:blue"
            Color of the Bezier curves.
        warncolor : str, default "tab:orange"
            Color of the regions on the Bezier curves with a radius of curvature
            less than `radius_min`.
        """

        # Save the points.
        self.points = points
        self.tp = points.shape[0] > 2
        if self.tp:
            self.points = self.points.T

        # Save the remaining parameters.
        self.seg_len = seg_len
        self.radius_min = radius_min
        self.ax = ax
        self.color = color
        self.warncolor = warncolor

        # Define array lengths.
        self.Np = self.points.shape[1]   # number of points
        self.Nb = self.Np - 2       # number of Bezier curves
        self.Nt = 60                # number of parametric values

        # Check if there are enough points.
        if self.Np < 3:
            raise ValueError("waypoints: not enough points")

        # Initialize the states.
        self.sel = None     # selected control point
        self.shift = False  # shift key pressed
        self.no_del = False # cannot delete point

        # Define the parametric coefficients for Bezier curves.
        self.t = np.linspace(0, 1, self.Nt)
        self.t0 = (1 - self.t)**2
        self.t1 = 2*(1 - self.t)*self.t
        self.t2 = self.t**2

        # Initialize the midpoints.
        self.m = (self.points[:, :-1] + self.points[:, 1:])/2
        self.m[:, 0] = self.points[:, 0] # first midpoint
        self.m[:, -1] = self.points[:, -1] # last midpoint

        # Define the Bezier curves and radii of curvature.
        self.b = np.zeros((self.Nb, 2, self.Nt))
        self.r = np.zeros((self.Nb, self.Nt))
        for j in range(self.Nb):
            self.bezier(j)

        # If not plot should be made, just join the Bezier curves.
        if not plot:
            self.join()
            return

        # Generate a plot axis object if needed.
        if self.ax is None:
            _, self.ax = plt.subplots()

        # Plot and save the control lines.
        self.plot_cl, = self.ax.plot(self.points[1], self.points[0],
            color="#BBBBBB", linewidth=0.5)

        # Plot and save the control points.
        self.plot_cp, = self.ax.plot(self.points[1], self.points[0],
            "o", color="#BBBBBB", markerfacecolor="none")

        # Plot and save the no-delete marker.
        self.plot_nd, = self.ax.plot([], [],
            "x", color="#FF0000")

        # Initialize the Bezier plot curves.
        self.plot_bc = [] # main Bezier curves
        self.plot_bf = [] # failure curves (less than min radius of curvature)
        for j in range(self.Nb):
            bc, = self.ax.plot([], [], color=self.color)
            bf, = self.ax.plot([], [], color=self.warncolor, linewidth=3)
            self.plot_bc.append(bc)
            self.plot_bf.append(bf)
            self.update_bezier_plot(j)

        # Link mouse events to methods.
        self.canvas = self.ax.figure.canvas
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.canvas.mpl_connect("key_release_event", self.on_key_release)
        self.canvas.mpl_connect("resize_event", self.on_resize)
        self.canvas.mpl_connect("close_event", self.on_close)

        # Set equal axis scaling.
        self.ax.set_aspect("equal")

        # Set the view.
        self.fig = self.ax.figure
        self.home()

        # Set the grid.
        self.ax.grid(visible=True, color="#CCCCCC", linewidth=0.2)

        # Remove x and y labels
        self.ax.set_xlabel("")
        self.ax.set_ylabel("")

        # Move tick labels inside.
        self.ax.tick_params(axis="x", direction="in", bottom=False, pad=-15)
        self.ax.tick_params(axis="y", direction="in", left=False, pad=-45)

        # Remove white space around plot.
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Remove the box by hiding all spines.
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)

        # Render.
        plt.show()

    def home(self) -> None:
        """ Set the view to the limits of the data with padding. """

        # Get the midpoint and desired span of the view.
        xmin, xmax = self.points[1].min(), self.points[1].max()
        ymin, ymax = self.points[0].min(), self.points[0].max()
        xmid, ymid = (xmin + xmax)/2, (ymin + ymax)/2
        xspan, yspan = 1.2*(xmax - xmin), 1.2*(ymax - ymin)

        # Adjust the span to fit the figure window aspect ratio.
        wfig, hfig = self.fig.get_size_inches()
        if wfig/hfig > xspan/yspan:
            xspan = yspan * wfig/hfig
        else:
            yspan = xspan * hfig/wfig

        # Set the view limits.
        xlim = xmid - 0.5*xspan, xmid + 0.5*xspan
        ylim = ymid - 0.5*yspan, ymid + 0.5*yspan
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.xlim_home = self.ax.get_xlim()
        self.ylim_home = self.ax.get_ylim()
        self.is_home = True

    def resize(self) -> None:
        """ Set the view to the limits of the data with padding. """

        # Get the midpoint and desired span of the view.
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        xmid, ymid = (xmin + xmax)/2, (ymin + ymax)/2
        xspan, yspan = (xmax - xmin), (ymax - ymin)

        # Adjust the span to fit the figure window aspect ratio.
        wfig, hfig = self.fig.get_size_inches()
        if wfig/hfig > xspan/yspan:
            xspan = yspan * wfig/hfig
        else:
            yspan = xspan * hfig/wfig

        # Set the view limits.
        xlim = xmid - 0.5*xspan, xmid + 0.5*xspan
        ylim = ymid - 0.5*yspan, ymid + 0.5*yspan
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.xlim_home = self.ax.get_xlim()
        self.ylim_home = self.ax.get_ylim()

    def bezier(self,
            j: int
        ) -> None:
        """ Calculate the jth Bezier curve and its radius of curvature. """

        # Define start, control, and end points for this segment.
        P0 = self.m[:, j]      # previous midpoint
        P1 = self.points[:, j + 1]  # control point
        P2 = self.m[:, j + 1]  # next midpoint

        # Define the Bezier curve segment.
        self.b[j, 0] = self.t0 * P0[0] + self.t1 * P1[0] + self.t2 * P2[0]
        self.b[j, 1] = self.t0 * P0[1] + self.t1 * P1[1] + self.t2 * P2[1]

        # Define the radius of curvature.
        Dx = 2*(1 - self.t)*(P1[0] - P0[0]) + 2*self.t*(P2[0] - P1[0])
        Dy = 2*(1 - self.t)*(P1[1] - P0[1]) + 2*self.t*(P2[1] - P1[1])
        Dx2 = 2*(P2[0] - 2*P1[0] + P0[0])
        Dy2 = 2*(P2[1] - 2*P1[1] + P0[1])
        num = np.sqrt(Dx**2 + Dy**2)**3
        den = np.abs(Dx*Dy2 - Dy*Dx2)
        den = np.clip(den, 1e-9, None)
        self.r[j] = np.abs(num)/den

    def update_bezier_plot(self,
            j: int
        ) -> None:
        """ Update the jth Bezier curve plot. """

        # Get the data.
        x = self.b[j, 0]
        y = self.b[j, 1]
        r = self.r[j]

        # Get the points of low radii of curvature.
        is_fail = r < self.radius_min

        # Update the plot data.
        self.plot_bc[j].set_data(y, x)
        self.plot_bf[j].set_data(y[is_fail], x[is_fail])

    def join(self) -> None:
        """ Join the several Bezier curves together into one path. """

        # Concatenate the Bezier curves together.
        x = np.zeros(self.Nb*self.Nt)
        y = np.zeros(self.Nb*self.Nt)
        for j in range(self.Nb):
            na = j*self.Nt
            nb = (j+1)*self.Nt
            x[na:nb] = self.b[j, 0]
            y[na:nb] = self.b[j, 1]

        # Reinterpolate x and y for uniform spacing.
        for n in range(100):
            # Get distance traveled.
            dx = np.diff(x)
            dy = np.diff(y)
            dr = np.sqrt(dx**2 + dy**2)

            # Early exit if all segments are within tolerance.
            if np.abs(self.seg_len - dr).max() < 1e-10:
                break

            # Reinterpolate to get uniform spacing.
            r = np.insert(np.cumsum(dr), 0, 0.0)
            if n == 0:
                K = round(r[-1]/self.seg_len) + 1
                rr = np.arange(K) * self.seg_len
            x = np.interp(rr, r, x)
            y = np.interp(rr, r, y)

            # Fix the end point.
            dx = x[-1] - x[-2]
            dy = y[-1] - y[-2]
            dr = math.sqrt(dx**2 + dy**2)
            if dr > 0.0:
                x[-1] = x[-2] + dx/dr * self.seg_len
                y[-1] = y[-2] + dy/dr * self.seg_len

        # Save to self.
        self.path = np.array((x, y, np.zeros(K)))
        if self.tp:
            self.path = self.path.T

    def on_press(self,
            event: MouseEvent
        ) -> None:
        """
        Left-mouse click:
            Begin control-point move.

        Shift, left-mouse click or middle click:
            Begin click and drag to pan view.

        Right-mouse click:
            Create new control point.

        Shift, right-mouse click:
            Delete control point.
        """

        # Exit if mouse is outside canvas.
        if event.inaxes != self.ax:
            return

        # Depending on which mouse button is pressed,
        if event.button == 1: # left mouse button
            if self.shift: # If shift key is down, begin view panning.
                # Remember where the click was.
                self.x_on_press = event.xdata
                self.y_on_press = event.ydata
                self.xlim_on_press = self.ax.get_xlim()
                self.ylim_on_press = self.ax.get_ylim()

            else: # If shift key is not down, begin control-point move.
                # Clear no-delete point.
                if self.no_del:
                    self.no_del = False
                    self.plot_nd.set_data([], [])

                # Find the control point closest to the mouse.
                dx = event.ydata - self.points[0]
                dy = event.xdata - self.points[1]
                r = np.sqrt(dx**2 + dy**2)
                self.sel = np.argmin(r)

                # Move the control point to the mouse.
                self.on_motion(event)

        elif event.button == 2: # If middle mouse button, begin view panning.
            # Remember where the click was.
            self.x_on_press = event.xdata
            self.y_on_press = event.ydata
            self.xlim_on_press = self.ax.get_xlim()
            self.ylim_on_press = self.ax.get_ylim()

        elif event.button == 3: # right mouse button
            if self.shift: # If shift key is down, delete control point.
                # Find the control point closest to the mouse.
                dx = event.ydata - self.points[0]
                dy = event.xdata - self.points[1]
                r = np.sqrt(dx**2 + dy**2)
                i = np.argmin(r)

                # Show no-delete point if needed.
                if self.Np <= 3:
                    self.no_del = True
                    self.plot_nd.set_data(
                        [self.points[1, i]], [self.points[0, i]])
                    return
                elif self.no_del:
                    self.no_del = False
                    self.plot_nd.set_data([], [])

                # Delete the control point.
                self.points = np.delete(self.points, i, axis=1)
                self.plot_cp.set_data(self.points[1], self.points[0])
                self.plot_cl.set_data(self.points[1], self.points[0])
                self.Np -= 1

                # Delete the midpoint before.
                j = i - 1 if i > 1 else i
                self.m = np.delete(self.m, j, axis=1)

                # Move the midpoint after, if not second or second to last.
                if (i != 1) and (i != self.Np - 1):
                    if i == 0: # first point
                        self.m[:, 0] = self.points[:, 0]
                    elif i == self.Np: # last point
                        self.m[:, self.Np - 2] = self.points[:, self.Np - 1]
                    else: # any other point
                        self.m[:, i - 1] = (self.points[:, i - 1]
                            + self.points[:, i])/2

                # Delete the corresponding Bezier curve.
                j = min(max(i - 1, 0), self.Np - 2)
                self.b = np.delete(self.b, j, axis=0)
                self.r = np.delete(self.r, j, axis=0)
                self.plot_bc[j].remove()
                self.plot_bc.pop(j)
                self.plot_bf[j].remove()
                self.plot_bf.pop(j)
                self.Nb -= 1

                # Move the Bezier curve before.
                if i > 1:
                    j = min(i - 2, self.Np - 3)
                    self.bezier(j)
                    self.update_bezier_plot(j)

                # Move the Bezier curve after.
                if i < self.Np - 1:
                    j = max(i - 1, 0)
                    self.bezier(j)
                    self.update_bezier_plot(j)

            else: # If shift key is not down, create new control point.
                # Clear no-delete point.
                if self.no_del:
                    self.no_del = False
                    self.plot_nd.set_data([], [])

                # Get the mouse location.
                x, y = event.ydata, event.xdata

                # Extract the coordinates of the control points.
                x1, y1 = self.points[:, :-1]
                x2, y2 = self.points[:, 1:]

                # Vector from first control point to point of interest
                dx1 = x - x1
                dy1 = y - y1

                # Vector from first to second control point
                dx21 = x2 - x1
                dy21 = y2 - y1

                # Calculate the projection parameter.
                len_sq = np.clip(dx21**2 + dy21**2, 1e-9, None)
                dot = dx1 * dx21 + dy1 * dy21
                t = np.clip(dot / len_sq, 0.0, 1.0)

                # Find the closest point on the line segment.
                xp = x1 + t * dx21
                yp = y1 + t * dy21

                # Calculate the distance to the closest point.
                dist = np.sqrt((x - xp)**2 + (y - yp)**2)

                # Get the index of the closest line segment.
                i = np.argmin(dist)

                # Make this the selected control point.
                self.sel = i + 1

                # Insert the new point before the next control point.
                pi = np.array([event.ydata, event.xdata])
                self.points = np.insert(self.points, i + 1, pi, axis=1)
                self.plot_cp.set_data(self.points[1], self.points[0])
                self.plot_cl.set_data(self.points[1], self.points[0])
                self.Np += 1

                # Move midpoint i and insert new midpoint before i + 1.
                if i > 0:
                    self.m[:, i] = (self.points[:, i] + self.points[:, i + 1])/2
                mi = self.points[:, i + 2] if (i == self.Np - 3) \
                    else (self.points[:, i + 1] + self.points[:, i + 2])/2
                self.m = np.insert(self.m, i + 1, mi, axis=1)

                # Insert new Bezier curve before i.
                self.b = np.insert(self.b, i, np.zeros((2, self.Nt)), axis=0)
                self.r = np.insert(self.r, i, np.zeros(self.Nt), axis=0)
                bc, = self.ax.plot([], [], color=self.color)
                bf, = self.ax.plot([], [], color=self.warncolor, linewidth=3)
                self.plot_bc.insert(i, bc)
                self.plot_bf.insert(i, bf)
                self.Nb += 1

                # Update the Bezier curves.
                for j in range(i - 1, i + 2):
                    if j < 0 or j >= self.Nb:
                        continue
                    self.bezier(j)
                    self.update_bezier_plot(j)

            # Refresh the drawing.
            self.canvas.draw_idle()

    def on_motion(self,
            event: MouseEvent
        ) -> None:
        """
        Shift, left-mouse drag or middle click:
            Pan the view.

        Otherwise:
            Move the selected control point.
        """

        # Exit if mouse is outside canvas.
        if event.inaxes != self.ax:
            return

        # Drag view.
        if (self.shift and event.button == 1) or (event.button == 2):
            # Get the change in mouse position.
            dx = event.xdata - self.x_on_press
            dy = event.ydata - self.y_on_press

            # Adjust the view limits.
            self.xlim_on_press -= dx
            self.ylim_on_press -= dy
            self.ax.set_xlim(self.xlim_on_press)
            self.ax.set_ylim(self.ylim_on_press)

            # Set to no longer in home view.
            self.is_home = False

        # Move control point.
        elif self.sel is not None:
            # Move the control point to the mouse location.
            i = self.sel
            y_mouse = np.round(event.ydata, 4)
            x_mouse = np.round(event.xdata, 4)
            self.points[:, i] = [y_mouse, x_mouse]

            # Move the previous midpoint.
            if i > 1:
                if i == self.Np - 1:
                    self.m[:, i - 1] = self.points[:, i]
                else:
                    self.m[:, i - 1] = (self.points[:, i - 1]
                        + self.points[:, i])/2

            # Move the next midpoint.
            if i < self.Np - 2:
                if i == 0:
                    self.m[:, i] = self.points[:, i]
                else:
                    self.m[:, i] = (self.points[:, i] + self.points[:, i + 1])/2

            # Update the sets of control points and lines.
            self.plot_cp.set_data(self.points[1], self.points[0])
            self.plot_cl.set_data(self.points[1], self.points[0])

            # Update the middle and adjacent Bezier curves.
            for j in [i - 2, i - 1, i]:
                if (j < 0) or (j >= self.Nb):
                    continue
                self.bezier(j)
                self.update_bezier_plot(j)

        # Refresh the drawing.
        self.canvas.draw_idle()

    def on_release(self,
            _event: MouseEvent
        ) -> None:
        """ Unselect any selected control point and reset the view. """

        # Unselect control point.
        self.sel = None

        # Reset the view.
        if self.is_home:
            self.home()
            self.canvas.draw_idle()

    def on_scroll(self,
            event: ScrollEvent
        ) -> None:
        """
        Zoom view centered on the mouse location.
        Hold shift to zoom faster.
        """

        # Exit if mouse is outside canvas.
        if event.inaxes != self.ax:
            return

        # Get the zoom factor.
        self.is_home = False
        factor = 0.8 if self.shift else 0.95
        if event.button == "down":
            factor = 1/factor

        # Get the current view limits.
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        # Get the new zoomed span.
        dx = (xmax - xmin)*factor
        dy = (ymax - ymin)*factor

        # Get the relative postion of the cursor within the view.
        rx = (event.xdata - xmin)/(xmax - xmin)
        ry = (event.ydata - ymin)/(ymax - ymin)

        # Get the new view limits.
        xmin = event.xdata - dx*(rx)
        xmax = event.xdata + dx*(1 - rx)
        ymin = event.ydata - dy*(ry)
        ymax = event.ydata + dy*(1 - ry)

        # Set the new axis limits.
        self.ax.set_xlim([xmin, xmax])
        self.ax.set_ylim([ymin, ymax])
        self.canvas.draw_idle()

    def on_key_press(self,
            event: KeyEvent
        ) -> None:
        """ Register shift key press or reset view on "h" key. """

        if event.key == "shift":
            self.shift = True
        elif event.key == "h": # Reset the view.
            self.home()
            self.canvas.draw_idle()

    def on_key_release(self,
            event: KeyEvent
        ) -> None:
        """ Unregister shift key press. """

        if event.key == "shift":
            self.shift = False

    def on_resize(self,
            _event: ResizeEvent
        ) -> None:
        """
        On window resize, maintain the view as either the limits of the data
        with padding or the current view.
        """

        if self.is_home:
            self.home()
        else:
            self.resize()
        self.canvas.draw_idle()

    def on_close(self,
            _event: CloseEvent
        ) -> None:
        """ Join the Bezier curves when closing the plot. """

        self.join()


def llh_to_vne(
        llh_t: np.ndarray,
        T: float
    ) -> np.ndarray:
    """
    Convert geodetic position over time to velocity of the navigation frame
    relative to the earth frame over time. Geodetic position is quadratically
    extrapolated by one sample.

    Parameters
    ----------
    llh_t : (3, K) or (K, 3) np.ndarray
        Matrix of geodetic position vectors of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    T : float
        Sampling period in seconds.

    Returns
    -------
    vne_t : (3, K) or (K, 3) np.ndarray
        Matrix of velocity vectors.
    """

    # Check input.
    if isinstance(llh_t, (list, tuple)):
        llh_t = np.array(llh_t)
    trs = (llh_t.ndim == 2 and llh_t.shape[0] != 3)

    # Transpose input.
    if trs:
        llh_t = llh_t.T

    # Parse geodetic position.
    lat = llh_t[0]
    lon = llh_t[1]
    hae = llh_t[2]

    # Extended derivatives
    if llh_t.shape[1] >= 3: # quadratic extrapolation
        lat_ext = 3*lat[-1] - 3*lat[-2] + lat[-3]
        lon_ext = 3*lon[-1] - 3*lon[-2] + lon[-3]
        hae_ext = 3*hae[-1] - 3*hae[-2] + hae[-3]
    else: # linear extrapolation
        lat_ext = 2*lat[-1] - lat[-2]
        lon_ext = 2*lon[-1] - lon[-2]
        hae_ext = 2*hae[-1] - hae[-2]
    Dlat = np.diff(np.append(lat, lat_ext))/T
    Dlon = np.diff(np.append(lon, lon_ext))/T
    Dhae = np.diff(np.append(hae, hae_ext))/T

    # Trig of latitude
    clat = np.cos(llh_t[0]) # (K,)
    slat = np.sin(llh_t[0]) # (K,)

    # Rotation rate of navigation frame relative to earth frame,
    # referenced in the navigation frame
    wnne_x = clat*Dlon
    wnne_y = -Dlat

    # Velocity of the navigation frame relative to the earth frame,
    # referenced in the navigation frame
    klat = np.sqrt(1 - E2*slat**2)
    Rt = A_E/klat
    Rm = (Rt/klat**2)*(1 - E2)
    vN = -wnne_y*(Rm + hae)
    vE =  wnne_x*(Rt + hae)
    vD = -Dhae
    vne_t = np.array((vN, vE, vD))

    # Transpose output.
    if trs:
        vne_t = vne_t.T

    return vne_t


def somigliana(
        llh: np.ndarray
    ) -> np.ndarray:
    """
    Calculate the local acceleration of gravity vector in the navigation frame
    using the Somigliana equation. The navigation frame here has the North,
    East, Down (NED) orientation.

    Parameters
    ----------
    llh : (3,) or (3, K) or (K, 3) np.ndarray
        Geodetic position vector of latitude (radians), longitude (radians), and
        height above ellipsoid (meters) or matrix of such vectors.

    Returns
    -------
    gamma : (3,) or (3, K) or (K, 3) np.ndarray
        Acceleration of gravity in meters per second squared.
    """

    # Check input.
    if isinstance(llh, (list, tuple)):
        llh = np.array(llh)
    trs = (llh.ndim == 2 and llh.shape[0] != 3)

    # Transpose input.
    if trs:
        llh = llh.T

    # Get local acceleration of gravity for height equal to zero.
    slat2 = np.sin(llh[0])**2
    klat = np.sqrt(1 - E2*slat2)
    grav_z0 = GRAV_E*(1 + GRAV_K*slat2)/klat

    # Calculate gamma for the given height.
    grav_z = grav_z0*(1 + (3/A_E**2)*llh[2]**2
        - 2/A_E*(1 + GRAV_F + GRAV_M - 2*GRAV_F*slat2)*llh[2])

    # Form vector.
    if np.ndim(grav_z) > 0:
        K = len(grav_z)
        grav = np.zeros((3, K))
        grav[2, :] = grav_z
    else:
        grav = np.array([0.0, 0.0, grav_z])

    # Transpose output.
    if trs:
        grav = grav.T

    return grav


def vne_to_rpy(
        vne_t: np.ndarray,
        grav_t: np.ndarray,
        T: float,
        alpha: float = 0.06,
        wind: np.ndarray = None
    ) -> np.ndarray:
    """
    Estimate the attitude angles in radians based on velocity.

    Parameters
    ----------
    vne_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of velocity of the navigation frame relative to the
        ECEF frame (meters per second).
    grav_t : float or (K,) np.ndarray
        Local acceleration of gravity magnitude in meters per second
        squared. If grav_t is 2D, the vector norm will be used.
    T : float
        Sampling period in seconds.
    alpha : float, default 0.06
        Angle of attack in radians.
    wind : (2,) or (2, K) np.ndarray, default None
        Horizontal velocity vector of wind in meters per second.

    Returns
    -------
    rpy_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of attitude angles roll, pitch, and yaw, all in
        radians. These angles are applied in the context of a North, East, Down
        navigation frame to produce the body frame in a zyx sequence of passive
        rotations.
    """

    # Check input.
    if isinstance(vne_t, (list, tuple)):
        vne_t = np.array(vne_t)
    if isinstance(grav_t, (int, float)):
        grav_t = np.array([float(grav_t)])
    elif isinstance(grav_t, (list, tuple)):
        grav_t = np.array(grav_t)
    trs = (vne_t.ndim == 2 and vne_t.shape[0] != 3)
    if grav_t.ndim == 2:
        if grav_t.shape[0] == 3:
            grav_t = np.linalg.norm(grav_t, axis=0)
        else:
            grav_t = np.linalg.norm(grav_t, axis=1)

    # Transpose input.
    if trs:
        vne_t = vne_t.T

    # Filter the velocity.
    vN, vE, vD = vne_t

    # Get the horizontal velocity.
    vH = np.sqrt(vN**2 + vE**2)

    # Check if there is horizontal motion.
    isH = np.clip(1 - np.exp(-vH), 0.0, 1.0)

    # Estimate the yaw.
    if wind is None:
        yaw = np.arctan2(vE, vN)*isH
    else:
        yaw = np.arctan2(vE - wind[1], vN - wind[0])*isH
        # Inversely, the wind can be estimated with
        # | sh = sqrt(vx^2 + vy^2)
        # | wx = vx - sh cos(yaw)
        # | wy = vy - sh sin(yaw)

    # Estimate the pitch.
    pit = np.arctan(-(vD * isH)/(vH + (1 - isH))) + alpha * isH

    # Estimate the roll.
    aN = np.gradient(vN)/T # x-axis acceleration
    aE = np.gradient(vE)/T # y-axis acceleration
    ac = (vN*aE - vE*aN)/(vH + 1e-4) # cross product vH with axy
    rol = np.arctan(ac/grav_t) * isH

    # Assemble.
    rpy_t = np.vstack((rol, pit, yaw))

    # Transpose output.
    if trs:
        rpy_t = rpy_t.T

    return rpy_t


def llh_to_tva(
        llh_t: np.ndarray,
        T: float
    ) -> np.ndarray:
    """
    Generate time, velocity, and attitude from a path and sampling period.

    Parameters
    ----------
    llh_t : (3, K) np.ndarray
        Matrix of columns of position vectors (rad, rad, m).
    T : float
        Sampling period (s).

    Returns
    -------
    t : (K,) np.ndarray
        Array of time values (s).
    vne_t : (3, K) np.ndarray
        Matrix of columns of velocity vectors (m/s).
    rpy_t : (3, K) np.ndarray
        Matrix of columns of roll, pitch, and yaw attitude vectors (rad).
    """

    # Check input.
    trs = (llh_t.ndim == 2 and llh_t.shape[0] != 3)

    # Transpose input.
    if trs:
        llh_t = llh_t.T

    # Define time.
    K = llh_t.shape[1]
    t = np.arange(K)*T

    # Estimate velocity and attitude.
    vne_t = llh_to_vne(llh_t, T)
    grav_t = somigliana(llh_t)
    rpy_t = vne_to_rpy(vne_t, grav_t[2, :], T)

    # Transpose output.
    if trs:
        vne_t = vne_t.T
        rpy_t = rpy_t.T

    return t, vne_t, rpy_t


def noise_fogm(
        T: float,
        tau: float,
        var: float,
        K: int
    ) -> np.ndarray:
    """
    Generate first-order, Gauss-Markov (FOGM) noise.

    Parameters
    ----------
    T : float
        Sampling period (s).
    tau : float
        Time constant (s).
    var : float
        Variance.
    K : int
        Number of noise samples.
    """

    # Define scaling factors.
    ka = math.exp(-T/tau)
    kb = math.sqrt(var*(1 - math.exp(-2*T/tau)))

    # Define the noise array.
    K = int(K)
    eta = kb*np.random.randn(K)

    # Initialize the state.
    x = np.sqrt(var)*eta[-1] # state

    # Process through time.
    y = np.zeros(K)
    for k in range(K):
        y[k] = x
        x = ka*x + eta[k]

    return y

# -------------
# Mechanization
# -------------

def mech_inv(
        llh_t: np.ndarray,
        rpy_t: np.ndarray,
        T: float,
        grav_model: Callable[[np.ndarray], np.ndarray] = somigliana
    ) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute the inverse mechanization of pose to get inertial measurement unit
    sensor values.

    Parameters
    ----------
    llh_t : (3, K) or (K, 3) np.ndarray
        Matrix of geodetic positions in terms of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    rpy_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of attitude angles roll, pitch, and yaw, all in
        radians. These angles are applied in the context of a North, East, Down
        navigation frame to produce the body frame in a zyx sequence of passive
        rotations.
    T : float
        Sampling period in seconds.
    grav_model : function, default somigliana
        The gravity model function to use. This function should be able to take
        a matrix of position vectors in terms of latitude (radians), longitude
        (radians), and height above ellipsoid (meters) and return a matrix of
        the same shape representing the local acceleration of gravity vectors
        (meters per second squared) in the navigation frame with a North, East,
        Down (NED) orientation.

    Returns
    -------
    fbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of specific force vectors (meters per second squared) of the body
        frame relative to the inertial frame, referenced in the body frame.
    wbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of rotation rate vectors (radians per second) of the body frame
        relative to the inertial frame, referenced in the body frame.

    Notes
    -----
    The function internally calculates the velocity vector from the position
    vector.

    This algorithm uses the forward Euler differential in order to be a perfect
    dual with the forward mechanization algorithm which uses the forward Euler
    integral. As a consequence, the estimated sensor values lead the pose
    (position, velocity, and attitude) values by a small amount of time because
    they are informed by future pose values. Specifically, the rotation rates
    will lead by half a sampling period and the specific forces will lead by a
    full sampling period.

    This function is not a perfect dual of the forward mechanization algorithm
    if a barometric altitude aiding model was used.
    """

    # Check input.
    if isinstance(llh_t, (list, tuple)):
        llh_t = np.array(llh_t)
    if isinstance(rpy_t, (list, tuple)):
        rpy_t = np.array(rpy_t)
    trs = (llh_t.ndim == 2 and llh_t.shape[0] != 3)

    # Transpose input.
    if trs:
        llh_t = llh_t.T
        rpy_t = rpy_t.T

    # Number of points in time
    K = llh_t.shape[1]

    # Trig of latitude
    clat = np.cos(llh_t[0]) # (K,)
    slat = np.sin(llh_t[0]) # (K,)

    # Unwrap the attitude angles so that
    # the extrapolation below works correctly.
    rpy_t = np.unwrap(rpy_t, axis=1)

    # Derivative of position
    llh_ext = 3*llh_t[:, -1] - 3*llh_t[:, -2] + llh_t[:, -3] # (3,)
    Dllh = np.diff(np.column_stack((llh_t, llh_ext)), axis=1)/T # (3, K)

    # Rotation rate of navigation frame relative to earth frame,
    # referenced in the navigation frame
    wnne = np.array([
        clat*Dllh[1],
        -Dllh[0],
        -slat*Dllh[1]]) # (3, K)

    # Velocity of the navigation frame relative to the earth frame,
    # referenced in the navigation frame
    klat = np.sqrt(1 - E2*slat**2) # (K,)
    Rt = A_E/klat # (K,)
    Rm = (Rt/klat**2)*(1 - E2) # (K,)
    vne = np.array([
        -wnne[1]*(Rm + llh_t[2]),
        wnne[0]*(Rt + llh_t[2]),
        -Dllh[2]]) # (3, K)

    # Derivative of velocity
    vne_ext = 3*vne[:, -1] - 3*vne[:, -2] + vne[:, -3] # (3,)
    Dvne = np.diff(np.column_stack((vne, vne_ext)), axis=1)/T # (3, K)

    # Rotation matrices
    Cbn = r3f.rpy_to_dcm(rpy_t) # (K, 3, 3)
    Cbn_ext = Cbn[K-1] @ Cbn[K-2].T @ Cbn[K-1] # (3, 3)
    Cbn = np.concatenate((Cbn, Cbn_ext[None, :, :]), axis=0) # (K+1, 3, 3)
    Cnb = np.transpose(Cbn, (0,2,1)) # (K+1, 3, 3)

    # Navigation to body rotation rate via inverse Rodrigues rotation
    D = Cbn[:-1] @ Cnb[1:] # (K, 3, 3)
    d11 = D[:, 0, 0];   d12 = D[:, 0, 1];   d13 = D[:, 0, 2] # (K,)
    d21 = D[:, 1, 0];   d22 = D[:, 1, 1];   d23 = D[:, 1, 2] # (K,)
    d31 = D[:, 2, 0];   d32 = D[:, 2, 1];   d33 = D[:, 2, 2] # (K,)
    q = d11 + d22 + d33 # trace of D (K,)
    q_min = 2*math.cos(3.1415926) + 1
    q = q*(q <= 3)*(q >= q_min) + 3.0*(q > 3) + q_min*(q < q_min) # (K,)
    ang = np.arccos((q-1)/2) # angle of rotation (K,)
    k = ang/np.sqrt(3 + 2*q - q**2 + (q > 2.9995))*(q <= 2.9995) \
        + (q**2 - 11*q + 54)/60*(q > 2.9995) # scaling factor (K,)
    # This is really wbbn, but it will be used to build wbbi.
    wbbi_t = k*np.array([d32 - d23, d13 - d31, d21 - d12])/T # (3, K)

    # Rotation rates
    wnei = np.array([
        W_EI*clat,
        np.zeros(K),
        -W_EI*slat]) # (3, K)
    w = wnne + wnei
    # Matrix product of Cbn with w. This is now truly wbbi.
    wbbi_t[0] += Cbn[:-1, 0, 0]*w[0] + Cbn[:-1, 0, 1]*w[1] + Cbn[:-1, 0, 2]*w[2]
    wbbi_t[1] += Cbn[:-1, 1, 0]*w[0] + Cbn[:-1, 1, 1]*w[1] + Cbn[:-1, 1, 2]*w[2]
    wbbi_t[2] += Cbn[:-1, 2, 0]*w[0] + Cbn[:-1, 2, 1]*w[1] + Cbn[:-1, 2, 2]*w[2]

    # Specific force
    w += wnei
    grav = grav_model(llh_t) # (3, K)
    fnbi = Dvne - grav # (3, K)
    # Cross product of w with vne
    fnbi[0] += w[1]*vne[2] - w[2]*vne[1]
    fnbi[1] += w[2]*vne[0] - w[0]*vne[2]
    fnbi[2] += w[0]*vne[1] - w[1]*vne[0]
    fbbi_t = np.zeros((3, K))
    # Matrix product of Cbn with fnbi
    fbbi_t[0, :] = Cbn[:-1, 0, 0]*fnbi[0] \
        + Cbn[:-1, 0, 1]*fnbi[1] \
        + Cbn[:-1, 0, 2]*fnbi[2]
    fbbi_t[1, :] = Cbn[:-1, 1, 0]*fnbi[0] \
        + Cbn[:-1, 1, 1]*fnbi[1] \
        + Cbn[:-1, 1, 2]*fnbi[2]
    fbbi_t[2, :] = Cbn[:-1, 2, 0]*fnbi[0] \
        + Cbn[:-1, 2, 1]*fnbi[1] \
        + Cbn[:-1, 2, 2]*fnbi[2]

    # Transpose output.
    if trs:
        fbbi_t = fbbi_t.T
        wbbi_t = wbbi_t.T

    return fbbi_t, wbbi_t


def mech(
        fbbi_t: np.ndarray,
        wbbi_t: np.ndarray,
        llh0: np.ndarray,
        vne0: np.ndarray,
        rpy0: np.ndarray,
        T: float,
        hae_t: np.ndarray | None = None,
        baro_name: str | None = None,
        grav_model: Callable[[np.ndarray], np.ndarray] = somigliana
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute the forward mechanization of inertial measurement unit sensor values
    to get pose.

    Parameters
    ----------
    fbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of specific force vectors (meters per second squared) of the body
        frame relative to the inertial frame, referenced in the body frame.
    wbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of rotation rate vectors (radians per second) of the body frame
        relative to the inertial frame, referenced in the body frame.
    llh0 : (3,) np.ndarray
        Initial geodetic position of latitude (radians), longitude (radians),
        and height above ellipsoid (meters).
    vne0 : (3,) np.ndarray
        Initial velocity vector (meters per second) in North, East, and Down
        (NED) directions.
    rpy0 : (3,) np.ndarray
        Initial roll, pitch, and yaw angles in radians. These angles are applied
        in the context of a North, East, Down (NED) navigation frame to produce
        the body frame in a zyx sequence of passive rotations.
    T : float
        Sampling period in seconds.
    hae_t : (K,) np.ndarray, default None
        External source of altitude. If `baro_name` is `None`, `hae_t` directly
        overrides the height. If `baro_name` is any of the accepted strings,
        `hae_t` represents the barometric altimeter data.
    baro_name : str, default None
        The name of the barometric altitude aiding model. Current models are
        third-order with specific tuning coefficients: "savage", "rogers",
        "widnall", "silva", "iae", "ise", "itae", and "itse". If the
        `baro_name` is `None`, the height is directly overridden using `hae_t`.
    grav_model : function, default somigliana
        The gravity model function to use. This function should take a position
        vector of latitude (radians), longitude (radians), and height above
        ellipsoid (meters) and return the local acceleration of gravity vector
        (meters per second squared) in the navigation frame with a North, East,
        Down (NED) orientation.

    Returns
    -------
    llh_t : (3, K) or (K, 3) np.ndarray
        Matrix of geodetic positions in terms of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    vne_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of velocity of the navigation frame relative to the
        ECEF frame (meters per second).
    rpy_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of attitude angles roll, pitch, and yaw, all in
        radians. These angles are applied in the context of a North, East, Down
        navigation frame to produce the body frame in a zyx sequence of passive
        rotations.
    """

    # Check the inputs.
    if isinstance(fbbi_t, (list, tuple)):
        fbbi_t = np.array(fbbi_t)
    if isinstance(wbbi_t, (list, tuple)):
        wbbi_t = np.array(wbbi_t)
    if isinstance(llh0, (list, tuple)):
        llh0 = np.array(llh0)
    if isinstance(vne0, (list, tuple)):
        vne0 = np.array(vne0)
    if isinstance(rpy0, (list, tuple)):
        rpy0 = np.array(rpy0)
    trs = (fbbi_t.ndim == 2 and fbbi_t.shape[0] != 3)

    # Initialize states.
    llh = llh0.copy()
    vne = vne0.copy()
    Cnb = r3f.rpy_to_dcm(rpy0).T

    # Transpose input.
    if trs:
        fbbi_t = fbbi_t.T
        wbbi_t = wbbi_t.T

    # Precalculate vertical velocity override or init baro model.
    override = False
    baro = None
    if hae_t is not None:
        if baro_name is None:
            override = True
            vD_t = np.zeros(len(hae_t))
            vD_t[:-1] = -np.diff(hae_t)/T
            # Second-order extrapolation
            vD_t[-1] = 2*vD_t[-2] - vD_t[-3]
        else:
            baro = Baro(baro_name)

    # Storage
    K = fbbi_t.shape[1]
    llh_t = np.zeros((3, K))
    vne_t = np.zeros((3, K))
    rpy_t = np.zeros((3, K))

    # Get the coefficients for when to show progress.
    pa = math.ceil(K/100)
    pb = K - math.floor(K/pa)*pa

    # Time loop
    for k in range(K):
        # Inputs
        fbbi = fbbi_t[:, k]
        wbbi = wbbi_t[:, k]

        # Override height and velocity.
        if override:
            llh[2] = hae_t[k]
            vne[2] = vD_t[k]

        # Results storage
        llh_t[:, k] = llh
        vne_t[:, k] = vne
        rpy_t[:, k] = r3f.dcm_to_rpy(Cnb.T)

        # Get the derivatives.
        if baro is None:
            Dllh, Dvne, wbbn = mech_step(fbbi, wbbi,
                llh, vne, Cnb, grav_model=grav_model)
        else:
            Dllh, Dvne, wbbn = mech_step(fbbi, wbbi,
                llh, vne, Cnb, hae_t[k], baro, grav_model=grav_model)

        # Integrate.
        llh += Dllh * T
        vne += Dvne * T
        Cnb[:, :] = Cnb @ r3f.rodrigues(wbbn * T)
        Cnb = r3f.mgs(Cnb)
        if baro is not None:
            baro.er_int += baro.er*T

        # Progress bar
        if (k - pb) % pa:
            print(f"\r{int((k+1)/K*100):3d}%", end="")

    # Clear the line after showing progress.
    print("\r", end="", flush=True)

    # Transpose output.
    if trs:
        llh_t = llh_t.T
        vne_t = vne_t.T
        rpy_t = rpy_t.T

    return llh_t, vne_t, rpy_t


def mech_step(
        fbbi: np.ndarray,
        wbbi: np.ndarray,
        llh: np.ndarray,
        vne: np.ndarray,
        Cnb: np.ndarray,
        hb: float | None = None,
        baro: Baro | None = None,
        grav_model: Callable[[np.ndarray], np.ndarray] = somigliana
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get the derivatives of position, velocity, and attitude for one time step.

    Parameters
    ----------
    fbbi : (3,) np.ndarray
        Vector of specific forces (meters per second squared) of the body frame
        relative to the inertial frame, referenced in the body frame.
    wbbi : (3,) np.ndarray
        Vector of rotation rates (radians per second) of the body frame relative
        to the inertial frame, referenced in the body frame.
    llh : (3,) np.ndarray
        Vector of geodetic position in terms of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    vne : (3,) np.ndarray
        Vector of velocity of the navigation frame relative to the ECEF frame
        (meters per second).
    Cnb : (3, 3) np.ndarray
        Passive rotation matrix from the body frame to the NED navigation frame.
    hb : float, default None
        Barometric altitude (m).
    baro : Baro object, default None
        The barometric altitude aiding object.
    grav_model : function, default somigliana
        The gravity model function to use. This function should take a position
        vector of latitude (radians), longitude (radians), and height above
        ellipsoid (meters) and return the local acceleration of gravity vector
        (meters per second squared) in the navigation frame with a North, East,
        Down (NED) orientation.

    Returns
    -------
    Dllh : (3,) np.ndarray
        Derivative of the vector of the geodetic position.
    Dvne : (3,) np.ndarray
        Derivative of the vector of the navigation frame velocity.
    wbbn : (3,) np.ndarray
        Derivative of the vector of the rotation rate of the body frame relative
        to the navigation frame.
    """

    # Trig of latitude
    clat = math.cos(llh[0])
    slat = math.sin(llh[0])
    tlat = math.tan(llh[0])

    # Rotation rate of earth relative to inertial
    wneix = W_EI*clat
    wneiz = -W_EI*slat

    # Rotation rate of navigation relative to earth
    klat = math.sqrt(1 - E2*slat**2)
    Rt = A_E/klat
    Rm = (Rt/klat**2)*(1 - E2)
    wnnex = vne[1]/(Rt + llh[2])
    wnney = -vne[0]/(Rm + llh[2])
    wnnez = -vne[1]*tlat/(Rt + llh[2])

    # Rotation rate of body relative to navigation
    wx = wnnex + wneix
    wy = wnney
    wz = wnnez + wneiz
    Dllh = np.array([wx, wy, wz]) # temp use
    wbbn = wbbi - Cnb.T @ Dllh

    # Position derivatives
    Dllh[0] = -wnney
    Dllh[1] = wnnex/clat
    Dllh[2] = -vne[2]

    # Velocity derivatives
    wx += wneix
    wz += wneiz
    Dvne = Cnb @ fbbi + grav_model(llh)
    Dvne[0] -= wy * vne[2] - wz * vne[1]
    Dvne[1] -= wz * vne[0] - wx * vne[2]
    Dvne[2] -= wx * vne[1] - wy * vne[0]

    # Baro model (all third-order)
    if baro is not None:
        baro.er = llh[2] - hb
        Dllh[2] += -baro.K[0]*baro.er
        Dvne[2] += baro.K[1]*baro.er + baro.K[2]*baro.er_int

    return Dllh, Dvne, wbbn


def jacobian(
        fbbi: np.ndarray,
        llh: np.ndarray,
        vne: np.ndarray,
        Cnb: np.ndarray,
        baro: Baro | None = None
    ) -> np.ndarray:
    """
    Calculate the continuous-domain Jacobian matrix of the propagation function.
    The attitude change is handled via a tilt error vector. Note that this
    matrix must be discretized along with the dynamics noise covariance matrix.
    This can be done with the Van Loan method:

        Phi, _, Qd = inu.vanloan(F, None, Q)

    where `F` is the Jacobian returned by this function and `Q` is the dynamics
    noise covariance matrix. The `Phi` and `Qd` matrices are then the matrices
    you would use in your Bayesian estimation filter.

    Parameters
    ----------
    fbbi : (3,) np.ndarray
        Vector of specific forces (meters per second squared) of the body frame
        relative to the inertial frame, referenced in the body frame.
    llh : (3,) np.ndarray
        Vector of geodetic position in terms of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    vne : (3,) np.ndarray
        Vector of velocity of the navigation frame relative to the ECEF frame
        (meters per second).
    Cnb : (3, 3) np.ndarray
        Passive rotation matrix from the body frame to the NED navigation frame.
    baro : Baro object, default None
        The barometric altitude aiding object.

    Returns
    -------
    F : (9, 9) np.ndarray
        Jacobian matrix.

    Notes
    -----
    The order of states are

        latitude, longitude, height above ellipsoid,
        North velocity, East velocity, down velocity,
        x tilt error, y tilt error, z tilt error

    The tilt error vector, psi, is applied to a true body to NED navigation
    frame rotation matrix, Cnb, to produce a tilted rotation matrix:

        ~              T
        Cnb = exp([psi] ) Cnb
                       x
    """

    # Parse the forces, positions, and velocities.
    fN, fE, fD = Cnb @ fbbi
    lat, _, hae = llh
    vN, vE, vD = vne

    # Trig of latitude
    clat = math.cos(lat)
    slat = math.sin(lat)
    clat2 = clat**2
    slat2 = slat**2
    tlat = math.tan(lat)

    # Rotation rate of earth relative to inertial
    wx = W_EI*clat
    wz = -W_EI*slat

    # Distance from Earth
    klat = math.sqrt(1 - E2*slat2)
    Rt = A_E/klat
    Rm = (Rt/klat**2)*(1 - E2)
    lt = Rt + hae
    lm = Rm + hae

    # Get the partial derivatives with respect to latitude and height.
    y0 = GRAV_E*(1.0 + GRAV_K*slat2)/klat
    nu = 2.0/A_E*(1.0 + GRAV_F + GRAV_M - 2*GRAV_F*slat2)
    eta = 1 + (3/A_E**2)*hae**2 - nu*hae
    Dyl = ((2*GRAV_K*GRAV_E + E2*y0/klat)*eta/klat
        + 8*GRAV_F*y0*hae/A_E)*slat*clat
    Dyh = -y0*nu + y0*6*hae / A_E**2

    # Define the Jacobian matrix.
    F = np.zeros((9, 9))

    # dp_dp
    F[0, 2] = -vN/lm**2
    F[1, 0] = vE*tlat/(lt*clat)
    F[1, 2] = -vE/(lt**2*clat)

    # dp_dv
    F[0, 3] = 1/lm
    F[1, 4] = 1/(lt*clat)
    F[2, 5] = -1

    # dv_dp
    F[3, 0] = -2*vE*wx - vE**2/(lt*clat2)
    F[3, 2] = vE**2*tlat/lt**2 - vN*vD/lm**2
    F[4, 0] = 2*vN*wx + 2*vD*wz + vN*vE/(lt*clat2)
    F[4, 2] = -vE*(vN*tlat + vD)/lt**2
    F[5, 0] = -2*vE*wz + Dyl
    F[5, 2] = (vN/lm)**2 + (vE/lt)**2 + Dyh

    # dv_dv
    F[3, 3] = vD/lm
    F[3, 4] = 2*wz - 2*vE*tlat/lt
    F[3, 5] = vN/lm
    F[4, 3] = -2*wz + vE*tlat/lt
    F[4, 4] = (vN*tlat + vD)/lt
    F[4, 5] = 2*wx + vE/lt
    F[5, 3] = -2*vN/lm
    F[5, 4] = -2*wx - 2*vE/lt

    # dv_dq
    F[3, 7] = -fD
    F[3, 8] = fE
    F[4, 6] = fD
    F[4, 8] = -fN
    F[5, 6] = -fE
    F[5, 7] = fN

    # dq_dp
    F[6, 0] = wz
    F[6, 2] = -vE/lt**2
    F[7, 2] = vN/lm**2
    F[8, 0] = -wx - vE/(lt*clat2)
    F[8, 2] = vE*tlat/lt**2

    # dq_dv
    F[6, 4] = 1/lt
    F[7, 3] = -1/lm
    F[8, 4] = -tlat/lt

    # dq_dq
    F[6, 7] = wz - vE*tlat/lt
    F[6, 8] = vN/lm
    F[7, 6] = -wz + vE*tlat/lt
    F[7, 8] = wx + vE/lt
    F[8, 6] = -vN/lm
    F[8, 7] = -wx - vE/lt

    # Baro model (all third-order)
    if baro is not None:
        F[2, 2] += -baro.K[0]
        F[5, 2] += baro.K[1]

    return F

# -----------
# Deprecation
# -----------

def inv_mech(
        llh_t: np.ndarray,
        rpy_t: np.ndarray,
        T: float,
        grav_model: Callable[[np.ndarray], np.ndarray] = somigliana
    ) -> tuple[np.ndarray, np.ndarray]:
    warnings.warn(
        "`inv_mech` is deprecated and will be removed. "
        "Use `mech_inv` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return mech_inv(llh_t, rpy_t, T, grav_model)
