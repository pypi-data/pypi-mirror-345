"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import importlib as mprt
import inspect as insp
import re as rgex
import sys as s

from babelplot.extension.function import FunctionSignature, parameter_w_name_h

"""
insp.Parameter.POSITIONAL_ONLY
insp.Parameter.POSITIONAL_OR_KEYWORD
insp.Parameter.VAR_POSITIONAL
insp.Parameter.KEYWORD_ONLY
insp.Parameter.VAR_KEYWORD
"""


def PrintBackendDraft(target_class: str, /) -> None:
    """"""
    if "." not in target_class:
        print(
            f"{target_class}: Invalid class specification. "
            f"Expected=Must contain at least one dot."
        )
        s.exit(1)

    py_module, target_class = target_class.rsplit(sep=".", maxsplit=1)
    imported = mprt.import_module(py_module)

    if not hasattr(imported, target_class):
        print(f"{target_class}: Not a class of module {py_module}")
        s.exit(2)

    target_class = getattr(imported, target_class)
    for name in sorted(dir(target_class)):
        attribute = getattr(target_class, name)
        if insp.isfunction(attribute):
            documentation = insp.getdoc(attribute)
            if not (
                (documentation is None)
                or (
                    rgex.search(r"\bplot\b", documentation, flags=rgex.IGNORECASE)
                    is None
                )
            ):
                signature, _ = FunctionSignature(attribute, should_include_name=True)
                if (n_parameters := signature.__len__()) == 0:
                    continue
                if signature[0][-1] == "self":
                    if n_parameters == 1:
                        continue
                    if not _ParameterIsPositional(signature[1]):
                        continue
                elif not _ParameterIsPositional(signature[0]):
                    continue

                parameters = []
                for parameter in signature:
                    if parameter[-1] not in ("self", "args", "kwargs"):
                        parameters.append(_SpecificationOfParameter(parameter))
                parameters = str(parameters)[1:-1].replace("'", "")
                print(f"({name}, ({parameters}))")


_POSITIONAL_PARAMETERS = (
    insp.Parameter.POSITIONAL_ONLY.description,
    insp.Parameter.POSITIONAL_OR_KEYWORD.description,
)


def _SpecificationOfParameter(parameter: parameter_w_name_h, /) -> str:
    """"""
    if _ParameterIsPositional(parameter):
        return parameter[-1]  # str(pos_arg_t)[1:] + "/" + parameter[-1]

    return f'"{parameter[-1]}"'


def _ParameterIsPositional(parameter: parameter_w_name_h, /) -> bool:
    """"""
    return (parameter[0] in _POSITIONAL_PARAMETERS) and (
        parameter[2] is insp.Parameter.empty
    )


if __name__ == "__main__":
    #
    PrintBackendDraft(s.argv[1])


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
