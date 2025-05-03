r"""
Thermodynamic quantities

The code for the integrals doesn't have the pre-factor $4\pi$,
since the integrals are computed with respect to $\xi^3$,
which is equivalent.

The volume-averaged and bubble volume averaged quantities are different, and should not be confused with each other.

The integrals are computed using the trapezoidal rule and with respect to $\xi^3$,
since the functions are constant outside the bubble, where the functions are constant, but very few points are given.
This scheme gives the correct results for these ranges,
as the trapezoidal rule computes the integral of a constant function exactly, even when only the endpoints are given.
If the integrals were with respect to $\xi$, the functions would have the factor $\xi^2$,
which would break this useful property and require a more dense grid of points.
"""

import logging
import typing as tp

import numpy as np

import pttools.type_hints as th
from .boundary import Phase
from . import props
from . import relativity
if tp.TYPE_CHECKING:
    from pttools.models.model import Model

logger = logging.getLogger(__name__)

# Todo: Fix the equations in the docstrings


def entropy_density_diff(model: "Model", w: np.ndarray, xi: np.ndarray, v_wall: float, phase: np.ndarray = None) -> float:
    r"""Bubble volume averaged entropy density
    $$\frac{3}{4\pi v_w^3} {s}_\text{avg}$$
    """
    return 3/(4*np.pi * v_wall**3) * va_entropy_density_diff(model, w, xi, v_wall, phase)


def kinetic_energy_density(v: np.ndarray, w: np.ndarray, xi: np.ndarray, v_wall: float) -> float:
    r"""Bubble volume averaged kinetic energy density
    $$\frac{3}{4\pi {v}_w^3} \Delta {e}_Q$$
    """
    return 3/(4*np.pi * v_wall**3) * va_kinetic_energy_density(v, w, xi)


def kinetic_energy_fraction(ek_bva: float, eb: float) -> float:
    r"""Bubble volume averaged kinetic energy fraction
    $$K_\text{bva} = \frac{e_{K,\text{bva}}}{\bar{e}}$$
    """
    return ek_bva / eb


def thermal_energy_density(v_wall: float, eqp: float) -> float:
    r"""Bubble volume averaged thermal energy density after the phase transition
    $${e}_Q' = {e}_Q + {e}_\theta - {e}_K' - {e}_\theta' = 4\pi \int_0^{{\xi}_\text{max}} d\xi \xi^2 \frac{3}{4} {w}_n - {e}_K' - \Delta {e}_\theta$$
    """
    return 3/(4*np.pi * v_wall**3) * eqp


def thermal_energy_density_diff(w: np.ndarray, xi: np.ndarray, v_wall: float) -> float:
    r"""Bubble volume averaged thermal energy density difference"""
    return 3/(4*np.pi * v_wall**3) * va_thermal_energy_density_diff(w, xi)


def thermal_energy_fraction(eq_bva: th.FloatOrArr, eb: th.FloatOrArr) -> th.FloatOrArr:
    r"""Thermal energy fraction $\frac{e_Q'}{\bar{e}}$

    :param eq_bva: thermal energy density $e_Q'$
    :param eb: average energy density $\bar{e}$
    :return: thermal energy fraction
    """
    return eq_bva / eb


def trace_anomaly_diff(model: "Model", w: np.ndarray, xi: np.ndarray, v_wall: float, phase: np.ndarray = None) -> float:
    r"""Bubble volume averaged trace anomaly
    $$\epsilon = \frac{3}{4\pi {v}_w^3} \Delta {e}_\theta$$
    """
    return 3/(4*np.pi * v_wall**3) * va_trace_anomaly_diff(model, w, xi, v_wall, phase)


def ebar(model: "Model", wn: float) -> float:
    r"""Energy is conserved, and therefore $\bar{e}=e_n$."""
    return model.e(wn, Phase.SYMMETRIC)


def kappa(
        model: "Model",
        v: np.ndarray, w: np.ndarray, xi: np.ndarray,
        v_wall: float,
        delta_e_theta: float = None) -> float:
    r"""Kinetic efficiency factor
    $$\kappa = \frac{e_K}{\lvert\Delta {e}_\theta\rvert}$$
    """
    if delta_e_theta is None:
        delta_e_theta = va_trace_anomaly_diff(model, w, xi, v_wall)
    return va_kinetic_energy_density(v, w, xi) / np.abs(delta_e_theta)


def kappa_approx(alpha_n: th.FloatOrArr) -> th.FloatOrArr:
    r"""Approximate kinetic efficiency factor"""
    return alpha_n / (0.73 + 0.083*np.sqrt(alpha_n) + alpha_n)


# @numba.njit
def mean_adiabatic_index(wb: th.FloatOrArr, eb: th.FloatOrArr) -> th.FloatOrArr:
    r"""Mean adiabatic index
    $$\Gamma = \frac{\bar{w}}{\bar{e}}$$
    """
    return wb / eb


