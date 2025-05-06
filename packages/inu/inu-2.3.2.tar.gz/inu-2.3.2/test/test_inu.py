# Run `pytest` in the terminal.

import time
import numpy as np
import inu
import r3f

# -----------------
# Support Functions
# -----------------

def test_Baro():
    model_names = ["savage", "rogers", "widnall", "silva",
        "iae", "ise", "itae", "itse"]
    for name in model_names:
        baro_model = inu.Baro(name)
        assert len(baro_model.K) == 3
        assert (baro_model.K > 0).all()
        assert (baro_model.K < 1.1).all()
        assert baro_model.er == 0.0
        assert baro_model.er_int == 0.0


def test_wrap():
    v = np.array([1.5*np.pi, -1.25*np.pi])
    u = inu.wrap(v)
    assert (u == np.array([-np.pi/2, 0.75*np.pi])).all()


def test_ned_enu():
    v = np.array([2.0, 3, 5])
    assert (inu.ned_enu(v) == np.array([3.0, 2, -5])).all()

    v = np.array([
        [2.0, 3, 5],
        [1.0, 0.5, 0.1]])
    u = np.array([
        [3.0, 2, -5],
        [0.5, 1, -0.1]])
    assert (inu.ned_enu(v) == u).all()
    assert (inu.ned_enu(v.T) == u.T).all()


def test_vanloan():
    T = 0.1
    F = np.array([
        [0.0, 1],
        [0, 0]])
    B = np.array([
        [1.0],
        [1]])
    Q = np.diag([0.1, 0.01])
    I = np.eye(2)

    # Get discretized dynamics matrices.
    Phi, Bd, Qd = inu.vanloan(F, B, Q, T)

    # Get the approximate discretized dynamics matrices.
    hPhi = I + F * T + (1/2) * F @ F * T**2 * (1/6) * F @ F @ F * T**3
    hBd = B * T + (1/2) * F @ B * T**2 + (1/6) * F @ F @ B * T**3
    hQd = Q * T + T**2/2 * (F @ Q + Q @ F.T) \
        + T**3/6 * (F @ F @ Q + 2 * F @ Q @ F.T + Q @ F.T @ F.T)

    assert np.allclose(Phi, hPhi)
    assert np.allclose(Bd, hBd)
    assert np.allclose(Qd, hQd)

# ----------------
# Truth Generation
# ----------------

def test_path_generation():
    seg_len = 0.1
    funcs = [inu.path_box, inu.path_clover, inu.path_grid, inu.path_spiral]

    # Test each path generation function.
    for func in funcs:
        # Get the path.
        x, y, z = func(seg_len)

        # Verify the line segment lengths.
        dx = np.diff(x)
        dy = np.diff(y)
        dr = np.sqrt(dx**2 + dy**2)
        assert np.abs(seg_len - dr).max() < 1e-10

        # Verify the ending point is the starting point.
        r = np.sqrt((x[0] - x[-1])**2 + (y[0] - y[-1])**2 + (z[0] - z[-1])**2)
        assert (r < seg_len)

    # Check pretzel.
    p = inu.path_pretzel(100.0)
    assert np.allclose(p[:, 0], p[:, -1])


def test_llh_to_vne():
    # Constants
    T = 1.0
    llh_t = np.array([
        [0.0, 0.0, 100.0],
        [0.001, 0.001, 10.0]]).T

    # Attempt normal orientation.
    vne_t = inu.llh_to_vne(llh_t, T)
    assert (np.abs(vne_t[0] - 6335.5) < 1.0).all()
    assert (np.abs(vne_t[1] - 6378.2) < 1.0).all()
    assert (np.abs(vne_t[2] - 90.0) < 1e-9).all()

    # Attempt transpose.
    tvne_t = inu.llh_to_vne(llh_t.T, T)
    assert np.allclose(vne_t, tvne_t.T)


