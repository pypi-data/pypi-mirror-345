# Run `pytest` in the terminal.
import math
import numpy as np
import r3f

np.random.seed(0)

# -----------------------------------
# Attitude-representation Conversions
# -----------------------------------

def test_axis_angle_vector():
    a = 1.0/math.sqrt(3.0)
    ang = 2

    # single conversion with list
    ax = [a, a, a]
    vec = r3f.axis_angle_to_vector(ax, ang)
    assert np.allclose(vec, [2*a, 2*a, 2*a])
    AX, ANG = r3f.vector_to_axis_angle(vec)
    assert np.allclose(ax, AX)
    assert np.allclose(ang, ANG)

    # single conversion with tuple
    ax = (a, a, a)
    vec = r3f.axis_angle_to_vector(ax, ang)
    assert np.allclose(vec, [2*a, 2*a, 2*a])
    AX, ANG = r3f.vector_to_axis_angle(vec)
    assert np.allclose(ax, AX)
    assert np.allclose(ang, ANG)

    # single conversion with degrees
    ax = (a, a, a)
    ang = 2*180/math.pi
    vec = r3f.axis_angle_to_vector(ax, ang, degs=True)
    assert np.allclose(vec, [2*a, 2*a, 2*a])
    AX, ANG = r3f.vector_to_axis_angle(vec, degs=True)
    assert np.allclose(ax, AX)
    assert np.allclose(ang, ANG)

    # multiple conversions with ndarray
    ax = np.array([
        [1, 0, 0, a],
        [0, 1, 0, a],
        [0, 0, 1, a]])
    ang = np.array([2, 2, 2, 2])
    vec = np.array([
            [2, 0, 0, 2*a],
            [0, 2, 0, 2*a],
            [0, 0, 2, 2*a]])
    VEC = r3f.axis_angle_to_vector(ax, ang)
    assert np.allclose(VEC, vec)
    AX, ANG = r3f.vector_to_axis_angle(VEC)
    assert np.allclose(ax, AX)
    assert np.allclose(ang, ANG)

    # multiple conversions with list
    ax = np.array([
        [1, 0, 0, a],
        [0, 1, 0, a],
        [0, 0, 1, a]])
    ang = [2, 2, 2, 2]
    vec = [[2, 0, 0, 2*a],
            [0, 2, 0, 2*a],
            [0, 0, 2, 2*a]]
    VEC = r3f.axis_angle_to_vector(ax, ang)
    assert np.allclose(VEC, vec)
    AX, ANG = r3f.vector_to_axis_angle(vec)
    assert np.allclose(ax, AX)
    assert np.allclose(ang, ANG)

    # multiple conversions transposed
    ax = np.array([
        [1, 0, 0, a],
        [0, 1, 0, a],
        [0, 0, 1, a]]).T
    ang = np.array([2, 2, 2, 2])
    vec = np.array([
            [2, 0, 0, 2*a],
            [0, 2, 0, 2*a],
            [0, 0, 2, 2*a]]).T
    VEC = r3f.axis_angle_to_vector(ax, ang)
    assert np.allclose(VEC, vec)
    AX, ANG = r3f.vector_to_axis_angle(VEC)
    assert np.allclose(ax, AX)
    assert np.allclose(ang, ANG)


def test_rpy_vector():
    # single conversion with list
    vec = [1.0, 1.0, 1.0]
    rpy = r3f.vector_to_rpy(vec)
    VEC = r3f.rpy_to_vector(rpy.tolist())
    assert np.allclose(vec, VEC)

    # single conversion with tuple
    vec = (1.0, 1.0, 1.0)
    rpy = r3f.vector_to_rpy(vec)
    VEC = r3f.rpy_to_vector(rpy)
    assert np.allclose(vec, VEC)

    # single conversion with degrees
    vec = np.array([1.0, 1.0, 1.0])
    rpy = r3f.vector_to_rpy(vec, degs=True)
    VEC = r3f.rpy_to_vector(rpy, degs=True)
    assert np.allclose(vec, VEC)

    # mutiple conversions
    a = 1.0/math.sqrt(3.0)
    vec = np.array([
            [2, 0, 0, 2*a],
            [0, 2, 0, 2*a],
            [0, 0, 2, 2*a]])
    rpy = r3f.vector_to_rpy(vec)
    VEC = r3f.rpy_to_vector(rpy)
    assert np.allclose(vec, VEC)