def omega(
        model: "Model",
        w: np.ndarray, xi: np.ndarray,
        v_wall: float,
        delta_e_theta: float = None) -> float:
    r"""Thermal efficiency factor
    $$\omega = \frac{\Delta {e}_Q}{\Delta {e}_\theta}$$
    """
    if delta_e_theta is None:
        delta_e_theta = va_trace_anomaly_diff(model, w, xi, v_wall)
    return va_thermal_energy_density_diff(w, xi) / np.abs(delta_e_theta)


def ubarf2(v: np.ndarray, w: np.ndarray, xi: np.ndarray, v_wall: float, ek_bva: float = None) -> float:
    r"""Enthalpy-weighted mean square fluid 4-velocity around the bubble
    $$\bar{U}_f^2 = \frac{3}{4\pi \bar{w} v_w^3} e_K$$

    Presumes that w[-1] = wn = wbar
    """
    if ek_bva is None:
        ek_bva = kinetic_energy_density(v, w, xi, v_wall)
    return ek_bva / w[-1]


def wbar(w: np.ndarray, xi: np.ndarray, v_wall: float, wn: float) -> float:
    r"""Average enthalpy density $\bar{w}$"""
    # https://stackoverflow.com/a/8768734
    w_reverse = w[::-1]
    i_max = w.size - np.argmax(w_reverse != w[-1]) - 1
    if i_max == 0:
        i_max = -1
    ret = 1/(xi[i_max]**3) * np.trapezoid(w[:i_max+1], xi[:i_max+1]**3)
    if not (ret is None or np.isnan(ret)) and ret <= wn:
        logger.warning(f"Should have wbar > wn. Got: wbar={wn}, wn={wn}")
    return ret


def va_enthalpy_density(eq: float) -> float:
    """Volume-averaged enthalpy density"""
    return 4/3 * eq


def va_entropy_density_diff(model: "Model", w: np.ndarray, xi: np.ndarray, v_wall: float, phase: np.ndarray = None) -> float:
    r"""
    Volume-averaged entropy density
    $${s}_\text{avg} = \int d\xi \xi^2 (s(w,\phi) - s(w_n, \phi_s)$$
    """
    if phase is None:
        phase = props.find_phase(xi, v_wall)
    return 4*np.pi/3 * np.trapezoid(model.s(w, phase) - model.s(w[-1], Phase.SYMMETRIC), xi**3)


# @numba.njit
def va_kinetic_energy_density(v: np.ndarray, w: np.ndarray, xi: np.ndarray) -> float:
    r"""
    Volume-averaged kinetic energy density
    $${e}_K = 4 \pi \int_0^{{\xi}_\text{max}} d\xi \xi^2 w \gamma^2 v^2$$
    Each point is multiplied by $v$, and therefore having ${\xi}_{max}$ too far does not affect the results.
    :gw_pt_ssm:`\ ` eq. B.22

    :param v: $v$
    :param w: $w$
    :param xi: $\xi$
    :return: $e_K$
    """
    return 4*np.pi/3 * np.trapezoid(w * v**2 * relativity.gamma2(v), xi**3)


def va_kinetic_energy_fraction(ek_va: float, eb: float) -> float:
    r"""Volume-averaged kinetic energy fraction
    $$K_\text{va} = \frac{e_{K,\text{va}}}{\bar{e}}$$
    """
    return ek_va / eb


def va_thermal_energy_density(v_shock: float, wn: float, ek: float, delta_e_theta: float) -> float:
    r"""Volume-averaged thermal energy density after the phase transition
    $${e}_Q' = {e}_Q + {e}_\theta - {e}_K' - {e}_\theta' = 4\pi \int_0^{{\xi}_\text{max}} d\xi \xi^2 \frac{3}{4} {w}_n - {e}_K' - \Delta {e}_\theta$$
    """
    return np.pi * wn * v_shock**3 - ek - delta_e_theta


# @numba.njit
def va_thermal_energy_density_diff(w: np.ndarray, xi: np.ndarray) -> float:
    r"""Volume-averaged thermal energy density
    $$\Delta e_Q = 4 \pi \int_0^{\xi_\text{max}} d\xi \xi^2 \frac{3}{4} (w - w_n)$$
    """
    return 4*np.pi/3 * np.trapezoid(0.75*(w - w[-1]), xi**3)


def va_thermal_energy_fraction(eq_va: float, eb: float):
    r"""Volume-averaged kinetic energy fraction
    $$Q_\text{va} = \frac{e_{Q,\text{va}}}{\bar{e}}$$
    """
    return eq_va / eb


def va_trace_anomaly_diff(model: "Model", w: np.ndarray, xi: np.ndarray, v_wall: float, phase: np.ndarray = None) -> float:
    r"""Volume-averaged trace anomaly difference
    $$\Delta {e}_\theta = 4 \pi \int_0^{{\xi}_\text{max}} d\xi \xi^2 (\theta - {\theta}_n)$$
    """
    if phase is None:
        phase = props.find_phase(xi, v_wall)
    theta = model.theta(w, phase)
    theta_n = model.theta(w[-1], Phase.SYMMETRIC)
    return 4*np.pi/3 * np.trapezoid((theta - theta_n), xi**3)
