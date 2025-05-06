"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

import matplotlib.pyplot as pypl  # noqa
import numpy as nmpy
import skimage.measure as msre
from color_spec_changer.translation import NewTranslatedColor
from babelplot.task.plotting import NewPlotFunctionsTemplate
from babelplot.type.dimension import dim_e
from babelplot.type.ffp_base import backend_element_h
from babelplot.type.figure import figure_t as base_figure_t
from babelplot.type.frame import frame_t as base_frame_t
from babelplot.type.plot import plot_t as base_plot_t
from babelplot.type.plot_function import plot_function_h
from babelplot.type.plot_type import plot_e, plot_type_h
from logger_36 import L
from matplotlib.artist import Artist as backend_plot_t  # noqa
from matplotlib.container import Container as backend_plots_t  # noqa
from matplotlib.gridspec import GridSpec as grid_spec_t  # noqa
from matplotlib.markers import MarkerStyle as marker_style_t  # noqa
from matplotlib.patches import Polygon as polygon_t  # noqa
from matplotlib.pyplot import Axes as backend_frame_2d_t  # noqa
from matplotlib.pyplot import Figure as backend_figure_t  # noqa
from matplotlib.pyplot import figure as NewBackendFigure  # noqa
from mpl_toolkits.mplot3d import Axes3D as backend_frame_3d_t  # noqa

import matplotlib as mtpl  # noqa

NAME = "matplotlib"


array_t = nmpy.ndarray
backend_frame_h = backend_frame_2d_t | backend_frame_3d_t


def _DefaultProperties(type_: type[plot_type_h], /) -> dict[str, h.Any]:
    """"""
    name = type_.__name__
    properties = mtpl.rcParams.find_all(f"^{name}\\.")

    return {_key.replace(f"{name}.", ""): _vle for _key, _vle in properties.items()}


def _SetProperty(
    element: backend_element_h | h.Sequence[backend_element_h],
    name: str,
    value: h.Any,
    /,
) -> None:
    """"""
    if isinstance(element, h.Sequence):
        elements = element
        for element in elements:
            _SetProperty(element.raw, name, value)
        return

    if name == "marker":
        new_marker = marker_style_t(value)
        element.raw.set_paths((new_marker.get_path(),))
    else:
        property_ = {name: value}
        try:
            pypl.setp(element.raw, **property_)
        except AttributeError:
            L.error(
                f'Property "{name}": Invalid property for element of type "{type(element).__name__}"'
            )


def _Property(
    element: backend_element_h | h.Sequence[backend_element_h], name: str, /
) -> h.Any:
    """"""
    if isinstance(element, h.Sequence):
        return _Property(element[0].raw, name)

    try:
        output = pypl.getp(element.raw, property=name)
    except AttributeError:
        output = None
        L.error(
            f'Property "{name}": Invalid property for element of type "{type(element).__name__}"'
        )

    return output


@d.dataclass(slots=True, repr=False, eq=False)
class plot_t(base_plot_t):
    _BackendDefaultProperties: h.ClassVar[h.Callable] = _DefaultProperties
    _BackendSetProperty: h.ClassVar[h.Callable] = _SetProperty
    _BackendProperty: h.ClassVar[h.Callable] = _Property


@d.dataclass(slots=True, repr=False, eq=False)
class frame_t(base_frame_t):
    _BackendSetProperty: h.ClassVar[h.Callable] = _SetProperty
    _BackendProperty: h.ClassVar[h.Callable] = _Property

    def _NewPlot(
        self,
        plot_function: plot_function_h,
        *args,
        title: str | None = None,  # /!\ If _, then it is swallowed by kwargs!
        type_: tuple[plot_type_h | plot_function_h, int],
        **kwargs,
    ) -> plot_t:
        """"""
        return plot_t(
            title=title,
            property=kwargs.copy(),
            backend_name=self.backend_name,
            raw=plot_function(self.raw, *args, **kwargs),
        )


