"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d

from babelplot.runtime.backends import BACKENDS
from babelplot.type.dimension import dim_e
from babelplot.type.ffp_base import backend_frame_h, backend_plot_h, base_t
from babelplot.type.plot import plot_t
from babelplot.type.plot_function import plot_function_h
from babelplot.type.plot_type import plot_type_h


@d.dataclass(slots=True, repr=False, eq=False)
class frame_t(base_t):
    title: str | None = None
    dim: dim_e | None = None
    frame_dim: int | None = d.field(init=False, default=None)
    plots: list[plot_t] = d.field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """"""
        self.frame_dim = self.dim.value[1]

    def AddPlot(
        self,
        type_: plot_type_h | plot_function_h,
        *args,
        title: str | None = None,
        **kwargs,
    ) -> plot_t:
        """"""
        full_type = (type_, self.frame_dim)
        plot_function = BACKENDS.PlotFunction(self.backend_name, type_, self.frame_dim)
        args, kwargs = BACKENDS.TranslatedArguments(
            self.backend_name, args, kwargs, plot_function
        )
        plot = self._NewPlot(
            plot_function,
            *args,
            title=title,
            type_=full_type,
            **kwargs,
        )
        plot.type_ = full_type
        # Note: plot.__class__ is not plot_t; It is the subclass defined by a backend.
        DefaultProperties = getattr(plot.__class__, "_BackendDefaultProperties", None)
        if DefaultProperties is not None:
            for name, value in DefaultProperties(type(plot.raw)).items():
                if name not in plot.property:
                    plot.property[name] = value

        self.plots.append(plot)

        return plot

    def _NewPlot(
        self,
        plot_function: plot_function_h,
        *args,
        title: str | None = None,  # /!\ If _, then it is swallowed by kwargs!
        type_: tuple[plot_type_h | plot_function_h, int],
        **kwargs,
    ) -> plot_t:
        """"""
        raise NotImplementedError

    def RemovePlot(self, plot: plot_t, /) -> None:
        """"""
        self.plots.remove(plot)
        self._RemoveBackendPlot(plot.raw, self.raw)

    @staticmethod
    def _RemoveBackendPlot(plot: backend_plot_h, frame: backend_frame_h, /) -> None:
        """"""
        raise NotImplementedError

    def Clear(self) -> None:
        """"""
        # Do not use a for-loop since self.plots will be modified during looping
        while self.plots.__len__() > 0:
            plot = self.plots[0]
            self.RemovePlot(plot)


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
