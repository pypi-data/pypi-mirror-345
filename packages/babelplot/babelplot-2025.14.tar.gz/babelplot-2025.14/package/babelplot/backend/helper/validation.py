"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import importlib as mprt
import importlib.util as mput
import sys as s
import typing as h
from pathlib import Path as path_t

from babelplot.runtime.backends import BACKENDS
from babelplot.type.plot_function import plot_functions_h
from babelplot.type.plot_type import plot_e


def CheckBackend(backend: str | path_t, /) -> None:
    """"""
    path = path_t(backend)
    if path.is_file():
        backend_stem = path.stem
        spec = mput.spec_from_file_location(backend_stem, path)
        module = mput.module_from_spec(spec)
        spec.loader.exec_module(module)
        s.modules[backend_stem] = module
    else:
        if backend in BACKENDS:
            py_path = BACKENDS[backend].py_path
        else:
            py_path = backend
        try:
            module = mprt.import_module(py_path)
        except ModuleNotFoundError as exception:
            print(f"Backend {backend} failed to import:\n{exception}")
            return

    if hasattr(module, "PLOTS"):
        defined = getattr(module, "PLOTS")
        if isinstance(defined, dict):
            issues = _PlotFunctionsIssues(defined)
            if issues is not None:
                print(f"--- PLOTS:\n    ", "\n    ".join(issues), sep="")
        else:
            print(
                f'--- {type(defined).__name__}: Invalid type for "PLOTS". Expected=dict.'
            )
    else:
        print('--- Missing "PLOTS" dictionary')

    # TODO: Check that translations respect the format (to be documented by the way).


def _PlotFunctionsIssues(plots: plot_functions_h, /) -> h.Sequence[str] | None:
    """"""
    issues = []

    for key, value in plots.items():
        if not isinstance(key, plot_e):
            issues.append(
                f"{key}/{type(key).__name__}: Invalid plot type. "
                f"Expected={plot_e.__name__}."
            )
            continue

        if not isinstance(value, list | tuple):
            issues.append(
                f"{key}/{type(value).__name__}: Invalid plot record type. "
                f"Expected=list or tuple."
            )
            continue

        value = tuple(filter(lambda _: _ is not None, value))

        how_defined = key.value
        if (n_dimensions := value.__len__()) != (
            n_required := how_defined[2].__len__()
        ):
            issues.append(
                f"{key}: Invalid number of possible dimensions {n_dimensions}. "
                f"Expected={n_required}."
            )
            continue

        for d_idx, for_dim in enumerate(value):
            if not callable(for_dim):
                issues.append(
                    f"{key}/{for_dim}: Invalid plot function "
                    f"for dim {how_defined[2][d_idx]}. "
                    f"Expected=Callable."
                )

    missing = set(plot_e.__members__.values()).difference(plots.keys())
    if missing.__len__() > 0:
        missing = str(sorted(_elm.name for _elm in missing))[1:-1].replace("'", "")
        issues.append(f"Missing plot type(s): {missing}")

    if issues.__len__() > 0:
        return issues

    return None


if __name__ == "__main__":
    #
    CheckBackend(s.argv[1])


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
