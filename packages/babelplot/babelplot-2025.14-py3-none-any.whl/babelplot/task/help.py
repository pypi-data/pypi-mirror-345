"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import importlib as mprt
import sys as s

from babelplot.constant.path import BACKEND_CATALOG_PY_PATH
from babelplot.runtime.backends import BACKENDS
from babelplot.type.plot_type import plot_e
from logger_36 import L
from logger_36.api.handler import AddConsoleHandler

AddConsoleHandler(L)


def PrintUsage() -> None:
    """"""
    print(
        "Usage: python -m babelplot.task.help parameter_1 [parameter_2...]\n"
        "    parameter_1 can be:\n"
        "        - backends: lists the available backends\n"
        '        - one of the backends listed when calling with parameter_1 being "backends": '
        "requires additional parameters (see below)\n"
        "        - plots: list the known plot types\n"
        "    parameters_2, when required, can be:\n"
        "        - plots: lists the plots available for the specified backend\n"
        "        - parameters: lists the BabelPlot equivalents of some backend plot parameters"
    )


def PrintHelp() -> None:
    """"""
    if (n_arguments := s.argv.__len__()) == 1:
        PrintUsage()
    elif n_arguments == 2:
        if s.argv[1] == "backends":
            backends = str(BACKENDS).splitlines()
            backends = (f"    {_lne}" for _lne in backends)
            backends = "\n".join(backends)
            print(f"Available Backends:\n{backends}")
        elif s.argv[1] == "plots":
            plots = plot_e.Formatted().splitlines()
            plots = (f"    {_lne}" for _lne in plots)
            plots = "\n".join(plots)
            print(f"Defined BabelPlot Plots:\n{plots}")
        else:
            print(f"{s.argv[1]}: Invalid parameter")
            PrintUsage()
    elif n_arguments == 3:
        if BACKENDS.IsValid(s.argv[1]):
            backend_name = s.argv[1]
            try:
                backend = mprt.import_module(
                    f"{BACKEND_CATALOG_PY_PATH}.{backend_name}_"
                )
            except ModuleNotFoundError as exception:
                print(f"Backend {backend_name} failed to import:\n{exception}")
                PrintUsage()
                return

            if s.argv[2] == "plots":
                plots = []
                for key, value in backend.PLOTS.items():
                    if key is plot_e._DEFAULT:
                        continue

                    functions = []
                    for dim, function in enumerate(value, start=2):
                        if function is not None:
                            functions.append(f"Dim.{dim}: {function.__name__}")
                    functions = ", ".join(functions)
                    if functions.__len__() > 0:
                        plots.append(f"{key}: {functions}")
                plots = "\n    ".join(plots)
                print(f"Available {s.argv[1].capitalize()} Plots:\n    {plots}")
            elif s.argv[2] == "parameters":
                if hasattr(backend, "TRANSLATIONS") and (
                    backend.TRANSLATIONS.__len__() > 0
                ):
                    translations = []
                    for babelplot, backend in backend.TRANSLATIONS.items():
                        translations.append(f"{babelplot} -> {backend}")
                    translations = "\n".join(translations)
                    print(
                        f"Available Backend Parameter Translations "
                        f"(BabelPlot -> {s.argv[1]}):\n{translations}"
                    )
                else:
                    print("No Translations Defined")
            else:
                print(f"{s.argv[2]}: Invalid parameter")
                PrintUsage()
        else:
            print(f"{s.argv[1]}: Invalid backend")
            PrintUsage()


if __name__ == "__main__":
    #
    PrintHelp()


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