def test_dcm_vector():
    ang = math.pi/4

    # single conversion with list
    vec = [0.0, 0.0, ang]
    dcm = [[math.cos(ang), math.sin(ang), 0],
        [-math.sin(ang), math.cos(ang), 0],
        [0, 0, 1]]
    DCM = r3f.vector_to_dcm(vec)
    assert np.allclose(dcm, DCM)
    VEC = r3f.dcm_to_vector(dcm)
    assert np.allclose(vec, VEC)

    # single conversion with tuple
    vec = (0.0, ang, 0.0)
    dcm = np.array([
        [math.cos(ang), 0, -math.sin(ang)],
        [0, 1, 0],
        [math.sin(ang), 0, math.cos(ang)]])
    DCM = r3f.vector_to_dcm(vec)
    assert np.allclose(dcm, DCM)
    VEC = r3f.dcm_to_vector(DCM)
    assert np.allclose(vec, VEC)

    # multiple conversions
    a = 1.0/math.sqrt(3.0)
    vec = np.array([
            [2, 0, 0, 2*a],
            [0, 2, 0, 2*a],
            [0, 0, 2, 2*a]])
    DCM = r3f.vector_to_dcm(vec)
    VEC = r3f.dcm_to_vector(DCM)
    assert np.allclose(vec, VEC)


def test_quat_vector():
    ang = math.pi/4

    # single conversion with list
    vec = [0.0, 0.0, ang]
    #quat
    QUAT = r3f.vector_to_quat(vec)
    quat = [0.92387953, 0, 0, 0.38268343]
    VEC = r3f.quat_to_vector(quat)
    assert np.allclose(vec, VEC)

    # single conversion with tuple
    vec = (0.0, 0.0, ang)
    quat = r3f.vector_to_quat(vec)
    VEC = r3f.quat_to_vector(quat)
    assert np.allclose(vec, VEC)

    # multiple conversions
    a = 1.0/math.sqrt(3.0)
    vec = np.array([
            [2, 0, 0, 2*a],
            [0, 2, 0, 2*a],
            [0, 0, 2, 2*a]])
    quat = r3f.vector_to_quat(vec)
    VEC = r3f.quat_to_vector(quat)
    assert np.allclose(vec, VEC)


def test_rpy_axis_angle():
    # single conversions with list and tuple and ndarray and degrees
    ax, ang = r3f.rpy_to_axis_angle([0, 0, np.pi/4])
    assert np.allclose(ax, np.array([0, 0, 1]))
    assert np.allclose(ang, np.pi/4)
    ax, ang = r3f.rpy_to_axis_angle((0, np.pi/4, 0))
    assert np.allclose(ax, np.array([0, 1, 0]))
    assert np.allclose(ang, np.pi/4)
    ax, ang = r3f.rpy_to_axis_angle(np.array([45.0, 0, 0]), degs=True)
    assert np.allclose(ax, np.array([1, 0, 0]))
    assert np.allclose(ang, 45.0)
    RPY = r3f.axis_angle_to_rpy(ax, ang, degs=True)
    assert np.allclose(RPY, np.array([45.0, 0, 0]))
    RPY = r3f.axis_angle_to_rpy([1.0, 0, 0], ang, degs=True)
    assert np.allclose(RPY, np.array([45.0, 0, 0]))

    # multiple conversions
    N = 10
    r = np.random.uniform(-np.pi, np.pi, N)
    p = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, N)
    y = np.random.uniform(-np.pi, np.pi, N)
    ax, ang = r3f.rpy_to_axis_angle([r, p, y])
    [R, P, Y] = r3f.axis_angle_to_rpy(ax, ang)
    assert np.allclose(r, R)
    assert np.allclose(p, P)
    assert np.allclose(y, Y)

    # multiple conversions with transpose ax and list ang
    [R, P, Y] = r3f.axis_angle_to_rpy(ax.T, ang.tolist()).T
    assert np.allclose(r, R)
    assert np.allclose(p, P)
    assert np.allclose(y, Y)


