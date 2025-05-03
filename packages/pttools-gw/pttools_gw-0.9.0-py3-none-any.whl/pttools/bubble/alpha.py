r"""
Functions for computing $\alpha_n$, the strength parameter at nucleation temperature,
and $\alpha_+$, the strength parameter just in front of the wall.
"""

import threading
import typing as tp

import numba
from numba.extending import overload
import numpy as np
from scipy.optimize import fsolve

import pttools.type_hints as th
from pttools import speedup
from pttools.bubble import bag
from pttools.bubble import boundary
from pttools.bubble import const
from pttools.bubble import fluid_bag
from pttools.bubble import check
from pttools.bubble import integrate
from pttools.bubble import props
from pttools.bubble import transition


CS2CACHE: tp.Dict[th.CS2FunScalarPtr, th.CS2CFunc] = {}
find_alpha_plus_scalar_lock = threading.Lock()


@numba.njit
def alpha_n_max_bag(v_wall: th.FloatOrArr, n_xi: int = const.N_XI_DEFAULT) -> th.FloatOrArr:
    r"""
    Calculates the maximum relative trace anomaly outside the bubble, $\alpha_{n,\max}$,
    in the Bag Model for given $v_\text{wall}$, which is max $\alpha_n$ for (supersonic) deflagration.

    :param v_wall: $v_\text{wall}$
    :param n_xi: number of $\xi$ points
    :return: $\alpha_{n,\max}$, the relative trace anomaly outside the bubble
    """
    return alpha_n_max_deflagration_bag(v_wall, n_xi)


# @numba.njit
def _alpha_n_max_deflagration_bag_scalar(v_wall: th.FloatOrArr, n_xi: int = const.N_XI_DEFAULT) -> th.FloatOrArr:
    check.check_wall_speed(v_wall)
    sol_type = boundary.SolutionType.HYBRID.value if v_wall > const.CS0 else boundary.SolutionType.SUB_DEF.value
    ap = 1. / 3 - 1.0e-10  # Warning - this is not safe.  Causes warnings for v low vw
    _, w, xi = fluid_bag.sound_shell_alpha_plus(v_wall, ap, sol_type, n_xi)
    n_wall = props.find_v_index(xi, v_wall)
    return w[n_wall + 1] * (1. / 3)


_alpha_n_max_deflagration_bag_scalar_numba = numba.njit(_alpha_n_max_deflagration_bag_scalar)


@numba.njit(parallel=True)
def _alpha_n_max_deflagration_bag_arr(v_wall: th.FloatOrArr, n_xi: int = const.N_XI_DEFAULT) -> np.ndarray:
    ret = np.zeros_like(v_wall)
    for i in numba.prange(v_wall.size):
        ret[i] = _alpha_n_max_deflagration_bag_scalar_numba(v_wall[i], n_xi)
    # alpha_N = (w_+/w_N)*alpha_+
    # w_ is normalised to 1 at large xi
    # Need n_wall+1, as w is an integral of v, and lags by 1 step
    return ret


def _alpha_n_max_deflagration_bag_arr_wrapper(v_wall: th.FloatOrArr, n_xi: int = const.N_XI_DEFAULT) -> np.ndarray:
    return _alpha_n_max_deflagration_bag_arr(v_wall, n_xi)


def alpha_n_max_deflagration_bag(v_wall: th.FloatOrArr, n_xi: int = const.N_XI_DEFAULT) -> th.FloatOrArr:
    r"""
    Calculates the maximum relative trace anomaly outside the bubble, $\alpha_{n,\max}$,
    in the Bag Model for given $v_\text{wall}$, for deflagration.
    Works also for hybrids, as they are supersonic deflagrations.

    :param v_wall: $v_\text{wall}$
    :param n_xi: number of $\xi$ points
    :return: $\alpha_{n,\max}$
    """
    if isinstance(v_wall, float):
        return _alpha_n_max_deflagration_bag_scalar(v_wall, n_xi)
    if isinstance(v_wall, np.ndarray):
        if not v_wall.ndim:
            return _alpha_n_max_deflagration_bag_scalar(v_wall.item(), n_xi)
        return _alpha_n_max_deflagration_bag_arr(v_wall, n_xi)
    raise TypeError(f"Unknown type for v_wall: {type(v_wall)}")


