import numpy as np
import pandas as pd
import scipy
import scipy.constants as constants


def uptime(df: pd.DataFrame, gain: float = 1, sample_rate: float = 25, critical_angle: float = 39) -> float:
    """
    Return a float representing the Upright Position Time of the session.
    This function will return a percentage of the session spent in the upright position.
    Length of the session is solely determined by the length of the provided DataFrame and sample rate.
    """
    # apply gain to all columns except epoc (ms)
    df[df.columns.difference(["epoc (ms)"])] *= gain

    # initialize
    uptime = pd.DataFrame(
        columns=["epoc (ms)", "upright (0/1)", "angle (deg)"])
    filtered = pd.DataFrame(
        columns=["epoc (ms)",
                 "x-axis (m/s^2)", "y-axis (m/s^2)", "z-axis (m/s^2)",
                 "x-axis (rad/s)", "y-axis (rad/s)", "z-axis (rad/s)"]
    )

    # convert g to m/s^2 and deg/s to rad/s
    df[["x-axis (m/s^2)", "y-axis (m/s^2)", "z-axis (m/s^2)"]] = df[["x-axis (g)", "y-axis (g)", "z-axis (g)"]] * constants.g
    df[["x-axis (rad/s)", "y-axis (rad/s)", "z-axis (rad/s)"]] = np.deg2rad(df[["x-axis (deg/s)", "y-axis (deg/s)", "z-axis (deg/s)"]])

    # time between two sample points
    dt = 1 / sample_rate
    # 2nd order 10 Hz low-pass
    [b, a] = scipy.signal.butter(2, 10 / (sample_rate / 2), "low")

    # timestamp
    uptime["epoc (ms)"] = df["epoc (ms)"]

    # apply filter to each axis
    filtered = df.copy()
    for col in ["x-axis (m/s^2)", "y-axis (m/s^2)", "z-axis (m/s^2)", "x-axis (rad/s)", "y-axis (rad/s)", "z-axis (rad/s)"]:
        filtered[col] = scipy.signal.lfilter(b, a, df[col])

    # trigonometric estimations of roll and pitch using raw accelerometer data
    filtered["acce-phi-hat"] = np.arctan2(filtered["y-axis (m/s^2)"], np.sqrt(filtered["x-axis (m/s^2)"] ** 2 + filtered["z-axis (m/s^2)"] ** 2))
    filtered["acce-theta-hat"] = np.arctan2(-filtered["x-axis (m/s^2)"], np.sqrt(filtered["y-axis (m/s^2)"] ** 2 + filtered["z-axis (m/s^2)"] ** 2))

    # state-space form of kalman filter
    a = np.array([
        [1, -dt, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, -dt],
        [0, 0, 0, 1]
    ])
    b = np.array([
        [dt, 0, 0, 0],
        [0, 0, dt, 0],
    ]).T
    c = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
    ])

    # initial error covariance matrix (4 x 4 identity matrix init with 1)
    # large values = unsure if initial state is correct
    # small values = confident that initial guess is correct
    p = np.eye(4) * 1

    # process covariance matrix (4 x 4 identity matrix init with 0.01)
    # large values = model is inaccurate
    # small values = model is accurate
    q = np.eye(4) * 0.01

    # measurement noise covariance matrix (2 x 2 identity matrix init with 10)
    # large values = greater sensor noise
    # small values = minimal sensor noise
    r = np.eye(2) * 10

    # initial value estimate (4 x 1 matrix)
    state_estimate = np.array([
        constants.pi / 2,
        0,
        0,
        0,
    ]).T

    # vector initialization
    phi = np.zeros(len(filtered))
    bias_phi = np.zeros(len(filtered))
    theta = np.zeros(len(filtered))
    bias_theta = np.zeros(len(filtered))

    # kalman filter
    for i in range(len(filtered)):
        gryo_x = filtered["x-axis (rad/s)"][i]
        gryo_y = filtered["y-axis (rad/s)"][i]
        gryo_z = filtered["z-axis (rad/s)"][i]

        phi_hat = phi[i - 1]
        theta_hat = theta[i - 1]

        # generate input vector
        phi_dot = gryo_x + \
            np.sin(phi_hat) * np.tan(theta_hat) * gryo_y + \
            np.cos(phi_hat) * np.tan(theta_hat) * gryo_z

        theta_dot = np.cos(phi_hat) * gryo_y - \
            np.sin(phi_hat) * gryo_z

        # predict state
        state_estimate = a @ state_estimate + \
            b @ np.array([
                phi_dot,
                theta_dot,
            ]).T

        # predict error covariance
        p = a @ p @ a.T + q

        # update
        measurement = np.array([
            filtered["acce-phi-hat"][i],
            filtered["acce-theta-hat"][i],
        ]).T

        y_tilde = measurement - c @ state_estimate

        s = r + c @ p @ c.T
        k = p @ c.T @ np.linalg.inv(s)

        state_estimate = state_estimate + k @ y_tilde

        p = (np.eye(4) - k @ c) @ p

        phi[i] = state_estimate[0]
        bias_phi[i] = state_estimate[1]
        theta[i] = state_estimate[2]
        bias_theta[i] = state_estimate[3]

    # convert phi and theta to a single angle output using quaternions
    roll = constants.pi / 2 - phi
    pitch = theta
    qr, qi, qj, qk = np.cos(roll / 2) * np.cos(pitch / 2), np.sin(roll / 2) * np.cos(pitch / 2), np.cos(roll / 2) * np.sin(pitch / 2), np.sin(roll / 2) * np.sin(pitch / 2)

    # angle in radians
    angle_rad = 2 * np.arctan2(np.sqrt(qi ** 2 + qj ** 2 + qk ** 2), qr)
    # angle in degrees
    angle_deg = np.degrees(angle_rad)

    return np.sum(critical_angle > angle_deg) / len(angle_deg)