def test_dcm_axis_angle():
    # Define common angle and cosine and sine.
    ang = np.pi/4
    co = np.cos(ang)
    si = np.sin(ang)

    # Test individual axes.
    C = np.array([[co, si, 0], [-si, co, 0], [0, 0, 1]])
    C_p = r3f.axis_angle_to_dcm(np.array([0, 0, 1]), ang)
    assert np.allclose(C, C_p)
    ax1, ang1 = r3f.dcm_to_axis_angle(C_p)
    assert np.allclose(np.array([0, 0, 1]), ax1)
    assert np.allclose(ang, ang1)
    C = np.array([[co, 0, -si], [0, 1, 0], [si, 0, co]])
    C_p = r3f.axis_angle_to_dcm(np.array([0, 1, 0]), ang)
    assert np.allclose(C, C_p)
    ax1, ang1 = r3f.dcm_to_axis_angle(C_p)
    assert np.allclose(np.array([0, 1, 0]), ax1)
    assert np.allclose(ang, ang1)
    C = np.array([[1, 0, 0], [0, co, si], [0, -si, co]])
    C_p = r3f.axis_angle_to_dcm(np.array([1, 0, 0]), ang)
    assert np.allclose(C, C_p)
    ax1, ang1 = r3f.dcm_to_axis_angle(C_p)
    assert np.allclose(np.array([1, 0, 0]), ax1)
    assert np.allclose(ang, ang1)

    # Test lists and degrees.
    C_p = r3f.axis_angle_to_dcm([1, 0, 0], 45.0, degs=True)
    ax1, ang1 = r3f.dcm_to_axis_angle(C_p.tolist(), degs=True)
    assert np.allclose(np.array([1, 0, 0]), ax1)
    assert np.allclose(45.0, ang1)

    # Test vectorized reciprocity (requires positive axes).
    N = 5
    ax = np.abs(np.random.randn(3, N))
    nm = np.linalg.norm(ax, axis=0)
    ax /= nm
    ang = np.random.randn(N)
    C = r3f.axis_angle_to_dcm(ax, ang)
    ax1, ang1 = r3f.dcm_to_axis_angle(C)
    assert np.allclose(ax, ax1)
    assert np.allclose(ang, ang1)

    # Test transpose.
    C1 = r3f.axis_angle_to_dcm(ax.T, ang)
    assert np.allclose(C1, C)

    # Test lists.
    C = r3f.axis_angle_to_dcm(ax.tolist(), ang.tolist())
    ax1, ang1 = r3f.dcm_to_axis_angle(C.tolist())
    assert np.allclose(ax, ax1)
    assert np.allclose(ang, ang1)

    # preserve units
    ang = np.array([1.0, 0.5])
    ax = np.array([
        [1, 2],
        [1, 2],
        [1, 2]])
    C = r3f.axis_angle_to_dcm(ax, ang)
    assert np.allclose(ang, np.array([1.0, 0.5]))


def test_quat_axis_angle():
    # axis angle to quat
    a = np.array([1, 1, 1])/np.sqrt(3) # normalized
    q1 = r3f.axis_angle_to_quat(a, np.pi)
    assert np.allclose(q1, np.array([0, 1, 1, 1])/np.sqrt(3))
    b = np.array([2, 2, 2])/np.sqrt(12) # normalized
    q2 = r3f.axis_angle_to_quat(b, np.pi)
    assert np.allclose(q2, np.array([0, 2, 2, 2])/np.sqrt(12))

    # backwards (requires normalized start)
    ax, ang = r3f.quat_to_axis_angle(q1)
    assert np.allclose(a, ax)
    assert np.allclose(np.pi, ang)

    # backwards (requires normalized start) with list
    ax, ang = r3f.quat_to_axis_angle(q1.tolist())
    assert np.allclose(a, ax)
    assert np.allclose(np.pi, ang)

    # Test vectorized reciprocity with transpose and lists.
    A = np.column_stack((a, b))
    Q = np.column_stack((q1, q2))
    PI = np.array([np.pi, np.pi])
    Q2 = r3f.axis_angle_to_quat(A.T.tolist(), PI.tolist()).T
    assert np.allclose(Q2, Q)
    A2, PI2 = r3f.quat_to_axis_angle(Q2.T.tolist())
    assert np.allclose(A, A2.T)


def test_dcm_rpy():
    # Build a random DCM.
    R = np.random.uniform(-np.pi, np.pi)
    P = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL)
    Y = np.random.uniform(-np.pi, np.pi)

    # Get rotation matrix.
    C_1g = np.array([
        [np.cos(Y), np.sin(Y), 0],
        [-np.sin(Y), np.cos(Y), 0],
        [0, 0, 1]])
    C_21 = np.array([
        [np.cos(P), 0, -np.sin(P)],
        [0, 1, 0],
        [np.sin(P), 0, np.cos(P)]])
    C_b2 = np.array([
        [1, 0, 0],
        [0, np.cos(R), np.sin(R)],
        [0, -np.sin(R), np.cos(R)]])
    C_bg = C_b2 @ C_21 @ C_1g

    # Check DCM to RPY.
    [r, p, y] = r3f.dcm_to_rpy(C_bg)
    assert np.allclose(r, R)
    assert np.allclose(p, P)
    assert np.allclose(y, Y)

    # Check with list and degrees.
    [r_deg, p_deg, y_deg] = r3f.dcm_to_rpy(C_bg.tolist(), True)
    C_2 = r3f.rpy_to_dcm([r_deg, p_deg, y_deg], True)
    assert np.allclose(C_bg, C_2)

    # Test vectorized reciprocity with transpose.
    N = 5
    R = np.random.uniform(-np.pi, np.pi, N)
    P = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, N)
    Y = np.random.uniform(-np.pi, np.pi, N)
    RPY = np.array([R, P, Y])
    C = r3f.rpy_to_dcm(RPY.T)
    [r, p, y] = r3f.dcm_to_rpy(C)
    assert np.allclose(r, R)
    assert np.allclose(p, P)
    assert np.allclose(y, Y)

    # preserve units
    R = np.random.uniform(-180.0, 180.0, N)
    P = np.random.uniform(-90.0 + r3f.TOL, 90.0 - r3f.TOL, N)
    Y = np.random.uniform(-180.0, 180.0, N)
    R0 = R.copy()
    P0 = P.copy()
    Y0 = Y.copy()
    C = r3f.rpy_to_dcm([R, P, Y], degs=True)
    assert np.allclose(R, R0)
    assert np.allclose(P, P0)
    assert np.allclose(Y, Y0)