@overload(alpha_n_max_deflagration_bag, jit_options={"nopython": True})
def _alpha_n_max_deflagration_bag_numba(v_wall: th.FloatOrArr, n_xi: int = const.N_XI_DEFAULT) -> th.FloatOrArr:
    if isinstance(v_wall, numba.types.Float):
        return _alpha_n_max_deflagration_bag_scalar
    if isinstance(v_wall, numba.types.Array):
        if not v_wall.ndim:
            return _alpha_n_max_deflagration_bag_scalar
        return _alpha_n_max_deflagration_bag_arr_wrapper
    raise TypeError(f"Unknown type for v_wall: {type(v_wall)}")


@numba.njit
def alpha_n_max_detonation_bag(v_wall: th.FloatOrArr) -> th.FloatOrArr:
    r"""
    Maximum allowed value of $\alpha_n$ for a detonation with wall speed $v_\text{wall}$ in the Bag Model.
    Same as :func:`alpha_plus_max_detonation`, since for a detonation $\alpha_n = \alpha_+$,
    as there is no fluid movement outside the wall.

    :param v_wall: $v_\text{wall}$
    :return: $\alpha_{n,\max,\text{detonation}}$
    """
    return alpha_plus_max_detonation_bag(v_wall)


@numba.njit
def alpha_n_max_hybrid_bag(v_wall: float, n_xi: int = const.N_XI_DEFAULT) -> float:
    r"""
    Calculates the relative trace anomaly outside the bubble, $\alpha_{n,\max}$,
    in the Bag Model for given $v_\text{wall}$, assuming hybrid fluid shell

    :param v_wall: $v_\text{wall}$
    :param n_xi: number of $\xi$ points
    :return: $\alpha_{n,\max}$
    """
    sol_type = transition.identify_solution_type_alpha_plus(v_wall, 1/3).value
    if sol_type == boundary.SolutionType.SUB_DEF:
        raise ValueError("Alpha_n_max_hybrid was called with v_wall < cs. Use alpha_n_max_deflagration instead.")

    # Might have been returned as "Detonation, which takes precedence over Hybrid
    sol_type = boundary.SolutionType.HYBRID.value
    ap = 1/3 - 1e-8
    _, w, xi = fluid_bag.sound_shell_alpha_plus(v_wall, ap, sol_type, n_xi)
    n_wall = props.find_v_index(xi, v_wall)

    # alpha_N = (w_+/w_N)*alpha_+
    # w_ is normalised to 1 at large xi
    return w[n_wall] * 1/3


@numba.njit
def alpha_n_min_deflagration_bag(v_wall: th.FloatOrArr) -> th.FloatOrArr:
    r"""
    Minimum $\alpha_n$ for a deflagration in the Bag Model. Equal to maximum $\alpha_n$ for a detonation.
    Same as :func:`alpha_n_min_hybrid`, as a hybrid is a supersonic deflagration.

    :param v_wall: $v_\text{wall}$
    :return: $\alpha_{n,\min,\text{deflagration}} = \alpha_{n,\min,\text{hybrid}} = \alpha_{n,\max,\text{detonation}}$
    """
    # This check is implemented in the inner functions
    # check.check_wall_speed(v_wall)
    return alpha_n_max_detonation_bag(v_wall)


@numba.njit
def alpha_n_min_hybrid_bag(v_wall: th.FloatOrArr) -> th.FloatOrArr:
    r"""
    Minimum $\alpha_n$ for a hybrid in the Bag Model. Equal to maximum $\alpha_n$ for a detonation.
    Same as :func:`alpha_n_min_deflagration`, as a hybrid is a supersonic deflagration.

    :param v_wall: $v_\text{wall}$
    :return: $\alpha_{n,\min,\text{hybrid}} = \alpha_{n,\min,\text{deflagration}} = \alpha_{n,\max,\text{detonation}}$
    """
    # This check is implemented in the inner functions
    # check.check_wall_speed(v_wall)
    return alpha_n_max_detonation_bag(v_wall)