def test_somigliana():
    # Constants
    llh_t = np.array([
        [0.0, 0.0, 100.0],
        [0.001, 0.001, 10.0]]).T

    # Attempt normal orientation.
    gam_t = inu.somigliana(llh_t)
    assert np.allclose(gam_t[2], np.array([9.78001657, 9.78029451]))

    # Attempt transpose.
    gam_t = inu.somigliana(llh_t.T)
    assert np.allclose(gam_t[:, 2], np.array([9.78001657, 9.78029451]))


def test_vne_to_rpy():
    # Constants
    T = 0.00125
    R = 100.0
    grav = 9.78
    K = 4

    t = np.arange(K) * T
    vne_t = np.zeros((3, K))
    vne_t[0] = (R*2*np.pi) * np.cos(2*np.pi*1.0*t)
    vne_t[1] = -(R*2*np.pi) * np.sin(2*np.pi*1.0*t)

    rpy_t = inu.vne_to_rpy(vne_t, grav, T, alpha=0)

    # Estimate roll for coordinated turn.
    ac = R*4*np.pi**2 # centripetal acceleration
    roll = -np.arctan(ac/grav)

    # Calculate the yaw.
    yaw = -2*np.pi*1.0*t

    assert (np.abs(rpy_t[0] - roll) < 1e-4).all()
    assert (rpy_t[1] == 0.0).all()
    assert np.allclose(rpy_t[2], yaw)


def test_llh_to_tva():
    # The results of llh_to_tva are not checked because the component fuctions
    # of this function already were checked. This test simply verifies that the
    # function can be called without errors.

    T = 1.0
    llh_t = np.array([
        [0.0, 0.0, 100.0],
        [0.001, 0.001, 10.0]]).T
    try:
        t, vne_t, rpy_t = inu.llh_to_tva(llh_t, T)
        assert True
    except:
        assert False


def test_mech():
    # Constants
    T = 0.01
    velocity = 100.0
    llh0 = np.array([0.0, 0, 100.0])

    # Test with time varying along axis 1.

    # Build path.
    p_t = inu.path_clover(T*velocity, radius=100.0, cycles=1)
    llh_t = r3f.curvilinear_to_geodetic(p_t, llh0)
    t, vne_t, rpy_t = inu.llh_to_tva(llh_t, T)

    # Inverse and forward mechanize.
    hfbbi_t, hwbbi_t = inu.mech_inv(llh_t, rpy_t, T)

    vne0 = vne_t[:, 0]
    rpy0 = rpy_t[:, 0]
    Cnb0 = r3f.rpy_to_dcm(rpy0).T
    tllh_t, tvne_t, trpy_t = inu.mech(hfbbi_t, hwbbi_t,
        llh0, vne0, rpy0, T)

    assert np.allclose(llh_t, tllh_t)
    assert np.allclose(vne_t, tvne_t)
    assert np.allclose(rpy_t, trpy_t)

    # Test with time varying along axis 0.

    # Build path.
    p_t = inu.path_clover(T*velocity, radius=100.0, cycles=1).T
    llh_t = r3f.curvilinear_to_geodetic(p_t, llh0)
    t, vne_t, rpy_t = inu.llh_to_tva(llh_t, T)

    # Inverse and forward mechanize.
    hfbbi_t, hwbbi_t = inu.mech_inv(llh_t, rpy_t, T)

    vne0 = vne_t[0, :]
    rpy0 = rpy_t[0, :]
    Cnb0 = r3f.rpy_to_dcm(rpy0).T
    tllh_t, tvne_t, trpy_t = inu.mech(hfbbi_t, hwbbi_t,
        llh0, vne0, rpy0, T)

    assert np.allclose(llh_t, tllh_t)
    assert np.allclose(vne_t, tvne_t)
    assert np.allclose(rpy_t, trpy_t)


def test_jacobian():
    # TODO I need to move analysis/jacobian.py into this function.
    pass
