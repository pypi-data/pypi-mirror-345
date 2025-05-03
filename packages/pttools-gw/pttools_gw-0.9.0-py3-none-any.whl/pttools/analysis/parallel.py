"""Utilities for parallel simulation of bubbles"""

import logging
import time
import typing as tp

import numpy as np

from pttools.bubble.bubble import Bubble
from pttools.bubble import fluid_reference
from pttools.bubble.integrate import precompile
from pttools.omgw0.omgw0_ssm import Spectrum
from pttools.speedup import options
from pttools.speedup.parallel import run_parallel
if tp.TYPE_CHECKING:
    from pttools.models.model import Model

logger = logging.getLogger(__name__)


def create_bubble(
        params: np.ndarray,
        model: "Model",
        post_func: callable = None,
        post_func_return_multiple: bool = False,
        use_bag_solver: bool = False,
        bubble_kwargs: tp.Dict[str, any] = None,
        allow_bubble_failure: bool = False,
        *args, **kwargs) -> tp.Union[tp.Optional[Bubble], tp.Tuple[tp.Optional[Bubble], tp.Any]]:
    """Create a single bubble and apply post-processing functions to retrieve results from it"""
    v_wall, alpha_n = params
    # This is a common error case and should be handled here to avoid polluting the logs with exceptions.
    if alpha_n < model.alpha_n_min and bubble_kwargs is not None \
            and ("allow_invalid" not in bubble_kwargs or not bubble_kwargs["allow_invalid"]):
        logger.error("Invalid alpha_n=%s. Minimum for the model: %s", alpha_n, model.alpha_n_min)
        return None, post_func.fail_value
    try:
        if bubble_kwargs is None:
            bubble = Bubble(model, v_wall, alpha_n, solve=False)
        else:
            bubble = Bubble(model, v_wall, alpha_n, solve=False, **bubble_kwargs)
    except Exception as e:
        if allow_bubble_failure:
            logger.exception("Failed to create a bubble:", exc_info=e)
            if post_func is None:
                return None
            if post_func_return_multiple:
                return None, *post_func.fail_value
            return None, post_func.fail_value
        raise e
    bubble.solve(use_bag_solver=use_bag_solver)
    if post_func is not None:
        if post_func_return_multiple:
            return bubble, *post_func(bubble, *args, **kwargs)
        return bubble, post_func(bubble, *args, **kwargs)
    return bubble


def create_spectrum(
        params: np.ndarray,
        model: "Model",
        post_func: callable = None,
        post_func_return_multiple: bool = False,
        use_bag_solver: bool = False,
        bubble_kwargs: tp.Dict[str, any] = None,
        spectrum_kwargs: tp.Dict[str, any] = None,
        allow_bubble_failure: bool = False,
        *args, **kwargs):
    """Create a single spectrum and apply post-processing functions to retrieve results from it"""
    bubble = create_bubble(
        params=params,
        model=model,
        use_bag_solver=use_bag_solver,
        bubble_kwargs=bubble_kwargs,
        allow_bubble_failure=allow_bubble_failure
    )
    if spectrum_kwargs is None:
        spectrum = Spectrum(bubble=bubble)
    else:
        spectrum = Spectrum(bubble=bubble, **spectrum_kwargs)

    if post_func is not None:
        if post_func_return_multiple:
            return spectrum, *post_func(spectrum, *args, **kwargs)
        return spectrum, post_func(spectrum, *args, **kwargs)
    return spectrum


def create_bubbles(
        model: "Model",
        v_walls: np.ndarray,
        alpha_ns: np.ndarray,
        func: callable = None,
        log_progress_percentage: float = 10,
        max_workers: int = options.MAX_WORKERS_DEFAULT,
        single_thread: bool = False,
        allow_bubble_failure: bool = False,
        kwargs: tp.Dict[str, any] = None,
        bubble_kwargs: tp.Dict[str, any] = None,
        bubble_func: callable = create_bubble) -> tp.Union[np.ndarray, tp.Tuple[np.ndarray, np.ndarray, ...]]:
    """Create multiple bubbles in parallel"""
    start_time = time.perf_counter()
    post_func_return_multiple = False
    if func is None:
        output_dtypes = None
    else:
        if not hasattr(func, "return_type"):
            raise ValueError("The function should have a return_type attribute for output array initialization")

        if isinstance(func.return_type, tuple):
            output_dtypes = (object, *func.return_type)
            post_func_return_multiple = True
        else:
            output_dtypes = (object, func.return_type)

    kwargs2 = {
        "model": model,
        "post_func": func,
        "post_func_return_multiple": post_func_return_multiple,
        "bubble_kwargs": bubble_kwargs,
        "allow_bubble_failure": allow_bubble_failure
    }
    if kwargs is not None:
        kwargs2.update(kwargs)

    params = np.empty((alpha_ns.size, v_walls.size, 2))
    for i_alpha_n, alpha_n in enumerate(alpha_ns):
        for i_v_wall, v_wall in enumerate(v_walls):
            params[i_alpha_n, i_v_wall, 0] = v_wall
            params[i_alpha_n, i_v_wall, 1] = alpha_n

    # Pre-do shared steps so that they don't have to be done for each process
    fluid_reference.ref()
    model.df_dtau_ptr()
    precompile()

    # Run the parallel processing
    ret = run_parallel(
        bubble_func, params,
        multiple_params=True,
        output_dtypes=output_dtypes,
        max_workers=max_workers,
        single_thread=single_thread,
        log_progress_percentage=log_progress_percentage,
        kwargs=kwargs2
    )
    bubble_count = alpha_ns.size * v_walls.size
    elapsed = time.perf_counter() - start_time
    elapsed_per_bubble = elapsed / bubble_count
    logger.debug(
        "Creating %s bubbles took %.3f s in total, %.3f s per bubble",
        bubble_count, elapsed, elapsed_per_bubble
    )
    return ret


def create_spectra(
        model: "Model",
        v_walls: np.ndarray,
        alpha_ns: np.ndarray,
        func: callable = None,
        log_progress_percentage: float = 5,
        max_workers: int = options.MAX_WORKERS_DEFAULT,
        single_thread: bool = False,
        allow_bubble_failure: bool = False,
        kwargs: tp.Dict[str, any] = None,
        bubble_kwargs: tp.Dict[str, any] = None,
        spectrum_kwargs: tp.Dict[str, any] = None) -> np.ndarray:
    """Create multiple spectra in parallel"""
    if kwargs is None:
        kwargs2 = {"spectrum_kwargs": spectrum_kwargs}
    else:
        kwargs2 = kwargs.copy()
        kwargs2["spectrum_kwargs"] = spectrum_kwargs
    return create_bubbles(
        model=model,
        v_walls=v_walls,
        alpha_ns=alpha_ns,
        func=func,
        log_progress_percentage=log_progress_percentage,
        max_workers=max_workers,
        single_thread=single_thread,
        allow_bubble_failure=allow_bubble_failure,
        kwargs=kwargs2,
        bubble_kwargs=bubble_kwargs,
        bubble_func=create_spectrum
    )


def solve_bubble(bubble: Bubble) -> None:
    bubble.solve()


def solve_bubbles(bubbles: np.ndarray, max_workers: int = options.MAX_WORKERS_DEFAULT) -> None:
    """Solve multiple existing bubbles in parallel"""
    run_parallel(solve_bubble, params=bubbles, max_workers=max_workers)
