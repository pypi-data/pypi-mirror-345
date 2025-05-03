"""Bag model"""

import logging
import typing as tp

import numba
import numpy as np

from pttools.bubble import Phase
from pttools.bubble.boundary import SolutionType
from pttools.bubble.integrate import add_df_dtau, differentials
from pttools.bubble.transition import identify_solution_type_bag
from pttools.models.analytic import AnalyticModel
from pttools.speedup.differential import DifferentialPointer
from pttools.speedup.utils import copy_doc
import pttools.type_hints as th

logger = logging.getLogger(__name__)


@numba.njit
def cs2_bag(w: th.FloatOrArr = None, phase: th.FloatOrArr = None) -> th.FloatOrArr:
    r"""Sound speed squared, $c_s^2=\frac{1}{3}$.
    :notes:`\ `, p. 37,
    :rel_hydro_book:`\ `, eq. 2.207
    """
    return 1/3 * np.ones_like(w) * np.ones_like(phase)

df_dtau_ptr_bag = differentials.get_pointer("bag") if "bag" in differentials else add_df_dtau("bag", cs2_bag)


class BagModel(AnalyticModel):
    r"""Bag equation of state.
    This is one of the simplest equations of state for a relativistic plasma.
    Each integration corresponds to a line on the figure below (fig. 9 of :gw_pt_ssm:`\ `).

    .. plot:: fig/xi_v_plane.py

    """
    DEFAULT_LABEL_LATEX = "Bag model"
    DEFAULT_LABEL_UNICODE = DEFAULT_LABEL_LATEX
    DEFAULT_NAME = "bag"
    TEMPERATURE_IS_PHYSICAL = False

    def __init__(
            self,
            V_s: float = AnalyticModel.DEFAULT_V_S, V_b: float = AnalyticModel.DEFAULT_V_B,
            a_s: float = None, a_b: float = None,
            g_s: float = None, g_b: float = None,
            T_min: float = None, T_max: float = None,
            alpha_n_min: float = None,
            name: str = None,
            label_latex: str = None,
            label_unicode: str = None,
            allow_invalid: bool = False,
            auto_potential: bool = False,
            log_info: bool = True):
        if log_info:
            logger.debug("Initialising BagModel")
        if V_b != 0:
            logger.warning("V_b has been specified for the bag model, even though it's usually omitted.")
        if alpha_n_min is not None:
            a_s, a_b, _, _ = self.get_a_g(a_s, a_b, g_s, g_b)
            a_s, a_b, V_s, V_b = self.alpha_n_min_find_params(
                alpha_n_min_target=alpha_n_min, a_s_default=a_s, a_b=a_b, V_s=V_s, V_b=V_b)

        super().__init__(
            V_s=V_s, V_b=V_b,
            a_s=a_s, a_b=a_b,
            g_s=g_s, g_b=g_b,
            T_min=T_min, T_max=T_max,
            name=name, label_latex=label_latex, label_unicode=label_unicode,
            gen_cs2=False, gen_cs2_neg=False,
            allow_invalid=allow_invalid,
            auto_potential=auto_potential,
            log_info=log_info
        )
        if self.a_s <= self.a_b:
            raise ValueError(
                "The bag model must have a_s > a_b for the critical temperature to be non-negative. "
                f"Got: a_s={self.a_s}, a_b={self.a_b}"
            )
        # The < case already generates an error in the base class, but let's check that as well just to be sure.
        if self.V_s <= self.V_b:
            msg = f"The bubble will not expand in the Bag model, when V_s <= V_b. Got: V_s = V_b = {V_s}"
            logger.error(msg)
            if not allow_invalid:
                raise ValueError(msg)

        # These have to be after super().__init__() for a_s and a_b to be populated.
        label_prec = 3
        if self.label_latex is self.DEFAULT_LABEL_LATEX:
            self.label_latex = \
                f"Bag, $a_s={self.a_s:.{label_prec}f}, a_b={self.a_b:.{label_prec}f}, " \
                f"V_s={self.V_s:.{label_prec}f}, V_b={self.V_b:.{label_prec}f}$"
        if self.label_unicode is self.DEFAULT_LABEL_UNICODE:
            self.label_unicode = \
                f"Bag, a_s={self.a_s:.{label_prec}f}, a_b={self.a_b:.{label_prec}f}, " \
                f"V_s={self.V_s:.{label_prec}f}, V_b={self.V_b:.{label_prec}f}"

    @copy_doc(AnalyticModel.alpha_plus_bag)
    def alpha_n(
            self,
            wn: th.FloatOrArr,
            error_on_invalid: bool = True,
            nan_on_invalid: bool = True,
            log_invalid: bool = True) -> th.FloatOrArr:
        return self.alpha_n_bag(
            wn=wn,
            error_on_invalid=error_on_invalid,
            nan_on_invalid=nan_on_invalid,
            log_invalid=log_invalid
        )

    def alpha_n_min_find(self, w_min: float = None, w_max: float = None) -> tp.Tuple[float, float]:
        return self.w_crit, self.alpha_n(self.w_crit)

    @classmethod
    def alpha_n_min_find_params(
            cls,
            alpha_n_min_target: float,
            a_s_default: float = None,
            a_b: float = 1,
            V_s: float = None,
            V_b: float = 0,
            safety_factor_alpha: float = None) -> tp.Tuple[float, float, float, float]:
        if a_s_default < 0 or a_b < 0 or V_s < 0 or V_b < 0:
            raise ValueError(
                f"Invalid parameters: a_s_default={a_s_default}, a_b={a_b}, V_s_default={V_s}, V_b={V_b}")
        if safety_factor_alpha is None:
            safety_factor_alpha = cls.ALPHA_N_MIN_FIND_SAFETY_FACTOR_ALPHA
        a_s = a_b / (1 - 3*alpha_n_min_target * safety_factor_alpha)
        if a_s_default is not None and a_s_default < a_s:
            a_s = a_s_default
        return a_s, a_b, V_s, V_b

    @copy_doc(AnalyticModel.alpha_plus_bag)
    def alpha_plus(
            self,
            wp: th.FloatOrArr,
            wm: th.FloatOrArr,
            vp_tilde: float = None,
            sol_type: SolutionType = None,
            error_on_invalid: bool = True,
            nan_on_invalid: bool = True,
            log_invalid: bool = True) -> th.FloatOrArr:
        return self.alpha_plus_bag(
            wp=wp, wm=wm, vp_tilde=vp_tilde,
            sol_type=sol_type,
            error_on_invalid=error_on_invalid,
            nan_on_invalid=nan_on_invalid,
            log_invalid=log_invalid
        )

    def alpha_theta_bar_n(
            self,
            wn: th.FloatOrArr,
            error_on_invalid: bool = True,
            nan_on_invalid: bool = True,
            log_invalid: bool = True) -> th.FloatOrArr:
        return self.alpha_n(
            wn=wn,
            error_on_invalid=error_on_invalid,
            nan_on_invalid=nan_on_invalid,
            log_invalid=log_invalid
        )

    def alpha_theta_bar_plus(
            self,
            wp: th.FloatOrArr,
            error_on_invalid: bool = True,
            nan_on_invalid: bool = True,
            log_invalid: bool = True) -> th.FloatOrArr:
        return self.alpha_plus(
            wp=wp,
            wm=np.nan,  # Not used
            error_on_invalid=error_on_invalid,
            nan_on_invalid=nan_on_invalid,
            log_invalid=log_invalid
        )

    def critical_temp(self, **kwargs) -> float:
        r"""Critical temperature for the bag model

        $$T_{cr} = \sqrt[4]{\frac{V_s - V_b}{a_s - a_b}}$$
        Note that :giese_2020:`\ ` p. 6 is using a different convention.
        """
        return ((self.V_s - self.V_b) / (self.a_s - self.a_b))**0.25

    cs2 = staticmethod(cs2_bag)

    def cs2_max(
            self,
            w_max: float, phase: Phase,
            w_min: float = 0, allow_fail: bool = False, **kwargs) -> tp.Tuple[float, float]:
        return 1/3, np.nan

    def cs2_min(
                self,
                w_max: float, phase: Phase,
                w_min: float = 0, allow_fail: bool = False, **kwargs) -> tp.Tuple[float, float]:
        return 1/3, np.nan

    @staticmethod
    @numba.njit
    def cs2_neg(w: th.FloatOrArr = None, phase: th.FloatOrArr = None) -> th.FloatOrArr:
        return - 1/3 * np.ones_like(w) * np.ones_like(phase)

    @staticmethod
    @numba.njit
    def cs2_temp(temp, phase):
        return cs2_bag(temp, phase)

    def delta_theta(
            self,
            wp: th.FloatOrArr, wm: th.FloatOrArr,
            error_on_invalid: bool = True, nan_on_invalid: bool = True, log_invalid: bool = True) -> th.FloatOrArr:
        delta_theta = (self.V_s - self.V_b) * np.ones_like(wp) * np.ones_like(wm)
        return self.check_delta_theta(
            delta_theta, wp=wp, wm=wm,
            error_on_invalid=error_on_invalid, nan_on_invalid=nan_on_invalid, log_invalid=log_invalid
        )

    def df_dtau_ptr(self) -> DifferentialPointer:
        return df_dtau_ptr_bag

    def e_temp(self, temp: th.FloatOrArr, phase: th.FloatOrArr) -> th.FloatOrArr:
        r"""Energy density as a function of temperature, :giese_2021:`\ ` eq. 15, :borsanyi_2016:`\ `, eq. S12
        The convention for $a_s$ and $a_b$ is that of :notes:`\ `, eq. 7.33.
        """
        self.validate_temp(temp)
        e_s = 3*self.a_s * temp**4 + self.V_s
        e_b = 3*self.a_b * temp**4 + self.V_b
        return e_b * phase + e_s * (1 - phase)

    # def nu_gdh2024(self, w: th.FloatOrArr, phase: th.FloatOrArr = Phase.BROKEN) -> th.FloatOrArr:
    #     """This is not the case when V != 0"""
    #     return np.zeros_like(w) * np.zeros_like(phase)

    # def omega(self, w: th.FloatOrArr, phase: th.FloatOrArr) -> th.FloatOrArr:
    #     """This is not the case when V != 0"""
    #     return 1/3 * np.ones_like(w) * np.ones_like(phase)

    def p_temp(self, temp: th.FloatOrArr, phase: th.FloatOrArr) -> th.FloatOrArr:
        r"""Pressure $p(T,\phi)$, :notes:`\ `, eq. 5.14, 7.1, 7.33, :giese_2021:`\ `, eq. 18
        $$p_s = a_s T^4$$
        $$p_b = a_b T^4$$
        The convention for $a_s$ and $a_b$ is that of :notes:`\ ` eq. 7.33.
        """
        self.validate_temp(temp)
        p_s = self.a_s * temp**4 - self.V_s
        p_b = self.a_b * temp**4 - self.V_b
        return p_b * phase + p_s * (1 - phase)

    def params_str(self) -> str:
        return f"a_s={self.a_s}, a_b={self.a_b}, V_s={self.V_s}, V_b={self.V_b}"

    def s_temp(self, temp: th.FloatOrArr, phase: th.FloatOrArr) -> th.FloatOrArr:
        r"""Entropy density $s=\frac{dp}{dT}$
        $$s_s = 4 a_s T^3$$
        $$s_b = 4 a_b T^3$$
        Derived from :notes:`\ ` eq. 7.33.
        """
        self.validate_temp(temp)
        s_s = 4*self.a_s*temp**3
        s_b = 4*self.a_b*temp**3
        return s_b * phase + s_s * (1 - phase)

    def solution_type(
            self,
            v_wall: float,
            alpha_n: float,
            wn: float = None,
            wn_guess: float = None,
            wm_guess: float = None) -> SolutionType:
        return identify_solution_type_bag(v_wall=v_wall, alpha_n=alpha_n)

    def temp(self, w: th.FloatOrArr, phase: th.FloatOrArr) -> th.FloatOrArr:
        r"""Temperature $T(w,\phi)$. Inverted from
        $$T(w) = \sqrt[4]{\frac{w}{4a(\phi)}}$$

        :param w: enthalpy $w$
        :param phase: phase $\phi$
        :return: temperature $T(w,\phi)$
        """
        # return (w / (4*(self.a_b*phase + self.a_s*(1-phase))))**(1/4)
        # Defined in the same way as for ConstCSModel
        temp_s = (w / (4*self.a_s))**0.25
        temp_b = (w / (4*self.a_b))**0.25
        return temp_b * phase + temp_s * (1 - phase)

    def theta(self, w: th.FloatOrArr, phase: th.FloatOrArr) -> th.FloatOrArr:
        """Trace anomaly $\theta$

        For the bag model the trace anomaly $\theta$ does not depend on the enthalpy.
        """
        return (self.V_b * phase + self.V_s * (1 - phase)) * np.ones_like(w)

    @staticmethod
    def v_shock(xi: th.FloatOrArr) -> th.FloatOrArr:
        r"""Velocity at the shock, :gw_pt_ssm:`\ ` eq. B.17
        $$v_\text{sh}(\xi) = \frac{3\xi^22 - 1}{2\xi}$$
        """
        return (3*xi**2 - 1)/(2*xi)

    def w(self, temp: th.FloatOrArr, phase: th.FloatOrArr) -> th.FloatOrArr:
        r"""Enthalpy $w(T)$
        $$w(T) = 4a(\phi)T^4$$

        :param temp: temperature $T$
        :param phase: phase $\phi$
        """
        self.validate_temp(temp)
        return 4 * (self.a_b * phase + self.a_s * (1-phase))*temp**4

    def wn(
            self,
            alpha_n: th.FloatOrArr,
            wn_guess: float = 1,
            analytical: bool = True,
            theta_bar: bool = False,
            error_on_invalid: bool = True,
            nan_on_invalid: bool = True,
            log_invalid: bool = True) -> th.FloatOrArr:
        r"""Enthalpy at nucleation temperature
        $$w_n = \frac{4}{3} \frac{V_s - V_b}{\alpha_n}$$
        This can be derived from the equations for $\theta$ and $\alpha_n$.
        """
        if theta_bar:
            super().wn(
                alpha_n, wn_guess=wn_guess, theta_bar=theta_bar,
                error_on_invalid=error_on_invalid, nan_on_invalid=nan_on_invalid, log_invalid=log_invalid
            )
        if analytical:
            return self.bag_wn_const / alpha_n
        return super().wn(
            alpha_n, wn_guess,
            error_on_invalid=error_on_invalid, nan_on_invalid=nan_on_invalid, log_invalid=log_invalid
        )

    @staticmethod
    def w_shock(xi: th.FloatOrArr, w_n: th.FloatOrArr) -> th.FloatOrArr:
        r"""Enthalpy at the shock, :gw_pt_ssm:`\ ` eq. B.18
        $$w_\text{sh}(\xi) = w_n \frac{9\xi^2 - 1}{3(1-\xi^2)}$$
        """
        return w_n * (9*xi**2 - 1)/(2*(1-xi**2))
