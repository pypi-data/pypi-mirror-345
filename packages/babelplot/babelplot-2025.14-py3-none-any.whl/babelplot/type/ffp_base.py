"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

"""
ffp: figure, frame, plot.
"""

import dataclasses as d
import typing as h

from babelplot.runtime.backends import BACKENDS
from logger_36 import L

backend_figure_h = h.TypeVar("backend_figure_h")
backend_frame_h = h.TypeVar("backend_frame_h")
backend_plot_h = h.TypeVar("backend_plot_h")
backend_element_h = backend_figure_h | backend_frame_h | backend_plot_h


@d.dataclass(slots=True, repr=False, eq=False)
class base_t:
    """
    raw: Certain plots of certain libraries might be composed of a list of plots,
        not just a unique plot, or even richer outputs (e.g., with Matplotlib).
    property: In case the backend does not make it easy to retrieve some properties,
        they are stored here. E.g., how to retrieve the marker of a scatter plot in
        Matplotlib?
        /!\\ Do not forget to initialize it with kwargs during element instantiation.
    """

    backend_name: str | None = None
    raw: backend_element_h | None = None
    property: dict[str, h.Any] = d.field(default_factory=dict)

    def SetProperty(self, *args, **kwargs) -> None:
        """"""
        args, kwargs = BACKENDS.TranslatedArguments(
            self.backend_name, args, kwargs, self.SetProperty.__name__
        )

        if (n_properties := args.__len__()) > 0:
            if (n_properties % 2) > 0:
                L.error(
                    f"Properties not passed in matching key-value pairs: "
                    f"n. argument(s)={n_properties}; Expected=Even number."
                )
                return

            for name, value in zip(args[:-1:2], args[1::2]):
                self._SetProperty(name, value)

        for name, value in kwargs.items():
            self._SetProperty(name, value)

    def _SetProperty(self, name: str, value: h.Any, /) -> None:
        """"""
        self.property[name] = value
        self._BackendSetProperty(name, value)

    def Property(self, *args) -> h.Any | tuple[h.Any]:
        """"""
        output = []

        args, _ = BACKENDS.TranslatedArguments(
            self.backend_name, args, {}, self.Property.__name__
        )

        for name in args:
            if name in self.property:
                output.append(self.property[name])
            else:
                output.append(self._BackendProperty(name))

        if output.__len__() > 1:
            return output

        return output[0]

    def _BackendSetProperty(self, name: str, value: h.Any, /) -> None:
        """"""
        L.warning(f"Setting property not implemented: {name}={type(value).__name__}")

    def _BackendProperty(self, name: str, /) -> h.Any:
        """"""
        L.warning(f"Getting property not implemented: {name}")


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