@numba.njit
def alpha_plus_initial_guess(v_wall: th.FloatOrArr, alpha_n_given: float) -> th.FloatOrArr:
    r"""
    Initial guess for root-finding of $\alpha_+$ from $\alpha_n$.
    Linear approx between $\alpha_{n,\min}$ and $\alpha_{n,\max}$.
    Doesn't do obvious checks like Detonation - needs improving?

    :param v_wall: $v_\text{wall}$, wall speed
    :param alpha_n_given: $\alpha_{n, \text{given}}$
    :return: initial guess for $\alpha_+$
    """
    if alpha_n_given < 0.05:
        return alpha_n_given

    alpha_plus_min = alpha_plus_min_hybrid(v_wall)
    alpha_plus_max = 1. / 3

    alpha_n_min = alpha_n_min_hybrid_bag(v_wall)
    alpha_n_max = alpha_n_max_deflagration_bag(v_wall)

    slope = (alpha_plus_max - alpha_plus_min) / (alpha_n_max - alpha_n_min)
    return alpha_plus_min + slope * (alpha_n_given - alpha_n_min)


@speedup.vectorize(nopython=True)
def alpha_plus_max_detonation_bag(v_wall: th.FloatOrArr) -> th.FloatOrArrNumba:
    r"""
    Maximum allowed value of $\alpha_+$ for a detonation with wall speed $v_\text{wall}$ in the Bag Model.
    Comes from inverting $v_w$ > $v_\text{Jouguet}$.

    $\alpha_{+,\max,\text{detonation}} = \frac{ (1 - \sqrt{3} v_\text{wall})^2 }{ 3(1 - v_\text{wall}^2 }$
    """
    check.check_wall_speed(v_wall)
    if v_wall < const.CS0:
        return 0
    a = 3 * (1 - v_wall ** 2)
    b = (1 - np.sqrt(3) * v_wall) ** 2
    return b / a


@speedup.vectorize(nopython=True)
def alpha_plus_min_hybrid(v_wall: th.FloatOrArr) -> th.FloatOrArrNumba:
    r"""
    Minimum allowed value of $\alpha_+$ for a hybrid with wall speed $v_\text{wall}$ in the Bag Model.
    Condition from coincidence of wall and shock.

    $$\alpha_{+, \min, \text{hybrid}} = \frac{ (1 - \sqrt{3} v_\text{wall})^2 }{ 9 v_\text{wall}^2 - 1}$$

    Todo: Is this specific to the bag model?

    :param v_wall: $v_\text{wall}$
    :return: $\alpha_{+, \min, \text{hybrid}}$
    """
    check.check_wall_speed(v_wall)
    if v_wall < const.CS0:
        return 0
    b = (1 - np.sqrt(3) * v_wall) ** 2
    c = 9 * v_wall ** 2 - 1
    return b / c


@numba.njit
def find_alpha_n_bag(
        v_wall: th.FloatOrArr,
        alpha_p: float,
        sol_type: boundary.SolutionType = boundary.SolutionType.UNKNOWN,
        n_xi: int = const.N_XI_DEFAULT,
        cs2_fun: th.CS2Fun = bag.cs2_bag,
        df_dtau_ptr: speedup.DifferentialPointer = integrate.DF_DTAU_BAG_PTR) -> float:
    r"""
    Calculates the transition strength parameter at the nucleation temperature,
    $\alpha_n$, from $\alpha_+$, for given $v_\text{wall}$ in the Bag Model.

    $$\alpha_n = \frac{4 \Delta \theta (T_n)}{3 w(T_n)} = \frac{4}{3} \frac{ \theta_s(T_n) - \theta_b(T_n) }{w(T_n)}$$

    :param v_wall: $v_\text{wall}$, wall speed
    :param alpha_p: $\alpha_+$, the at-wall strength parameter.
    :param sol_type: type of the bubble (detonation, deflagration etc.)
    :param n_xi: number of $\xi$ values to investigate
    :param cs2_fun: $c_s^2$ function
    :param df_dtau_ptr: pointer to the differential equations
    :return: $\alpha_n$, global strength parameter
    """
    check.check_wall_speed(v_wall)
    if sol_type == boundary.SolutionType.UNKNOWN.value:
        sol_type = transition.identify_solution_type_alpha_plus(v_wall, alpha_p).value
    _, w, xi = fluid_bag.sound_shell_alpha_plus(v_wall, alpha_p, sol_type, n_xi, cs2_fun=cs2_fun, df_dtau_ptr=df_dtau_ptr)
    n_wall = props.find_v_index(xi, v_wall)
    return alpha_p * w[n_wall] / w[-1]


