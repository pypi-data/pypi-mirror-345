"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import gzip
import typing as h
from multiprocessing import Process as process_t
from pathlib import Path as path_t

import numpy as nmpy
import plotly.figure_factory as fcry  # noqa
import plotly.graph_objects as plly  # noqa
from color_spec_changer.analysis import NColorsAndFormat
from color_spec_changer.translation import NewTranslatedColor
from babelplot.task.plotting import NewPlotFunctionsTemplate
from babelplot.task.showing import ShowHTMLPlotWithPyQt
from babelplot.type.dimension import dim_e
from babelplot.type.figure import figure_t as base_figure_t
from babelplot.type.frame import frame_t as base_frame_t
from babelplot.type.plot import plot_t as base_plot_t
from babelplot.type.plot_function import plot_function_h
from babelplot.type.plot_type import plot_e, plot_type_h
from plotly.basedatatypes import BaseTraceType as backend_plot_t  # noqa
from plotly.graph_objects import Figure as backend_figure_t  # noqa
from plotly.subplots import make_subplots as NewMultiAxesFigure  # noqa

NAME = "plotly"


array_t = nmpy.ndarray


_FIGURE_CONFIG = {
    "toImageButtonOptions": {  # TODO: No PNG export produced actually.
        "filename": str(path_t.home() / "plotly_figure"),
        "height": None,
        "width": None,
    },
    "modeBarButtonsToAdd": ("drawclosedpath",),
}


@d.dataclass(slots=True, repr=False, eq=False)
class plot_t(base_plot_t): ...


@d.dataclass(slots=True, repr=False, eq=False)
class frame_t(base_frame_t):

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

    def _NewBackendFigure(self, *args, **kwargs) -> backend_figure_t:
        """"""
        return backend_figure_t(*args, **kwargs)

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

    def AdjustLayout(self) -> None:
        """"""
        title_postfix = ""

        n_rows, n_cols = self.shape
        if (n_rows > 1) or (n_cols > 1):
            frame_titles = (n_rows * n_cols) * [""]
            arranged_plots: list[list[list[backend_plot_t] | None]] = [
                n_cols * [None] for _ in range(n_rows)
            ]
            for frame, (row, col) in zip(self.frames, self.locations):
                if frame.title is not None:
                    frame_titles[row * n_cols + col] = frame.title
                for plot in frame.plots:
                    if plot.title is not None:
                        plot.raw.update(name=plot.title)
                arranged_plots[row][col] = [_.raw for _ in frame.plots]

            frame_types = [n_cols * [{}] for _ in range(n_rows)]
            for row, plot_row in enumerate(arranged_plots):
                for col, plot_cell in enumerate(plot_row):
                    # Note: Subclasses of backend_plot_t have a type property.
                    frame_types[row][col] = {"type": plot_cell[0].type}

            raw = NewMultiAxesFigure(
                rows=n_rows, cols=n_cols, specs=frame_types, subplot_titles=frame_titles
            )
            for row, plot_row in enumerate(arranged_plots, start=1):
                for col, plot_cell in enumerate(plot_row, start=1):
                    for plot in plot_cell:
                        raw.add_trace(plot, row=row, col=col)
            self.raw = raw
        else:
            raw = self.raw

            frame = self.frames[0]
            if frame.title is not None:
                title_postfix = f" - {frame.title}"

            for plot in frame.plots:
                raw_plot = plot.raw
                raw.add_trace(raw_plot)
                if plot.title is not None:
                    raw_plot.update(name=plot.title)

        if self.title is not None:
            raw.update_layout(title_text=self.title + title_postfix)

    def _BackendShow(self, modal: bool, /) -> None:
        """
        Note on include_plotlyjs:
            - "cdn": works but must be online.
            - True => blank figure if using
              PySide6.QtWebEngineWidgets.QWebEngineView.setHtml because of html size
              limit.
              See note in babelplot.task.html.Show.
        """
        html = self.raw.to_html(include_plotlyjs=True, config=_FIGURE_CONFIG)
        html = gzip.compress(html.encode())

        process = process_t(target=ShowHTMLPlotWithPyQt, args=(html,))
        process.start()

        if modal:
            process.join()
        else:
            self.showing_process = process