def test_quat_rpy():
    # This set of tests relies on previous tests for rpy_to_axis_angle and 
    # axis_angle_to_quat.

    # Test forward path with list and transpose.
    N = 5
    R = np.random.uniform(-np.pi, np.pi, N)
    P = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, N)
    Y = np.random.uniform(-np.pi, np.pi, N)
    ax, ang = r3f.rpy_to_axis_angle([R, P, Y])
    q1 = r3f.axis_angle_to_quat(ax, ang)
    RPY = np.array([R, P, Y])
    q2 = r3f.rpy_to_quat(RPY.T.tolist()).T
    assert np.allclose(q1, q2)

    # Test backward path with transpose and list.
    [r, p, y] = r3f.quat_to_rpy(q2.T.tolist()).T
    assert np.allclose(r, R)
    assert np.allclose(p, P)
    assert np.allclose(y, Y)

    # preserve units
    R = np.random.uniform(-180.0, 180.0, N)
    P = np.random.uniform(-90.0 + r3f.TOL, 90.0 - r3f.TOL, N)
    Y = np.random.uniform(-180.0, 180.0, N)
    R0 = R.copy()
    P0 = P.copy()
    Y0 = Y.copy()
    q = r3f.rpy_to_quat([R, P, Y], degs=True)
    assert np.allclose(R, R0)
    assert np.allclose(P, P0)
    assert np.allclose(Y, Y0)


def test_quat_dcm():
    # This set of tests relies on previous tests of rpy_to_quat and rpy_to_dcm.

    # Multiple with transpose and list
    N = 5
    R = np.random.uniform(-np.pi, np.pi, N)
    P = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, N)
    Y = np.random.uniform(-np.pi, np.pi, N)
    q1 = r3f.rpy_to_quat([R, P, Y])
    C1 = r3f.rpy_to_dcm([R, P, Y])
    C2 = r3f.quat_to_dcm(q1.T.tolist())
    assert np.allclose(C1, C2)
    q2 = r3f.dcm_to_quat(C2.tolist())
    assert np.allclose(q1, q2)

    # Single
    C3 = r3f.quat_to_dcm(q1[:, 0])
    assert np.allclose(C1[0], C3)
    q3 = r3f.dcm_to_quat(C3)
    assert np.allclose(q1[:, 0], q3)

    # Check zero matrix.
    try:
        C1[-1, :, :] = np.zeros((3, 3))
        r3f.dcm_to_quat(C1)
    except ValueError as e:
        assert True

    # Check 180 rotation.
    try:
        C = np.array([
                [-1.0, 0, 0],
                [0, -1.0, 0],
                [0, 0, 1.0]])
        r3f.dcm_to_quat(C)
    except ValueError as e:
        assert True


def test_rot():
    irt2 = 1/np.sqrt(2)

    # z-axis rotation
    C = np.array([
        [irt2, irt2, 0],
        [-irt2, irt2, 0],
        [0, 0, 1]])
    assert np.allclose(r3f.dcm(45, 2, True), C)

    # y-axis rotation
    B = np.array([
        [irt2, 0, -irt2],
        [0, 1, 0],
        [irt2, 0, irt2]])
    assert np.allclose(r3f.dcm(45, 1, True), B)

    # x-axis rotation
    A = np.array([
        [1, 0, 0],
        [0, irt2, irt2],
        [0, -irt2, irt2]])
    assert np.allclose(r3f.dcm(45, 0, True), A)

    # Multiple rotations with a trivial rotation of 0
    R = r3f.dcm([45, 0, 45, 45], [2, 2, 1, 0], True)
    assert np.allclose(R, A @ B @ C)

    # String axes
    R = r3f.dcm([45, 45, 45], "zyx", True)
    assert np.allclose(R, A @ B @ C)

    # preserve units
    ang = np.array([45, 45, 45])
    ax = np.array([2, 1, 0])
    R = r3f.dcm(ang, ax, True)
    assert np.allclose(ang, np.array([45, 45, 45]))