@numba.njit
def find_alpha_n_from_w_xi(w: np.ndarray, xi: np.ndarray, v_wall: float, alpha_p: th.FloatOrArr) -> th.FloatOrArr:
    r"""
    Calculates the transition strength parameter with
    $$\alpha_n = \frac{w_+}{w_n} \alpha_p$$.

    Model-independent.

    :param w: $w$ array of a bubble
    :param xi: $xi$ array of a bubble
    :param v_wall: $v_\text{wall}$
    :param alpha_p: $\alpha_+$
    :return: $\alpha_n$
    """
    n_wall = props.find_v_index(xi, v_wall)
    wn = w[-1]
    return w[n_wall] / wn * alpha_p


@numba.njit
def _find_alpha_plus_optimizer_bag(
        alpha: np.ndarray,
        v_wall: float,
        sol_type: boundary.SolutionType,
        n_xi: int,
        alpha_n_given: float,
        cs2_fun: th.CS2Fun,
        df_dtau_ptr: speedup.DifferentialPointer) -> float:
    """find_alpha_plus() is looking for the zeroes of this function: $\alpha_n = \alpha_{n,\text{given}}$."""
    return find_alpha_n_bag(v_wall, alpha.item(), sol_type, n_xi, cs2_fun=cs2_fun, df_dtau_ptr=df_dtau_ptr) - alpha_n_given


def _find_alpha_plus_scalar_cs2_converter(cs2_fun_ptr: th.CS2FunScalarPtr) -> th.CS2CFunc:
    r"""Converter for getting a $c_s^2$ ctypes function from a pointer

    This is a rather ugly hack. There should be a better way to call a function by a pointer!
    """
    with find_alpha_plus_scalar_lock:
        if cs2_fun_ptr in CS2CACHE:
            return CS2CACHE[cs2_fun_ptr]
        # https://numba.pydata.org/numba-doc/0.15.1/interface_c.html
        cs2_fun = th.CS2CFunc(cs2_fun_ptr)
        CS2CACHE[cs2_fun_ptr] = cs2_fun
        return cs2_fun


# @numba.njit
def _find_alpha_plus_scalar_bag(
        v_wall: th.FloatOrArr,
        alpha_n_given: float,
        n_xi: int = const.N_XI_DEFAULT,
        cs2_fun_ptr: th.CS2FunScalarPtr = bag.CS2_BAG_SCALAR_PTR,
        df_dtau_ptr: speedup.DifferentialPointer = integrate.DF_DTAU_BAG_PTR,
        xtol: float = const.FIND_ALPHA_PLUS_TOL) -> th.FloatOrArrNumba:
    if alpha_n_given < alpha_n_max_detonation_bag(v_wall):
        # Must be detonation
        # sol_type = boundary.SolutionType.DETON
        return alpha_n_given
    if alpha_n_given >= alpha_n_max_deflagration_bag(v_wall):
        # Greater than the maximum possible -> fail
        return np.nan
    sol_type = boundary.SolutionType.SUB_DEF if v_wall <= const.CS0 else boundary.SolutionType.HYBRID
    ap_initial_guess = alpha_plus_initial_guess(v_wall, alpha_n_given)
    with numba.objmode(ret="float64"):
        cs2_fun = _find_alpha_plus_scalar_cs2_converter(cs2_fun_ptr)

        # This returns np.float64
        ret: float = fsolve(
            _find_alpha_plus_optimizer_bag,
            ap_initial_guess,
            args=(v_wall, sol_type, n_xi, alpha_n_given, cs2_fun, df_dtau_ptr),
            xtol=xtol,
            factor=0.1)[0]
    return ret


@numba.njit(parallel=True)
def _find_alpha_plus_bag_arr(
        v_wall: th.FloatOrArr,
        alpha_n_given: float,
        n_xi: int = const.N_XI_DEFAULT,
        cs2_fun_ptr: th.CS2FunScalarPtr = bag.CS2_BAG_SCALAR_PTR,
        df_dtau_ptr: speedup.DifferentialPointer = integrate.DF_DTAU_BAG_PTR,
        xtol: float = const.FIND_ALPHA_PLUS_TOL) -> th.FloatOrArrNumba:
    ap = np.zeros_like(v_wall)
    for i in numba.prange(v_wall.size):
        ap[i] = _find_alpha_plus_scalar_bag(v_wall[i], alpha_n_given, n_xi, cs2_fun_ptr=cs2_fun_ptr, df_dtau_ptr=df_dtau_ptr)
    return ap