def _Arrows2(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 2:
        u, v = args
        x, y = u.shape
    else:
        x, y, u, v = args

    if isinstance(x, int):
        x, y = nmpy.meshgrid(range(x), range(y), indexing="ij")

    return fcry.create_quiver(
        x.ravel(), y.ravel(), u.ravel(), v.ravel(), **kwargs
    ).data[0]


def _Arrows3(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 3:
        u, v, w = args
        x, y, z = u.shape
    else:
        x, y, z, u, v, w = args

    if isinstance(x, int):
        x, y, z = nmpy.meshgrid(range(x), range(y), range(z), indexing="ij")

    return plly.Cone(
        x=x.ravel(),
        y=y.ravel(),
        z=z.ravel(),
        u=u.ravel(),
        v=v.ravel(),
        w=w.ravel(),
        **kwargs,
    )


def _Bar3(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        counts = nmpy.asarray(args[0])
        x, y = counts.shape
    else:
        x, y, counts = args
        counts = nmpy.asarray(counts)

    if counts.ndim == 2:
        counts = counts.ravel()

    if isinstance(x, int):
        x, y = nmpy.meshgrid(range(x), range(y), indexing="ij")
    if x.ndim == 2:
        x = x.ravel()
        y = y.ravel()

    x = x.astype(nmpy.float64)
    y = y.astype(nmpy.float64)

    differences = nmpy.diff(x)
    thickness_x = min(differences[differences > 0.0])
    differences = nmpy.diff(y)
    thickness_y = min(differences[differences > 0.0])
    thickness_x *= 0.4
    thickness_y *= 0.4

    vertices_x = []
    vertices_y = []
    vertices_z = []
    for x_, y_, count in zip(x, y, counts):
        x_min, y_min = x_ - thickness_x, y_ - thickness_y
        x_max, y_max = x_ + thickness_x, y_ + thickness_y

        vertices_x.extend((x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max))
        vertices_y.extend((y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min))
        vertices_z.extend((0, 0, 0, 0, count, count, count, count))

    bottom = (
        nmpy.array((0, 0), dtype=nmpy.int64),
        nmpy.array((1, 2), dtype=nmpy.int64),
        nmpy.array((2, 3), dtype=nmpy.int64),
    )
    top = tuple(_ + 4 for _ in bottom)
    left = (
        nmpy.array((0, 1), dtype=nmpy.int64),
        nmpy.array((1, 5), dtype=nmpy.int64),
        nmpy.array((4, 4), dtype=nmpy.int64),
    )
    right = (
        nmpy.array((3, 2), dtype=nmpy.int64),
        nmpy.array((2, 6), dtype=nmpy.int64),
        nmpy.array((7, 7), dtype=nmpy.int64),
    )
    front = (
        nmpy.array((0, 0), dtype=nmpy.int64),
        nmpy.array((3, 7), dtype=nmpy.int64),
        nmpy.array((7, 4), dtype=nmpy.int64),
    )
    back = (
        nmpy.array((1, 1), dtype=nmpy.int64),
        nmpy.array((2, 6), dtype=nmpy.int64),
        nmpy.array((6, 5), dtype=nmpy.int64),
    )
    triangles_i = []
    triangles_j = []
    triangles_k = []
    v_idx = 0
    for _ in range(counts.size):
        for face in (bottom, top, left, right, front, back):
            triangles_i.extend(face[0] + v_idx)
            triangles_j.extend(face[1] + v_idx)
            triangles_k.extend(face[2] + v_idx)
        v_idx += 8

    if "color" in kwargs:
        colors = kwargs["color"]
        del kwargs["color"]
    else:
        colors = nmpy.random.random(size=(counts.size, 3))
    colors = colors[
        tuple(
            (nmpy.fromiter(range(12 * counts.size), nmpy.float64) / 12.0).astype(
                nmpy.int64
            )
        ),
        :,
    ]

    return plly.Mesh3d(
        x=vertices_x,
        y=vertices_y,
        z=vertices_z,
        i=triangles_i,
        j=triangles_j,
        k=triangles_k,
        facecolor=colors,
        **kwargs,
    )


def _BarH(*args, **kwargs) -> backend_plot_t:
    """"""
    return _BarV(*args, orientation="h", **kwargs)


def _BarV(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        counts = args[0]
        positions = tuple(range(counts.__len__()))
    else:
        positions, counts = args
    if kwargs.get("orientation") == "h":
        positions, counts = counts, positions

    return plly.Bar(x=positions, y=counts, **kwargs)


def _ElevationSurface(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        elevation = args[0]
        x, y = nmpy.meshgrid(
            range(elevation.shape[0]), range(elevation.shape[1]), indexing="ij"
        )
    else:
        x, y, elevation = args

    return plly.Surface(contours={}, x=x, y=y, z=elevation, **kwargs)


def _Image(image: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    if image.ndim == 2:
        return plly.Heatmap(z=image, **kwargs)

    return plly.Image(z=image, **kwargs)


def _IsoContour(*args, **kwargs) -> backend_plot_t:
    """"""
    parameters: dict[str, h.Any] = {
        "contours_coloring": "lines",
        "line_width": 2,
    }

    if args.__len__() == 2:
        values, value = args
    else:
        x, y, values, value = args
        parameters["x"] = x
        parameters["y"] = y
    parameters["z"] = values
    parameters["contours"] = {
        "start": value,
        "end": value,
        "size": 1,
        "showlabels": True,
    }

    parameters.update(kwargs)

    return plly.Contour(**parameters)


def _IsoSurface(values: array_t, value: float, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 3:
        x, y, z = args
    else:
        x, y, z = nmpy.meshgrid(
            range(values.shape[0]),
            range(values.shape[1]),
            range(values.shape[2]),
            indexing="ij",
        )

    parameters = {
        "surface": {"count": 1},
        "caps": {"x_show": False, "y_show": False, "z_show": False},
    }
    parameters.update(kwargs)

    return plly.Isosurface(
        x=x.ravel(),
        y=y.ravel(),
        z=z.ravel(),
        value=values.ravel(),
        isomin=value,
        isomax=value,
        **parameters,
    )


def _Mesh(triangles: array_t, vertices: array_t, *_, **kwargs) -> backend_plot_t:
    """
    Note: Mesh3d does not support setting edge colors. It can be done indirectly by
    adding a Scatter3d plot.
    """
    return plly.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=triangles[:, 0],
        j=triangles[:, 1],
        k=triangles[:, 2],
        **kwargs,
    )


def _Pie(values: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Pie(values=values, **kwargs)


def _Polygon(x: array_t, y: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    x = nmpy.concatenate((x, [x[0]]))
    y = nmpy.concatenate((y, [y[0]]))

    return plly.Scatter(x=x, y=y, mode="lines", fill="toself", **kwargs)


def _Polyline2(x: array_t, y: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter(x=x, y=y, mode="lines", **kwargs)


def _Polyline3(x: array_t, y: array_t, z: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter3d(x=x, y=y, z=z, mode="lines", **kwargs)


def _Scatter2(x: array_t, y: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter(x=x, y=y, mode="markers", **kwargs)


def _Scatter3(x: array_t, y: array_t, z: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter3d(x=x, y=y, z=z, mode="markers", **kwargs)


def _Text2(text: str, x: float, y: float, *_, **kwargs) -> backend_plot_t:
    """"""
    parameters = {"textposition": "top right"}
    parameters.update(kwargs)

    return plly.Scatter(x=[x], y=[y], text=[text], mode="text", **parameters)


def _Text3(text: str, x: float, y: float, z: float, *_, **kwargs) -> backend_plot_t:
    """"""
    parameters = {"textposition": "top right"}
    parameters.update(kwargs)

    return plly.Scatter3d(
        x=[x],
        y=[y],
        z=[z],
        text=[text],
        mode="text",
        **parameters,
    )


PLOTS = NewPlotFunctionsTemplate()

PLOTS[plot_e.ARROWS][0] = _Arrows2
PLOTS[plot_e.ARROWS][1] = _Arrows3
PLOTS[plot_e.BAR3][1] = _Bar3
PLOTS[plot_e.BARH][0] = _BarH
PLOTS[plot_e.BARV][0] = _BarV
PLOTS[plot_e.ELEVATION][1] = _ElevationSurface
PLOTS[plot_e.IMAGE][0] = _Image
PLOTS[plot_e.ISOSET][0] = _IsoContour
PLOTS[plot_e.ISOSET][1] = _IsoSurface
PLOTS[plot_e.MESH][1] = _Mesh
PLOTS[plot_e.PIE][0] = _Pie
PLOTS[plot_e.POLYGON][0] = _Polygon
PLOTS[plot_e.POLYLINE][0] = _Polyline2
PLOTS[plot_e.POLYLINE][1] = _Polyline3
PLOTS[plot_e.SCATTER][0] = _Scatter2
PLOTS[plot_e.SCATTER][1] = _Scatter3
PLOTS[plot_e.TEXT][0] = _Text2
PLOTS[plot_e.TEXT][1] = _Text3


def _ApplyGlobalTranslation(
    kwargs: dict[str, h.Any], who_s_asking: str | h.Callable | None, /
) -> None:
    """"""
    if who_s_asking in (_Scatter2, _Scatter3):
        marker = {}
        for passed, wanted in zip(
            ("color", "opacity", "size", "shape"),
            ("color", "opacity", "size", "symbol"),
        ):
            if (value := kwargs.get(passed)) is not None:
                marker[wanted] = value
                del kwargs[passed]
        if "color" in marker:
            format_ = NColorsAndFormat(marker["color"])
            n_colors = format_.n_colors
            if n_colors > 1:
                translated, _ = NewTranslatedColor(marker["color"], "function_rgb255")
                colorscale = [
                    [_idx / (n_colors - 1), _clr]
                    for _idx, _clr in enumerate(translated)
                ]
                marker["colorscale"] = colorscale
                marker["color"] = tuple(_[0] for _ in colorscale)
        if who_s_asking is _Scatter3:
            # /!\\ Passing one size per sample makes all of them disappear.
            if ("size" in marker) and not isinstance(marker["size"], int | float):
                marker["size"] = 0.5 * (min(marker["size"]) + max(marker["size"]))
            # /!\\ Opacity seems to be all-or-nothing.
            if "opacity" in marker:
                del marker["opacity"]

        kwargs["marker"] = marker
        #
    elif who_s_asking in (_Arrows2, _Polygon, _Polyline2, _Polyline3):
        line = {}
        for passed, wanted in zip(
            ("color", "color_edge", "opacity", "line_width", "line_style"),
            ("color", "color", "opacity", "width", "symbol"),
        ):
            if (value := kwargs.get(passed)) is not None:
                line[wanted] = value
                del kwargs[passed]

        kwargs["line"] = line
        #
    elif who_s_asking is _Pie:
        marker = {}
        for passed, wanted in zip(("color",), ("colors",)):
            if (value := kwargs.get(passed)) is not None:
                marker[wanted] = value
                del kwargs[passed]

        kwargs["marker"] = marker


TRANSLATIONS = {
    None: {
        "color_face": "surfacecolor",
        None: _ApplyGlobalTranslation,
    },
    _Arrows3: {"color": None},
    _BarH: {"color": None},
    _BarV: {"color": None},
    _ElevationSurface: {"color_edge": None, "surfacecolor": None, "width_edge": None},
    _Image: {"colormap": None},
    _IsoContour: {"color": "fillcolor"},
    _IsoSurface: {
        "color_edge": None,
        "surfacecolor": None,
        "step_size": None,
        "width_edge": None,
    },
    _Mesh: {"color_edge": None, "surfacecolor": "facecolor", "width_edge": None},
    _Polygon: {"surfacecolor": "fillcolor"},
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
