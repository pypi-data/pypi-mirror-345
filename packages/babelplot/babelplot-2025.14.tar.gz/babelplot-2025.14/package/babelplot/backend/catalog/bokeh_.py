"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import gzip
import typing as h
from multiprocessing import Process as process_t

import numpy as nmpy
from babelplot.task.plotting import NewPlotFunctionsTemplate, SetDefaultPlotFunction
from babelplot.task.showing import ShowHTMLPlotWithPyQt
from babelplot.type.dimension import dim_e
from babelplot.type.figure import figure_t as base_figure_t
from babelplot.type.frame import frame_t as base_frame_t
from babelplot.type.plot import plot_t as base_plot_t
from babelplot.type.plot_function import plot_function_h
from babelplot.type.plot_type import plot_e, plot_type_h
from bokeh.embed import file_html as HTMLofBackendContent  # noqa
from bokeh.layouts import column as NewBackendColLayout  # noqa
from bokeh.layouts import grid as NewBackendGridLayout  # noqa
from bokeh.layouts import row as NewBackendRowLayout  # noqa
from bokeh.models.renderers import GlyphRenderer as backend_plot_t  # noqa
from bokeh.plotting import figure as backend_frame_t  # noqa
from bokeh.resources import INLINE  # noqa

NAME = "bokeh"

array_t = nmpy.ndarray


class backend_figure_t: ...


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
            raw=plot_function(self.raw, *args, **kwargs),
        )


@d.dataclass(slots=True, repr=False, eq=False)
class figure_t(base_figure_t):

    layout: h.Any = d.field(init=False, default=None)

    def _NewBackendFigure(self, *args, **kwargs) -> None:
        """"""
        return None

    def _NewFrame(
        self,
        row: int,
        col: int,
        *args,
        title: str | None = None,
        dim: dim_e = dim_e.XY,
        **kwargs,
    ) -> frame_t:
        """"""
        return frame_t(
            title=title,
            dim=dim,
            backend_name=self.backend_name,
            raw=backend_frame_t(title=title, **kwargs),
        )

    def AdjustLayout(self) -> None:
        """"""
        # arranged_frames must be composed of list since Bokeh does not support tuples
        # here!
        n_rows, n_cols = self.shape
        arranged_frames: list[list[h.Any]] = [n_cols * [None] for _ in range(n_rows)]
        for frame, (row, col) in zip(self.frames, self.locations):
            raw = frame.raw
            if raw.renderers.__len__() == 0:
                _ = backend_frame_t.text(
                    raw,
                    x=(0,),
                    y=(0,),
                    text=("Empty Frame",),
                    text_font_size="30px",
                    text_color="#FF0000",
                )
            arranged_frames[row][col] = raw

        # Bokeh does not support inserting None as an indicator of empty space. As a
        # workaround, the frames are currently flattened (and None_s are filtered out).
        should_be_filtered = False
        for one_row in arranged_frames:
            if any(_ is None for _ in one_row):
                should_be_filtered = True
                break
        if should_be_filtered:
            arranged_frames = [_ for one_row in arranged_frames for _ in one_row]
            arranged_frames = list(filter(lambda _: _ is not None, arranged_frames))
            arranged_frames = [arranged_frames]
            n_rows = 1
            n_cols = arranged_frames[0].__len__()

        if n_rows > 1:
            if n_cols > 1:
                layout = NewBackendGridLayout(arranged_frames)
            else:
                column = [_row[0] for _row in arranged_frames]
                layout = NewBackendColLayout(column)
        else:
            layout = NewBackendRowLayout(arranged_frames[0])

        self.layout = layout

    def _BackendShow(self, modal: bool, /) -> None:
        """"""
        try:
            html = HTMLofBackendContent(self.layout, INLINE)
            html = gzip.compress(html.encode())
        except ValueError as exception:
            html = f"""
                <!DOCTYPE html>
                <html>
                <body>
                    <h1>Figure cannot be shown</h1>
                    <p>{str(exception)}</p>
                </body>
                </html>
            """

        process = process_t(target=ShowHTMLPlotWithPyQt, args=(html,))
        process.start()

        if modal:
            process.join()
        else:
            self.showing_process = process


def _DefaultFunction(type_: plot_e, frame_dim: int, /) -> plot_function_h:
    """"""

    def Actual(frame: backend_frame_t, *args, **kwargs) -> backend_plot_t:
        #
        return backend_frame_t.text(
            frame,
            x=(0,),
            y=(0,),
            text=(
                plot_t.UnhandledRequestMessage(
                    type_, *args, frame_dim=frame_dim, **kwargs
                ),
            ),
            text_font_size="30px",
            text_align="center",
            text_color="#FF0000",
        )

    return Actual


def _BarH(frame: backend_frame_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        counts = args[0]
        positions = tuple(range(counts.__len__()))
    else:
        positions, counts = args

    return frame.hbar(y=positions, right=counts, **kwargs)


def _BarV(frame: backend_frame_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        counts = args[0]
        positions = tuple(range(counts.__len__()))
    else:
        positions, counts = args

    return frame.vbar(x=positions, top=counts, **kwargs)


def _Image(frame: backend_frame_t, image: array_t, *args, **kwargs) -> backend_plot_t:
    """"""
    if nmpy.issubdtype(image.dtype, nmpy.floating):
        image = nmpy.round(255.0 * (image / image.max())).astype(nmpy.uint8)

    for_bokeh = nmpy.empty(image.shape[:2], dtype=nmpy.uint32)
    view = for_bokeh.view(dtype=nmpy.uint8).reshape(image.shape[:2] + (4,))

    if (image.ndim == 2) or (image.shape[2] != 4):
        if (image.ndim == 2) or (image.shape[2] == 1):
            planes = (image, image, image)
        else:
            planes = (image[..., 0], image[..., 1], image[..., 2])
        for d_idx in range(3):
            view[..., d_idx] = planes[d_idx]
        view[..., 3] = nmpy.full_like(image, 255)
    else:
        view[...] = image[...]

    frame.x_range.range_padding = frame.y_range.range_padding = 0

    return frame.image_rgba(
        image=(for_bokeh,), x=0, y=0, dw=image.shape[1], dh=image.shape[0]
    )


PLOTS = NewPlotFunctionsTemplate()
PLOTS[plot_e.BARH][0] = _BarH
PLOTS[plot_e.BARV][0] = _BarV
PLOTS[plot_e.IMAGE][0] = _Image
PLOTS[plot_e.SCATTER][0] = backend_frame_t.scatter
SetDefaultPlotFunction(PLOTS, _DefaultFunction)


TRANSLATIONS = {
    None: {
        "color_face": "fill_color",
        "opacity": "alpha",
    },
    "_NewFrame": {
        "azimuth": None,
        "elevation": None,
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