def test_euler():
    # Test the duality between the dcm and euler functions for every possible
    # sequence of three Euler rotations.
    ang = np.array([45, 30, 15.0])
    seqs = ["xzx", "xyx", "yxy", "yzy", "zyz", "zxz",
            "yzx", "zyx", "zxy", "xzy", "xyz", "yxz"]
    for seq in seqs:
        C = r3f.dcm(ang, seq, True)
        ang_fit = r3f.euler(C, seq, True)
        assert np.allclose(ang, ang_fit)

    # Test with list and degrees.
    C = r3f.dcm(ang, seq, True)
    ang_fit = r3f.euler(C.tolist(), seq, True)
    assert np.allclose(ang, ang_fit)

    # Test list or ndarray.
    seq = [1, 0, 2]
    C = r3f.dcm(ang, seq, True)
    ang_fit = r3f.euler(C, seq)
    assert np.allclose(np.radians(ang), ang_fit)
    ang_fit = r3f.euler(C, np.array(seq))
    assert np.allclose(np.radians(ang), ang_fit)

    # Test invalid axis sequence.
    try:
        r3f.euler(C, "xxy")
    except ValueError as e:
        assert True
    try:
        r3f.euler(C, "xyxz")
    except ValueError as e:
        assert True
    try:
        r3f.euler(C, [1, 0, 2, 1])
    except ValueError as e:
        assert True


def test_rotate():
    # Generate the random inputs.
    N = 10
    R = np.random.uniform(-np.pi, np.pi, N)
    P = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, N)
    Y = np.random.uniform(-np.pi, np.pi, N)
    C = r3f.rpy_to_dcm([R, P, Y])
    a = np.random.randn(3, N)

    # Rotate with the single function.
    b1 = r3f.rotate(C, a)

    # Rotate with a for loop.
    b2 = np.zeros((3, N))
    for n in range(N):
        b2[:, n] = C[n, :, :] @ a[:, n]

    # Check the results.
    assert np.allclose(b1, b2)

    # Test with lists and transpose.
    b3 = r3f.rotate(C.tolist(), a.T.tolist())
    assert np.allclose(b1, b3.T)

    # Test with single matrix.
    try:
        r3f.rotate(C[0, :, :], a)
    except ValueError as e:
        assert True
    try:
        r3f.rotate(C, a[0])
    except ValueError as e:
        assert True

# -------------------------
# Reference-frame Rotations
# -------------------------

def test_dcm_inertial_to_ecef():
    # Test single time.
    t = np.pi/r3f.W_EI
    C = r3f.dcm_inertial_to_ecef(t)
    assert np.allclose(C, np.diag([-1, -1, 1]))

    # Test multiple times with list.
    N = 11
    t = np.linspace(0.0, (2*np.pi)/r3f.W_EI, N)
    C = r3f.dcm_inertial_to_ecef(t.tolist())
    assert np.allclose(C[0, :, :], np.eye(3))
    assert np.allclose(C[int((N - 1)/2), :, :], np.diag([-1, -1, 1]))
    assert np.allclose(C[-1, :, :], np.eye(3))

def test_dcm_ecef_to_navigation():
    # Test single.
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL)
    lon = np.random.uniform(-np.pi, np.pi)
    A = r3f.dcm([lon, -(lat + np.pi/2)], [2, 1])
    B = r3f.dcm_ecef_to_navigation(lat, lon)
    assert np.allclose(A, B)

    # Test with ENU and degrees.
    D = np.zeros((3, 3))
    D[0] = A[1]
    D[1] = A[0]
    D[2] = -A[2]
    E = r3f.dcm_ecef_to_navigation(lat*180/np.pi, lon*180/np.pi,
            ned=False, degs=True)
    assert np.allclose(A, B)

    # Test multiple with lists.
    N = 10
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, size=N)
    lon = np.random.uniform(-np.pi, np.pi, size=N)
    C = r3f.dcm_ecef_to_navigation(lat.tolist(), lon.tolist())
    for n in range(N):
        A = r3f.dcm_ecef_to_navigation(lat[n], lon[n])
        assert np.allclose(A, C[n, :, :])

# ---------------------------
# Reference-frame Conversions
# ---------------------------

