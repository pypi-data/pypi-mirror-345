"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h
from multiprocessing import Process as process_t

from color_spec_changer.translation import NewTranslatedColor
from babelplot.task.plotting import NewPlotFunctionsTemplate, SetDefaultPlotFunction
from babelplot.type.dimension import dim_e
from babelplot.type.figure import figure_t as base_figure_t
from babelplot.type.frame import frame_t as base_frame_t
from babelplot.type.plot import plot_t as base_plot_t
from babelplot.type.plot_function import plot_function_h
from babelplot.type.plot_type import plot_e, plot_type_h
from numpy import ndarray as array_t
from vedo import Mesh as backend_mesh_t  # noqa
from vedo import Text2D as text_2d_t  # noqa
from vedo import Volume as volume_t  # noqa
from vedo import show as BackendShow  # noqa
from vedo.pyplot import plot as NewBackendPlot  # noqa

NAME = "vedo"

_MIN_HEIGHT_RATIO = 0.4

backend_plot_h = h.TypeVar("backend_plot_h")


@d.dataclass(slots=True, repr=False, eq=False)
class plot_t(base_plot_t): ...


@d.dataclass(slots=True, repr=False, eq=False)
class frame_t(base_frame_t):

    @property
    def backend_plots(self) -> list[backend_plot_h]:
        """"""
        output = []

        for plot in self.plots:
            if plot.title is None:
                output.append(plot.raw)
            else:
                output.append((plot.raw, plot.title))

        return output

    def _NewPlot(
        self,
        plot_function: plot_function_h,
        *args,
        title: str | None = None,  # If _, then it is swallowed by kwargs!
        type_: tuple[plot_type_h | plot_function_h, int],
        **kwargs,
    ) -> plot_t:
        """"""
        return plot_t(
            title=title,
            property=kwargs.copy(),
            backend_name=self.backend_name,
            raw=plot_function(*args, **kwargs),
        )


@d.dataclass(slots=True, repr=False, eq=False)
class figure_t(base_figure_t):

    @property
    def backend_plots_s(self) -> list[list[backend_plot_h]]:
        """"""
        return [_.backend_plots for _ in self.frames]

    def _NewBackendFigure(self, *args, **kwargs) -> None:
        """"""
        return None

    def _NewFrame(
        self,
        title: str | None,
        dim: dim_e,
        row: int,
        col: int,
        *args,
        **kwargs,
    ) -> frame_t:
        """"""
        return frame_t(
            title=title,
            dim=dim,
            backend_name=self.backend_name,
        )

    def _BackendShow(self, modal: bool, /) -> None:
        """"""
        _ShowAndClose = lambda: BackendShow(
            self.backend_plots_s, shape=self.shape, sharecam=False
        ).close()

        # Passing [...].close shows the figures one by one. Using _ShowAndClose instead.
        process = process_t(target=_ShowAndClose)
        process.start()

        if modal:
            process.join()
        else:
            self.showing_process = process


def _DefaultFunction(type_: plot_e, frame_dim: int, /) -> plot_function_h:
    """"""

    def Actual(*args, **kwargs) -> backend_plot_h:
        #
        return text_2d_t(
            plot_t.UnhandledRequestMessage(type_, *args, frame_dim=frame_dim, **kwargs),
            pos="middle-left",
            s=1.0,
            bold=True,
            c="red",
        )

    return Actual


def _ElevationSurface(elevation: array_t, *args, **kwargs) -> backend_plot_h:
    """"""
    (n_rows, n_cols), min_z, max_z = elevation.shape, elevation.min(), elevation.max()
    max_length = max(n_rows, n_cols)
    height = max_z - min_z

    if (height > 0) and (height / max_length < _MIN_HEIGHT_RATIO):
        scaling = _MIN_HEIGHT_RATIO * max_length / height
        if scaling.is_integer():
            scaling = int(scaling)
            equality = "="
        else:
            rounded = round(scaling)
            rounded_length = str(rounded).__len__()
            precision = max(3 - rounded_length, 0)
            if precision > 0:
                scaling = round(scaling, ndigits=precision)
            else:
                scaling = rounded
            equality = "≈"
        kwarg_axes = {"axes": {"ztitle": f"Scaling{equality}{scaling}"}}
    else:
        scaling = 1.0
        kwarg_axes = {}

    Elevation = lambda _row, _col: scaling * float(elevation[round(_row), round(_col)])

    return NewBackendPlot(
        Elevation, xlim=(0, n_rows), ylim=(0, n_cols), c="summer", **kwarg_axes
    )


def _IsoSurface(volume: array_t, iso_value: float, *_, **kwargs) -> backend_mesh_t:
    """"""
    return volume_t(volume).isosurface(value=[iso_value], **kwargs)


def _Mesh(triangles: array_t, vertices: array_t, *_, **kwargs) -> backend_mesh_t:
    """"""
    output = backend_mesh_t((vertices, triangles))

    if "width_edge" in kwargs:
        output.linewidth(kwargs["width_edge"])
    if "color_edge" in kwargs:
        output.linecolor(kwargs["color_edge"])
    if "color_face" in kwargs:
        output.color(c=kwargs["color_face"])

    return output


PLOTS = NewPlotFunctionsTemplate()
PLOTS[plot_e.ELEVATION][1] = _ElevationSurface
PLOTS[plot_e.ISOSET][1] = _IsoSurface
PLOTS[plot_e.MESH][1] = _Mesh
SetDefaultPlotFunction(PLOTS, _DefaultFunction)


TRANSLATIONS = {
    _IsoSurface: {
        "color_edge": None,
        "color_face": None,
        "step_size": None,
        "width_edge": None,
    },
    _Mesh: {
        "color_face": (
            "color_face",
            lambda _: NewTranslatedColor(_, "hex", index_or_reduction=0)[0],
        )
    },
}


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
