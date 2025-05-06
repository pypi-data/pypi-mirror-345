"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h
from enum import Enum as enum_t
from enum import unique

from babelplot.extension.enum_ import EnumValues


@unique
class dim_e(enum_t):
    """
    Data Dimension (corresponding frame/plotting dimensions) are given by the int of the
    member values.

    C=Channel, T=Time.
    C* corresponds to a channel-less frame of type * with a channel slider.
    T and TY are equivalent to X and XY, respectively.
    T* (other than T and TY) corresponds to a time-less frame of type * with a time
    slider.

    Note: The first element of member values could be an increasing integer, to ensure
    uniqueness. However, it is less error-prone to keep something name-related.
    """

    X = ("x", 1)
    XY = ("xy", 2)
    XYZ = ("xyz", 3)
    #
    CX = ("cx", 1)
    CXY = ("cxy", 2)
    CXYZ = ("cxyz", 3)
    #
    T = ("t", 1)
    TY = ("ty", 2)
    TXY = ("txy", 2)
    TXYZ = ("txyz", 3)
    #
    CT = ("ct", 1)
    CTY = ("cty", 2)
    CTXY = ("ctxy", 2)
    CTXYZ = ("ctxyz", 3)

    @classmethod
    def NewFromName(cls, axes: str, /) -> h.Self:
        """"""
        output = getattr(cls, axes.upper(), None)

        if output is None:
            raise ValueError(f"Unknown frame {axes}. Expected={EnumValues(dim_e)}.")

        return output


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
