import numpy as np
from astropy import units as u
from astropy.time import Time


# TODO: Fully understand this
def solve_eccentric_anomaly(mean_anomaly, eccentricity):
    """Solves the eccentric anomaly numerically.

    NOTES
    -----
    A method defined similar to the binary search
    from J. Meeus 1991 Chapter 29 Third Method.
    """
    mean_anomaly %= 2 * np.pi
    if mean_anomaly > np.pi:
        mean_anomaly = 2 * np.pi - mean_anomaly
        sign = -1
    else:
        sign = 1

    e0, d0 = np.pi / 2, np.pi / 4
    for _ in range(33):
        m1 = e0 - eccentricity * np.sin(e0)
        e0 = e0 + d0 * np.sign(mean_anomaly - m1)
        d0 /= 2

    return e0 * sign


def compute_true_anomaly(eccentric_anomaly, eccentricity):
    return 2 * np.arctan(
        np.sqrt((1 + eccentricity) / (1 - eccentricity)) * np.tan(eccentric_anomaly / 2)
    )


def date_to_epoch(date: str) -> float:
    """Converts the date to floating point number of the form <year>.<percentage>."""
    return Time(date, format="iso").decimalyear


def get_epoch(
    epoch: u.yr,
    period: u.yr,
    eccentricity: u.one,
    semi_major_axis: u.au,
    inclination: u.deg,
    periapsis_time: u.yr,
    argument_periapsis: u.deg,
    long_ascending_node: u.deg,
):
    """

    NOTES
    -----
    From J. Meeus+1991 Chapter 55 Binary Stars.
    """
    mean_anomaly = 2 * np.pi * (epoch - periapsis_time) / period
    eccentric_anomaly = solve_eccentric_anomaly(mean_anomaly.value, eccentricity.value)
    true_anomaly = compute_true_anomaly(eccentric_anomaly, eccentricity)

    # NOTE: Up to here soley Kepler, see Chapter 55 for these calculations
    theta = np.arctan2(
        np.cos(true_anomaly + argument_periapsis.to(u.rad)),
        np.sin(true_anomaly + argument_periapsis.to(u.rad)) * np.cos(inclination),
    )
    theta = (theta + long_ascending_node.to(u.rad)).to(u.deg)

    radius = semi_major_axis * (1 - eccentricity * np.cos(eccentric_anomaly))
    rho = (
        radius
        * np.sin(true_anomaly + argument_periapsis.to(u.rad))
        / np.cos(theta - long_ascending_node)
    )
    return rho, theta


def get_orbit(
    period: u.yr,
    eccentricity: u.one,
    semi_major_axis: u.au,
    inclination: u.deg,
    periapsis_time: u.yr,
    argument_periapsis: u.deg,
    long_ascending_node: u.deg,
):
    rhos, thetas = [], []
    for epoch in np.linspace(periapsis_time, periapsis_time + period, 1024):
        rho, theta = get_epoch(
            epoch,
            period,
            eccentricity,
            semi_major_axis,
            inclination,
            periapsis_time,
            argument_periapsis,
            long_ascending_node,
        )
        rhos.append(rho)
        thetas.append(theta)

    return u.Quantity(rhos), u.Quantity(thetas)