def test_ecef_geodetic():
    # Test single point.
    [xe, ye, ze] = r3f.geodetic_to_ecef([0.0, 0.0, 0.0])
    assert np.allclose([xe, ye, ze], [r3f.A_E, 0, 0])
    [lat, lon, hae] = r3f.ecef_to_geodetic([xe, ye, ze])
    assert np.allclose([lat, lon, hae], [0.0, 0.0, 0.0])

    # Build original data.
    N = 10
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, size=N)
    lon = np.random.uniform(-np.pi, np.pi, size=N)
    hae = np.random.uniform(-10e3, 100e3, size=N)

    # Test vectorized reciprocity with transpose and list.
    llh = np.array([lat, lon, hae])
    [xe, ye, ze] = r3f.geodetic_to_ecef(llh.T.tolist()).T
    xyz = np.array([xe, ye, ze])
    [Lat, Lon, Hae] = r3f.ecef_to_geodetic(xyz.T.tolist()).T
    assert np.allclose([lat, lon, hae], [Lat, Lon, Hae])

    # preserve units
    lat = np.random.uniform(-90.0 + r3f.TOL, 90.0 - r3f.TOL, size=N)
    lon = np.random.uniform(-180.0, 180.0, size=N)
    hae = np.random.uniform(-10e3, 100e3, size=N)
    lat0 = lat.copy()
    lon0 = lon.copy()
    hae0 = hae.copy()
    [xe, ye, ze] = r3f.geodetic_to_ecef([lat, lon, hae], degs=True)
    assert np.allclose(lat, lat0)
    assert np.allclose(lon, lon0)


def test_ecef_tangent():
    # This test depends on geodetic_to_ecef.

    # Test single point.
    xe = r3f.A_E
    ye = 0.0
    ze = r3f.B_E
    xe0 = r3f.A_E
    ye0 = 0.0
    ze0 = 0.0
    [xt, yt, zt] = r3f.ecef_to_tangent([xe, ye, ze], [xe0, ye0, ze0])
    XT = r3f.B_E
    YT = 0.0
    ZT = 0.0
    assert np.allclose([xt, yt, zt], [XT, YT, ZT])
    [XE, YE, ZE] = r3f.tangent_to_ecef([XT, YT, ZT], [xe0, ye0, ze0])
    assert np.allclose([xe, ye, ze], [XE, YE, ZE])

    # Test trivial conversion.
    [xt, yt, zt] = r3f.ecef_to_tangent([xe, ye, ze])
    assert np.allclose([xt, yt, zt], [0.0, 0.0, 0.0])

    # Build original data.
    N = 10
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, size=N)
    lon = np.random.uniform(-np.pi, np.pi, size=N)
    hae = np.random.uniform(-10e3, 100e3, size=N)
    [xe, ye, ze] = r3f.geodetic_to_ecef([lat, lon, hae])

    # Test vectorized reciprocity with transpose and lists.
    pe = np.array([xe, ye, ze])
    [xt, yt, zt] = r3f.ecef_to_tangent(pe.T.tolist()).T
    pt = np.array([xt, yt, zt])
    [XE, YE, ZE] = r3f.tangent_to_ecef(pt.T.tolist(), [xe[0], ye[0], ze[0]]).T
    assert np.allclose([xe, ye, ze], [XE, YE, ZE])

    # Test ENU and given pe0.
    [xT, yT, zT] = r3f.ecef_to_tangent(pe.T, pe[:, 0], False).T
    [xE, yE, zE] = r3f.tangent_to_ecef([xT, yT, zT], [xe[0], ye[0], ze[0]],
            ned=False)
    assert np.allclose([xe, ye, ze], [xE, yE, zE])


def test_geodetic_curvilinear():
    # Test single point.
    [xc, yc, zc] = r3f.geodetic_to_curvilinear([np.pi/4, 0, 1000], [0, 0, 0])
    assert xc > 0
    assert yc == 0
    assert zc == -1000
    [lat, lon, hae] = r3f.curvilinear_to_geodetic([xc, yc, zc], [0, 0, 0])
    assert np.allclose([np.pi/4, 0.0, 1e3], [lat, lon, hae])

    # Test ENU with degrees.
    [xC, yC, zC] = r3f.geodetic_to_curvilinear([45.0, 0, 1000],
            [0, 0, 0], False, True)
    [Lat, Lon, Hae] = r3f.curvilinear_to_geodetic([xC, yC, zC],
            [0, 0, 0], False, True)
    assert np.allclose([lat, lon, hae], [Lat*np.pi/180, Lon*np.pi/180, Hae])

    # Build original data.
    N = 10
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, size=N)
    lon = np.random.uniform(-np.pi, np.pi, size=N)
    hae = np.random.uniform(-10e3, 100e3, size=N)

    # Test geodetic to curvilinear with transpose and list.
    llh = np.array([lat, lon, hae])
    [xc, yc, zc] = r3f.geodetic_to_curvilinear(llh.T.tolist(), llh[:, 0]).T

    # Test vectorized reciprocity.
    [Lat, Lon, Hae] = r3f.curvilinear_to_geodetic([xc, yc, zc],
        [lat[0], lon[0], hae[0]])
    assert np.allclose([lat, lon, hae], [Lat, Lon, Hae])

    # Test without llh0.
    [Xc, Yc, Zc] = r3f.geodetic_to_curvilinear(llh)
    assert np.allclose([xc, yc, zc], [Xc, Yc, Zc])

    # Test trivial conversion.
    [xc, yc, zc] = r3f.geodetic_to_curvilinear(llh[:, 0])
    assert np.allclose([xc, yc, zc], [0.0, 0.0, 0.0])