def _find_alpha_plus_bag_arr_wrapper(
        v_wall: th.FloatOrArr,
        alpha_n_given: float,
        n_xi: int = const.N_XI_DEFAULT,
        cs2_fun_ptr: th.CS2FunScalarPtr = bag.CS2_BAG_SCALAR_PTR,
        df_dtau_ptr: speedup.DifferentialPointer = integrate.DF_DTAU_BAG_PTR,
        xtol: float = const.FIND_ALPHA_PLUS_TOL) -> th.FloatOrArrNumba:
    return _find_alpha_plus_bag_arr(
        v_wall=v_wall, alpha_n_given=alpha_n_given, n_xi=n_xi,
        cs2_fun_ptr=cs2_fun_ptr, df_dtau_ptr=df_dtau_ptr, xtol=xtol
    )


def find_alpha_plus_bag(
        v_wall: th.FloatOrArr,
        alpha_n_given: float,
        n_xi: int = const.N_XI_DEFAULT,
        cs2_fun_ptr: th.CS2FunScalarPtr = bag.CS2_BAG_SCALAR_PTR,
        df_dtau_ptr: speedup.DifferentialPointer = integrate.DF_DTAU_BAG_PTR,
        xtol: float = const.FIND_ALPHA_PLUS_TOL) -> th.FloatOrArrNumba:
    r"""
    Calculate the at-wall strength parameter $\alpha_+$ from given $\alpha_n$ and $v_\text{wall}$ in the Bag Model.

    $$\alpha_+ = \frac{4 \Delta \theta (T_+)}{3 w_+} = \frac{4}{3} \frac{ \theta_s(T_+) - \theta_b(T_+) }{w(T_+)}$$
    (:gw_pt_ssm:`\ `, eq. 2.11)

    Uses :func:`scipy.optimize.fsolve` and therefore spends time in the Python interpreter even when jitted.
    This should be taken into account when running parallel simulations.

    :param v_wall: $v_\text{wall}$, the wall speed
    :param alpha_n_given: $\alpha_n$, the global strength parameter
    :param n_xi: number of $\xi$ points
    :return: $\alpha_+$, the the at-wall strength parameter
    """
    if isinstance(v_wall, float):
        return _find_alpha_plus_scalar_bag(v_wall, alpha_n_given, n_xi, cs2_fun_ptr=cs2_fun_ptr, df_dtau_ptr=df_dtau_ptr, xtol=xtol)
    if isinstance(v_wall, np.ndarray):
        if not v_wall.ndim:
            return _find_alpha_plus_scalar_bag(v_wall.item(), alpha_n_given, n_xi, cs2_fun_ptr=cs2_fun_ptr, df_dtau_ptr=df_dtau_ptr, xtol=xtol)
        return _find_alpha_plus_bag_arr(v_wall, alpha_n_given, n_xi, cs2_fun_ptr=cs2_fun_ptr, df_dtau_ptr=df_dtau_ptr, xtol=xtol)
    raise TypeError(f"Unknown type for v_wall: {type(v_wall)}")


@overload(find_alpha_plus_bag, jit_options={"nopython": True})
def _find_alpha_plus_bag_numba(
        v_wall: th.FloatOrArr,
        alpha_n_given: float,
        n_xi: int = const.N_XI_DEFAULT,
        cs2_fun_ptr: th.CS2FunScalarPtr = bag.CS2_BAG_SCALAR_PTR,
        df_dtau_ptr: speedup.DifferentialPointer = integrate.DF_DTAU_BAG_PTR,
        xtol: float = const.FIND_ALPHA_PLUS_TOL) -> th.FloatOrArrNumba:
    if isinstance(v_wall, numba.types.Float):
        return _find_alpha_plus_scalar_bag
    if isinstance(v_wall, numba.types.Array):
        if not v_wall.ndim:
            return _find_alpha_plus_scalar_bag
        return _find_alpha_plus_bag_arr_wrapper
    raise TypeError(f"Unknown type for v_wall: {type(v_wall)}")
