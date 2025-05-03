from contextlib import contextmanager
from typing import Any, Generator, Union

import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy import ndarray

from .styles import PAPER_FORMATS, Layout, Style


@contextmanager
def get_context(
    layout: Layout,
    width_frac: float = 1,
    height_frac: float = 0.15,
    single_col: bool = False,
    nrows: int = 1,
    ncols: int = 1,
    override_rc_params: dict[str, Any] = dict(),
    **kwargs: Any,
) -> Generator[tuple[Figure, Union[Axes, ndarray[Any, Any]]], None, None]:
    rc_params, fig_width_in, fig_height_in = get_mpl_rcParams(
        layout=layout,
        width_frac=width_frac,
        height_frac=height_frac,
        single_col=single_col,
    )
    rc_params.update(override_rc_params)

    with plt.rc_context(rc_params):
        fig, axs = plt.subplots(nrows, ncols, constrained_layout=True, **kwargs)
        fig.set_size_inches(fig_width_in, fig_height_in)
        yield (fig, axs)


def get_mpl_rcParams(
    layout: Layout,
    width_frac: float = 1,
    height_frac: float = 0.15,
    single_col: bool = False,
) -> tuple[dict[str, Any], float, float]:
    """Get matplotlib rcParams dict and fig width & height in inches, depending on the
    chosen layout and fractional width and height. Fractional here in the sense that
    The resulting fig width/height in inches is calculated as `width_frac\\linewidth`
    and `height_frac\\textheight` in LaTeX. Usage:

    ```python
        rc_params, fig_width_in, fig_height_in = pub_ready_plots.get_mpl_rcParams(
            layout=Layout.ICML, width_frac=fig_width_frac, height_frac=fig_height_frac
        )
        plt.rcParams.update(rc_params)

        fig, axs = plt.subplots(
            nrows,
            ncols,
            constrained_layout=True, # Important!
        )
        fig.set_size_inches(fig_width_in, fig_height_in)

        # Your plot here!

        plt.savefig("filename.pdf")
    ```

    Then in your LaTeX file, include the plot as follows:

    ```tex
        \\includegraphics[width=\\linewidth]{filename.pdf}
    ```

    The arg. `width=\\linewidth` is important!

    Args:
        layout: The LaTeX template used. Possible values are Layout.ICML, Layout.NeurIPS,
            Layout.ICLR, Layout.AISTATS, Layout.UAI, Layout.JMLR, Layout.TMLR,
            Layout.POSTER_PORTRAIT (A1, 2-column),
            and Layout.POSTER_LANDSCAPE (A0, 3-col).
        width_frac: Fraction of `\\linewidth` as the figure width. Usually set to 1.
        height_frac: Fraction of `\\textheight` as the figure height. Try 0.175.
        single_col: Whether the plot is single column in a layout that has multiple
            columns (e.g. ICML, posters). Not supported for any other layout.

    Returns:
        rc_params: Matplotlib key-value rc-params. Use it via
            `plt.rcParams.update(rc_params)`. Note that you can always override/add
            key-values to this dict before applying it.
        fig_width_in: figure width in inches.
        fig_height_in: figure height in inches.
    """
    if (width_frac <= 0 or width_frac > 1) or (height_frac <= 0 or height_frac > 1):
        raise ValueError("Both `width_frac` and `height_frac` must be between 0 and 1.")

    if (
        layout
        not in [
            Layout.ICML,
            Layout.AISTATS,
            Layout.UAI,
            Layout.POSTER_PORTRAIT,
            Layout.POSTER_LANDSCAPE,
        ]
        and single_col
    ):
        raise ValueError(
            """Double-column is only supported for ICML, AISTATS, UAI, """
            """POSTER_PORTRAIT, and POSTER_LANDSCAPE."""
        )

    format: Style = PAPER_FORMATS[layout]
    is_poster_or_slides: bool = any(
        name in layout._name_.lower() for name in ["poster", "slides"]
    )

    rc_params = {
        "text.usetex": False,
        "font.size": format.footnote_size,
        "font.family": "sans-serif" if is_poster_or_slides else "serif",
        "font.serif": [format.font_name] + rcParams["font.serif"],
        "font.sans-serif": [format.font_name, "Times"] + rcParams["font.sans-serif"],
        "mathtext.fontset": "stixsans" if is_poster_or_slides else "cm",
        "lines.linewidth": format.linewidth,
        "axes.linewidth": format.linewidth / 2,
        "axes.titlesize": format.footnote_size,
        "axes.labelsize": format.script_size,
        "axes.unicode_minus": False,
        "axes.formatter.use_mathtext": True,
        "legend.fontsize": format.script_size,
        "xtick.labelsize": format.script_size,
        "ytick.labelsize": format.script_size,
        "xtick.major.size": format.tick_size,
        "ytick.major.size": format.tick_size,
        "xtick.major.width": format.tick_width,
        "ytick.major.width": format.tick_width,
    }

    w = width_frac * (format.col_width if single_col else format.text_width)
    h = height_frac * format.text_height

    return rc_params, w, h