def test_curvilinear_ecef():
    # This test depends on geodetic_to_ecef and geodetic_to_curvilinear.

    # Built test points.
    N = 10
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, size=N)
    lon = np.random.uniform(-np.pi, np.pi, size=N)
    hae = np.random.uniform(-10e3, 100e3, size=N)
    lat0 = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL)
    lon0 = np.random.uniform(-np.pi, np.pi)
    hae0 = np.random.uniform(-10e3, 100e3)
    [XE, YE, ZE] = r3f.geodetic_to_ecef([lat, lon, hae])
    [xc, yc, zc] = r3f.geodetic_to_curvilinear([lat, lon, hae],
            [lat0, lon0, hae0])
    [xe0, ye0, ze0] = r3f.geodetic_to_ecef([lat0, lon0, hae0])

    # Test multiple with transpose and lists.
    pc = np.array([xc, yc, zc])
    [xe, ye, ze] = r3f.curvilinear_to_ecef(pc.T.tolist(), [xe0, ye0, ze0]).T
    assert np.allclose(xe, XE)
    assert np.allclose(ye, YE)
    assert np.allclose(ze, ZE)
    pe = np.array([xe, ye, ze])
    [XC, YC, ZC] = r3f.ecef_to_curvilinear(pe.T.tolist(), [xe0, ye0, ze0]).T
    assert np.allclose(xc, XC)
    assert np.allclose(yc, YC)
    assert np.allclose(zc, ZC)

    # Test with no pe0.
    pe[:, 0] = np.array([xe0, ye0, ze0])
    [XC, YC, ZC] = r3f.ecef_to_curvilinear(pe)
    assert np.allclose(xc[1:], XC[1:])
    assert np.allclose(yc[1:], YC[1:])
    assert np.allclose(zc[1:], ZC[1:])

    # Test trivial conversion.
    [xc, yc, zc] = r3f.ecef_to_curvilinear([xe0, ye0, ze0])
    assert np.allclose([xc, yc, zc], [0.0, 0.0, 0.0])


def test_geodetic_tangent():
    # This test depends on geodetic_to_ecef and ecef_to_tangent.

    # Build test points.
    N = 10
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, size=N)
    lon = np.random.uniform(-np.pi, np.pi, size=N)
    hae = np.random.uniform(-10e3, 100e3, size=N)
    lat0 = lat[0]
    lon0 = lon[0]
    hae0 = hae[0]

    # Test geodetic to tangent with transpose and lists.
    llh = np.array([lat, lon, hae])
    [xt, yt, zt] = r3f.geodetic_to_tangent(llh.T.tolist(), [lat0, lon0, hae0]).T
    [xe, ye, ze] = r3f.geodetic_to_ecef([lat, lon, hae])
    [xe0, ye0, ze0] = r3f.geodetic_to_ecef([lat0, lon0, hae0])
    [XT, YT, ZT] = r3f.ecef_to_tangent([xe, ye, ze], [xe0, ye0, ze0])
    assert np.allclose(xt, XT)
    assert np.allclose(yt, YT)
    assert np.allclose(zt, ZT)

    # Test reciprocal.
    [LAT, LON, HAE] = r3f.tangent_to_geodetic([xt, yt, zt], [lat0, lon0, hae0])
    assert np.allclose(lat, LAT)
    assert np.allclose(lon, LON)
    assert np.allclose(hae, HAE)

    # Test with no llh0.
    [xt, yt, zt] = r3f.geodetic_to_tangent(llh)
    assert np.allclose(xt, XT)
    assert np.allclose(yt, YT)
    assert np.allclose(zt, ZT)

    # Test trivial conversion.
    [xt, yt, zt] = r3f.geodetic_to_tangent([lat0, lon0, hae0])
    assert np.allclose([xt, yt, zt], [0.0, 0.0, 0.0])