@d.dataclass(slots=True, repr=False, eq=False)
class figure_t(base_figure_t):
    _BackendSetProperty: h.ClassVar[h.Callable] = _SetProperty
    _BackendProperty: h.ClassVar[h.Callable] = _Property

    def _NewBackendFigure(self, *args, **kwargs) -> backend_figure_t:
        """"""
        return NewBackendFigure(*args, num=None, **kwargs)

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
        output = frame_t(
            title=title,
            dim=dim,
            backend_name=self.backend_name,
        )

        if dim is dim_e.XY:
            raw = self.raw.subplots(*args, **kwargs)
        elif dim is dim_e.XYZ:
            # See note below
            raw = backend_frame_3d_t(
                self.raw, *args, auto_add_to_figure=False, **kwargs
            )
            self.raw.add_axes(raw)
        else:
            raise NotImplementedError(f"Frame dimension {dim} not implemented.")
        if title is not None:
            raw.set_title(title)

        output.raw = raw

        return output

    def AdjustLayout(self) -> None:
        """"""
        figure_raw = self.raw

        if self.title is not None:
            figure_raw.suptitle(self.title)
        for frame in self.frames:
            if frame.title is not None:
                frame.raw.set_title(frame.title)
            for plot in frame.plots:
                if plot.title is not None:
                    plot_raw = plot.raw
                    if isinstance(plot_raw, h.Sequence):
                        plot_raw_s = plot_raw
                    else:
                        plot_raw_s = (plot_raw,)
                    for plot_raw in plot_raw_s:
                        if (
                            SetLabel := getattr(plot_raw, "set_label", None)
                        ) is not None:
                            SetLabel(plot.title)

        if self.frames.__len__() < 2:
            return

        grid_spec = grid_spec_t(*self.shape, figure=figure_raw)
        bottoms, tops, lefts, rights = grid_spec.get_grid_positions(figure_raw)

        for frame, (row, col) in zip(self.frames, self.locations):
            left, bottom, width, height = (
                lefts[col],
                bottoms[row],
                rights[col] - lefts[col],
                tops[row] - bottoms[row],
            )
            frame.raw.set_position((left, bottom, width, height))

    def _BackendShow(self, modal: bool, /) -> None:
        """"""
        self.raw.show()

        if modal:
            if "qt" in mtpl.get_backend().lower():
                from matplotlib.backends.qt_compat import QtWidgets  # noqa

                application = QtWidgets.QApplication.instance()
                application.exec()
            else:
                event_manager = self.raw.canvas
                event_manager.mpl_connect("close_event", _OnCloseEvent)
                event_manager.start_event_loop()


def _OnCloseEvent(event: h.Any, /) -> None:
    """"""
    event.canvas.stop_event_loop()

    figures = tuple(map(pypl.figure, pypl.get_fignums()))
    if figures.__len__() > 0:
        event_manager = figures[0].canvas
        event_manager.mpl_connect("close_event", _OnCloseEvent)
        event_manager.start_event_loop()


