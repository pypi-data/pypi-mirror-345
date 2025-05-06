"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h
from pathlib import Path as path_t

from babelplot.runtime.backends import BACKENDS
from babelplot.type.dimension import dim_e
from babelplot.type.figure import figure_t
from babelplot.type.frame import frame_t
from babelplot.type.plot import plot_t
from babelplot.type.plot_function import plot_function_h
from babelplot.type.plot_type import plot_type_h


def NewFigure(
    *args,
    title: str | None = None,
    offline_version: bool = False,
    backend: str | path_t | None = None,
    **kwargs,
) -> figure_t | None:
    """"""
    backend_name, actual_figure_t = BACKENDS.Activate(backend)
    if backend_name is None:
        return None

    return actual_figure_t.New(
        backend_name,
        *args,
        title=title,
        offline_version=offline_version,
        **kwargs,
    )


def NewPlot(
    type_: plot_type_h | plot_function_h,
    *plt_args,
    fig_args=(),
    frm_args=(),
    fig_kwargs: dict[str, h.Any] | None = None,
    frm_kwargs: dict[str, h.Any] | None = None,
    fig_title: str | None = None,
    frm_title: str | None = None,
    plt_title: str | None = None,
    dim: str | dim_e = dim_e.XY,
    backend: str | path_t | None = None,
    should_show: bool = True,
    modal: bool = True,
    **plt_kwargs,
) -> tuple[figure_t, frame_t, plot_t] | None:
    """"""
    if fig_kwargs is None:
        fig_kwargs = {}
    if frm_kwargs is None:
        frm_kwargs = {}
    if plt_kwargs is None:
        plt_kwargs = {}

    figure = NewFigure(
        *fig_args,
        title=fig_title,
        backend=backend,
        **fig_kwargs,
    )
    if figure is None:
        return None

    frame = figure.AddFrame(
        *frm_args,
        title=frm_title,
        dim=dim,
        **frm_kwargs,
    )
    plot = frame.AddPlot(
        type_,
        *plt_args,
        title=plt_title,
        **plt_kwargs,
    )

    if should_show:
        figure.Show(modal=modal)

    if should_show and modal:
        return None

    return figure, frame, plot


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