def test_curvilinear_tangent():
    N = 10
    lat = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL, size=N)
    lon = np.random.uniform(-np.pi, np.pi, size=N)
    hae = np.random.uniform(-10e3, 100e3, size=N)
    lat0 = np.random.uniform(-np.pi/2 + r3f.TOL, np.pi/2 - r3f.TOL)
    lon0 = np.random.uniform(-np.pi, np.pi)
    hae0 = np.random.uniform(-10e3, 100e3)
    [xc, yc, zc] = r3f.geodetic_to_curvilinear([lat, lon, hae], [lat0, lon0, hae0])
    [xt, yt, zt] = r3f.curvilinear_to_tangent([xc, yc, zc], [lat0, lon0, hae0])
    [xe, ye, ze] = r3f.geodetic_to_ecef([lat, lon, hae])
    [xe0, ye0, ze0] = r3f.geodetic_to_ecef([lat0, lon0, hae0])
    [XT, YT, ZT] = r3f.ecef_to_tangent([xe, ye, ze], [xe0, ye0, ze0])
    assert np.allclose(xt, XT)
    assert np.allclose(yt, YT)
    assert np.allclose(zt, ZT)
    [XC, YC, ZC] = r3f.tangent_to_curvilinear([xt, yt, zt], [xe0, ye0, ze0])
    assert np.allclose(xc, XC)
    assert np.allclose(yc, YC)
    assert np.allclose(zc, ZC)

# -------------------------
# Rotation Matrix Utilities
# -------------------------

def test_is_ortho():
    # Test non-orthogonal matrix with list.
    C = [[1.0, 0, 0],
            [0, 2.0, 0],
            [0, 0, 1.0]]
    assert r3f.is_ortho(C) is False

    # Test orthogonal matrix.
    C = np.array([[1.0, 0, 0],
            [0, 1.0, 0],
            [0, 0, 1.0]])
    assert r3f.is_ortho(C) is True

    # Test orthogonal array of matrices.
    C = np.zeros((5, 3, 3))
    for j in range(C.shape[0]):
        C[j, :, :] = np.eye(3)
    assert r3f.is_ortho(C) is True


def test_orthonormalize_dcm():
    # Build valid rotation matrices.
    J = 100_000
    C = np.zeros((J, 3, 3))
    for j in range(J):
        for m in range(J):
            c = np.random.randn(3, 3)
            if np.dot(np.cross(c[0], c[1]), c[2]) > 0:
                break
        C[j] = c

    # Test single matrix with list.
    D = C[0] + 0
    D = r3f.mgs(D.tolist())
    B = (D.T @ D) - np.eye(3)
    assert np.sum(np.abs(B)) < 1e-12

    assert r3f.is_ortho(D)
    Q, _ = np.linalg.qr(D)
    for i in range(3):
        if np.dot(Q[:, i], D[:, i]) < 0:
            Q[:, i] *= -1
    print(Q)
    print(D)
    assert np.allclose(D, Q)

    # Run many single matrix tests.
    N = 10
    eo = np.zeros((N, J))
    for n in range(0, N):
        D = C + 0
        for m in range(0, n + 1):
            D = r3f.mgs(D)
        B = (np.transpose(D, (0, 2, 1)) @ D) - np.eye(3)
        eo[n] = np.sum(np.sum(np.abs(B), axis=1), axis=1)

    nn = np.arange(N) + 1
    e_max = np.max(eo, axis=1)
    assert np.all(e_max[1:] < 1e-12)


def test_rodrigues():
    # Test single.
    theta = np.random.randn(3)
    Delta = r3f.rodrigues(theta)
    Theta = r3f.rodrigues_inv(Delta)
    assert np.allclose(theta, Theta)

    # Test multiple with transpose and lists.
    K = 1000
    theta = np.random.randn(3, K)
    delta = np.zeros((K, 3, 3))
    for k in range(K):
        delta[k, :, :] = r3f.rodrigues(theta[:, k])
    for k in range(K):
        theta[:, k] = r3f.rodrigues_inv(delta[k, :, :])
    Delta = r3f.rodrigues(theta.T.tolist())
    assert np.allclose(delta, Delta)
    Theta = r3f.rodrigues_inv(Delta.tolist())
    assert np.allclose(theta, Theta)

    # Check zero matrix.
    try:
        Delta[-1, :, :] = 0
        r3f.rodrigues_inv(Delta)
    except ValueError as e:
        assert True

    # Test 180 degree rotation.
    theta = np.array([1, 1, 0])
    theta = theta/np.linalg.norm(theta)*np.pi
    delta = r3f.rodrigues(theta)
    Delta = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1.0]])
    assert np.allclose(delta, Delta)
    try:
        r3f.rodrigues_inv(Delta)
    except:
        assert True
