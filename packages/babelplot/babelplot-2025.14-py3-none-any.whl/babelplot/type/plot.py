"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d

from babelplot.type.ffp_base import base_t
from babelplot.type.plot_function import plot_function_h
from babelplot.type.plot_type import plot_type_h


@d.dataclass(slots=True, repr=False, eq=False)
class plot_t(base_t):
    title: str | None = None
    type_: tuple[plot_type_h | plot_function_h, int] | None = None

    @staticmethod
    def UnhandledRequestMessage(
        type_: plot_type_h | plot_function_h, *args, frame_dim: int = 0, **kwargs
    ) -> str:
        """"""
        if frame_dim > 0:
            if isinstance(type_, str):
                name = type_
            else:
                name = type_.name
            request = f"{name}.{frame_dim}"
        else:
            request = str(type_)

        args = ", ".join(map(lambda _: type(_).__name__, args))
        kwargs = ", ".join(
            f"{_key}={type(_vle).__name__}" for _key, _vle in kwargs.items()
        )

        return f"Unhandled Plot Request\n{request}\nargs: {args}\nkwargs: {kwargs}"


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
