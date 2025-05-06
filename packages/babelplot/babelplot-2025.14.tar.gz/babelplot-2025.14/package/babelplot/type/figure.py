"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h
from multiprocessing import Process as process_t

from babelplot.runtime.backends import BACKENDS
from babelplot.type.dimension import dim_e
from babelplot.type.ffp_base import backend_figure_h, backend_frame_h, base_t
from babelplot.type.frame import frame_t
from logger_36 import L


def _DefaultShape() -> list[int]:
    """
    Meant to be a mutable tuple[int, int].
    """
    return [0, 0]


@d.dataclass(slots=True, repr=False, eq=False)
class figure_t(base_t):
    title: str | None = None
    offline_version: bool = False
    frames: list[frame_t] = d.field(init=False, default_factory=list)
    locations: list[tuple[int, int]] = d.field(init=False, default_factory=list)
    shape: list[int] = d.field(init=False, default_factory=_DefaultShape)
    showing_process: process_t | None = d.field(init=False, default=None)

    @classmethod
    def New(
        cls,
        backend_name: str,
        /,
        *args,
        title: str | None = None,
        offline_version: bool = False,
        **kwargs,
    ) -> h.Self:
        """"""
        output = cls(
            title=title,
            offline_version=offline_version,
            backend_name=backend_name,
        )

        args, kwargs = BACKENDS.TranslatedArguments(
            backend_name, args, kwargs, output._NewBackendFigure.__name__
        )
        raw = output._NewBackendFigure(*args, **kwargs)

        output.raw = raw

        return output

    def _NewBackendFigure(self, *args, **kwargs) -> backend_figure_h | None:
        """"""
        raise NotImplementedError

    def AddFrame(
        self,
        *args,
        title: str | None = None,
        dim: str | dim_e = dim_e.XY,
        row: int = 0,
        col: int = 0,
        **kwargs,
    ) -> frame_t | None:
        """"""
        if (where := (row, col)) in self.locations:
            L.error(f"{where}: Frame grid cell already filled")
            return None
        if (row < 0) and (col < 0):
            L.error(f"{where}: Grid coordinates cannot be both negative")
            return None

        if isinstance(dim, str):
            dim = dim_e.NewFromName(dim)
        if row < 0:
            row = self.shape[0]
        elif col < 0:
            col = self.shape[1]

        args, kwargs = BACKENDS.TranslatedArguments(
            self.backend_name, args, kwargs, self._NewFrame.__name__
        )
        output = self._NewFrame(title, dim, row, col, *args, **kwargs)

        self.frames.append(output)
        self.locations.append((row, col))
        self.shape[0] = max(self.shape[0], row + 1)
        self.shape[1] = max(self.shape[1], col + 1)

        return output

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
        raise NotImplementedError

    def AdjustLayout(self) -> None: ...

    def FrameAtLocation(
        self,
        row: int,
        col: int,
        *,
        as_backend: bool = False,
    ) -> frame_t | None:
        """"""
        if (row < 0) or (col < 0) or (row >= self.shape[0]) or (col >= self.shape[1]):
            L.error(
                f"Out-of-bound cell coordinates ({row},{col}). "
                f"Expected: 0≤row<{self.shape[0]} and 0≤col<{self.shape[1]}"
            )
            return None

        if (where := (row, col)) in self.locations:
            where = self.locations.index(where)
            output = self.frames[where]

            if as_backend:
                return output.raw
            else:
                return output

        return None

    def LocationOfFrame(self, frame: frame_t, /) -> tuple[int, int] | None:
        """"""
        if frame not in self.frames:
            L.error(f"Unknown frame {frame}")
            return None

        where = self.frames.index(frame)

        return self.locations[where]

    def RemoveFrame(self, frame: frame_t | h.Sequence[int], /) -> None:
        """"""
        if isinstance(frame, h.Sequence):
            location = frame
            frame = self.FrameAtLocation(*location)
        else:
            location = self.LocationOfFrame(frame)

        self.frames.remove(frame)
        self.locations.remove(location)

        if self.frames.__len__() > 0:
            max_row = max(_row for _row, _ in self.locations)
            max_col = max(_col for _, _col in self.locations)
            self.shape = [max_row + 1, max_col + 1]
        else:
            self.shape = _DefaultShape()

        self._RemoveBackendFrame(frame.raw, self.raw)

    @staticmethod
    def _RemoveBackendFrame(
        frame: backend_frame_h, figure: backend_figure_h, /
    ) -> None:
        """"""
        raise NotImplementedError

    def Clear(self) -> None:
        """"""
        # Do not use a for-loop since self.frames will be modified during looping.
        while self.frames.__len__() > 0:
            frame = self.frames[0]
            self.RemoveFrame(frame)

    def Show(
        self,
        /,
        *,
        modal: bool = True,
    ) -> None:
        """"""
        if self.offline_version:
            return

        if self.frames.__len__() == 0:
            L.warning(f"Figure {self.title} empty; Not showing.")
            return

        self.AdjustLayout()
        self._BackendShow(modal)

    def _BackendShow(self, modal: bool, /) -> None:
        """"""
        raise NotImplementedError


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