def _Arrows2(frame: backend_frame_2d_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 2:
        u, v = args
        x, y = u.shape
    else:
        x, y, u, v = args

    if isinstance(x, int):
        x, y = nmpy.meshgrid(range(x), range(y), indexing="ij")

    u = nmpy.asarray(u)
    v = nmpy.asarray(v)
    if u.ndim == 1:
        x = x.ravel()
        y = y.ravel()

    return frame.quiver(x, y, u, v, **kwargs)


def _Arrows3(frame: backend_frame_3d_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 3:
        u, v, w = args
        x, y, z = u.shape
    else:
        x, y, z, u, v, w = args

    if isinstance(x, int):
        x, y, z = nmpy.meshgrid(range(x), range(y), range(z), indexing="ij")

    u = nmpy.asarray(u)
    v = nmpy.asarray(v)
    w = nmpy.asarray(w)
    if u.ndim == 1:
        x = x.ravel()
        y = y.ravel()
        z = z.ravel()

    if ((color := kwargs.get("color")) is not None) and isinstance(color, nmpy.ndarray):
        kwargs = kwargs.copy()
        kwargs["color"] = nmpy.vstack((color, nmpy.repeat(color, 2, axis=0)))

    return frame.quiver(x, y, z, u, v, w, **kwargs)


def _Bar3(frame: backend_frame_3d_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        counts = nmpy.asarray(args[0])
        x, y = counts.shape
    else:
        x, y, counts = args
        counts = nmpy.asarray(counts)
    if isinstance(x, int):
        x, y = nmpy.meshgrid(range(x), range(y), indexing="ij")
    if counts.ndim == 1:
        x = x.ravel()
        y = y.ravel()

    width = kwargs.get("width", 0.8)
    depth = kwargs.get("depth", 0.8)
    offset = kwargs.get("offset", 0.0)
    kwargs = {
        _key: _vle
        for _key, _vle in kwargs.items()
        if _key not in ("width", "depth", "offset")
    }

    return frame.bar3d(x, y, offset, width, depth, counts, **kwargs)


def _BarH(frame: backend_frame_2d_t, *args, **kwargs) -> backend_plots_t:
    """"""
    if args.__len__() == 1:
        counts = args[0]
        positions = range(counts.__len__())
    else:
        positions, counts = args

    return frame.barh(positions, counts, **kwargs)


def _BarV(frame: backend_frame_2d_t, *args, **kwargs) -> backend_plots_t:
    """"""
    if args.__len__() == 1:
        counts = args[0]
        positions = range(counts.__len__())
    else:
        positions, counts = args

    return frame.bar(positions, counts, **kwargs)


def _ElevationSurface(frame: backend_frame_3d_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        elevation = args[0]
        x, y = nmpy.meshgrid(
            range(elevation.shape[0]), range(elevation.shape[1]), indexing="ij"
        )
    else:
        x, y, elevation = args

    return frame.plot_surface(x, y, elevation, **kwargs)


def _IsoContour(frame: backend_frame_2d_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 2:
        values, value = args
        output = frame.contour(values, (value,), **kwargs)
    else:
        x, y, values, value = args
        output = frame.contour(x, y, values, (value,), **kwargs)
    if not frame.yaxis_inverted():
        frame.invert_yaxis()
        frame.xaxis.tick_top()

    return output


def _IsoSurface(frame: backend_frame_3d_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if "step_size" in kwargs:
        mc_kwargs = {"step_size": kwargs["step_size"]}
        kwargs = kwargs.copy()
        del kwargs["step_size"]
    else:
        mc_kwargs = {}

    vertices, triangles, *_ = msre.marching_cubes(*args, **mc_kwargs)

    return _Mesh(frame, triangles, vertices, **kwargs)


def _Mesh(
    frame: backend_frame_3d_t, triangles: array_t, vertices: array_t, *_, **kwargs
) -> backend_plot_t:
    """
    Note: As of 3.9.2, plot_trisurf does not support custom triangle colors yet (see
    https://github.com/matplotlib/matplotlib/blob/v3.9.2/lib/mpl_toolkits/mplot3d/axes3d.py,
    line 2291).
    """
    return frame.plot_trisurf(
        vertices[:, 0], vertices[:, 1], triangles, vertices[:, 2], **kwargs
    )


def _Polygon(
    frame: backend_frame_2d_t, xs: array_t, ys: array_t, *_, **kwargs
) -> polygon_t:
    """"""
    output = polygon_t(nmpy.vstack((xs, ys)).T, **kwargs)
    frame.add_patch(output)

    return output


def _Text2(frame: backend_frame_2d_t, text, x, y, *_, **kwargs) -> backend_plot_t:
    """"""
    return frame.text(x, y, text, **kwargs)


def _Text3(frame: backend_frame_2d_t, text, x, y, z, *_, **kwargs) -> backend_plot_t:
    """"""
    return frame.text(x, y, z, text, **kwargs)


PLOTS = NewPlotFunctionsTemplate()

PLOTS[plot_e.ARROWS][0] = _Arrows2
PLOTS[plot_e.ARROWS][1] = _Arrows3
PLOTS[plot_e.BAR3][1] = _Bar3
PLOTS[plot_e.BARH][0] = _BarH
PLOTS[plot_e.BARV][0] = _BarV
PLOTS[plot_e.ELEVATION][1] = _ElevationSurface
PLOTS[plot_e.IMAGE][0] = backend_frame_2d_t.matshow
PLOTS[plot_e.ISOSET][0] = _IsoContour
PLOTS[plot_e.ISOSET][1] = _IsoSurface
PLOTS[plot_e.MESH][1] = _Mesh
PLOTS[plot_e.PIE][0] = backend_frame_2d_t.pie
PLOTS[plot_e.POLYGON][0] = _Polygon
PLOTS[plot_e.POLYLINE][0] = backend_frame_2d_t.plot
PLOTS[plot_e.POLYLINE][1] = backend_frame_3d_t.plot
PLOTS[plot_e.SCATTER][0] = backend_frame_2d_t.scatter
PLOTS[plot_e.SCATTER][1] = backend_frame_3d_t.scatter
PLOTS[plot_e.TEXT][0] = _Text2
PLOTS[plot_e.TEXT][1] = _Text3


TRANSLATIONS = {
    None: {
        "color": "c",
        "color_edge": "edgecolors",
        "color_face": "facecolors",
        "color_max": "vmax",
        "color_min": "vmin",
        "color_scaling": "norm",
        "colormap": "cmap",
        "depth_shade": "depthshade",
        "opacity": "alpha",
        "plot_non_finite": "plotnonfinite",
        "size": "s",
        "width_edge": "linewidths",
    },
    "_NewFrame": {
        "azimuth": "azim",
        "elevation": "elev",
    },
    _Arrows2: {"c": "color"},
    _Arrows3: {"c": "color"},
    _Bar3: {"c": "color"},
    _BarH: {
        "c": "color",
        "offset": "left",
    },
    _BarV: {
        "c": "color",
        "offset": "bottom",
    },
    _ElevationSurface: {"facecolors": "color"},
    _IsoContour: {"c": "colors"},
    _IsoSurface: {"facecolors": "color"},
    _Mesh: {
        "facecolors": (
            "color",
            lambda _: NewTranslatedColor(_, "hex", index_or_reduction=0)[0],
        )
    },
    _Polygon: {
        "edgecolors": "edgecolor",
        "facecolors": "facecolor",
    },
    backend_frame_2d_t.pie: {"c": "colors"},
    backend_frame_2d_t.quiver: {"c": "color"},
    backend_frame_3d_t.quiver: {"c": "colors"},
    backend_frame_3d_t.scatter: {2: "zs"},
}

"""
From: https://matplotlib.org/stable/api/prev_api_changes/api_changes_3.4.0.html
*Axes3D automatically adding itself to Figure is deprecated*

New Axes3D objects previously added themselves to figures when they were created,
unlike all other Axes classes, which lead to them being added twice if
fig.add_subplot(111, projection='3d') was called.

This behavior is now deprecated and will warn. The new keyword argument
auto_add_to_figure controls the behavior and can be used to suppress the warning. The
default value will change to False in Matplotlib 3.5, and any non-False value will be
an error in Matplotlib 3.6.

In the future, Axes3D will need to be explicitly added to the figure

fig = Figure()
ax = Axes3d(fig)
fig.add_axes(ax)

as needs to be done for other axes.Axes subclasses. Or, a 3D projection can be made
via:

fig.add_subplot(projection='3d')
"""

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
