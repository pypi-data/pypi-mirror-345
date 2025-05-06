"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import importlib as mprt
import importlib.util as mput
import sys as s
import typing as h
from pathlib import Path as path_t

from _operator import itemgetter as ItemAt
from babelplot.constant.backend import BACKEND_FROM_ALIAS, DEFAULT_BACKEND
from babelplot.constant.path import BACKEND_CATALOG_PY_PATH
from babelplot.type.plot_function import plot_function_h, plot_functions_h
from babelplot.type.plot_type import plot_e, plot_type_h
from babelplot.type.translator import arguments_translations_h
from logger_36 import L


@d.dataclass(slots=True, repr=False, eq=False)
class backend_t:
    path: path_t
    py_path: str
    plot_functions: plot_functions_h | None = None
    arguments_translations: arguments_translations_h | None = None

    def Activate(
        self,
        plot_functions: plot_functions_h,
        arguments_translations: arguments_translations_h,
        /,
    ) -> None:
        """"""
        self.plot_functions = plot_functions
        self.arguments_translations = arguments_translations

    def PlotFunction(
        self,
        type_: plot_e,
        frame_dim: int,
        /,
    ) -> plot_function_h:
        """"""
        plot_functions = self.plot_functions
        where = frame_dim - 2
        if ((output := plot_functions.get(type_)) is None) or (output[where] is None):
            return plot_functions[plot_e._DEFAULT][where](type_, frame_dim)

        return output[where]

    def TranslatedArguments(
        self,
        args: h.Sequence[h.Any],
        kwargs: dict[str, h.Any],
        who_s_asking: str | h.Callable | None,
        /,
    ) -> tuple[h.Sequence[h.Any], dict[str, h.Any]]:
        """"""
        translations = self.arguments_translations
        if (translations is None) or (translations.__len__() == 0):
            return args, kwargs

        if (generics := translations.get(None)) is None:
            generics = {}
        if (for_who_s_asking := translations.get(who_s_asking)) is None:
            for_who_s_asking = {}

        out_args = []
        out_kwargs = {}

        from_args_to_args = []
        for idx, value in enumerate(args):
            if (translation := for_who_s_asking.get(idx, -1)) == -1:
                # No translation needed; Keeping the passed arg.
                out_args.append(value)
            elif translation is None:
                # The argument should be discarded.
                pass
            else:  # isinstance(translation, int|str | tuple[int|str, h.Callable])
                # The passed arg should be placed at the position "translation", or
                # should actually be a kwarg with name "translation".
                if isinstance(translation, list | tuple):
                    translation, NewConvertedValue = translation
                    value = NewConvertedValue(value)
                if isinstance(translation, int):
                    from_args_to_args.append([translation, value])
                else:
                    out_kwargs[translation] = value

        out_args = [[_pos, _vle] for _pos, _vle in enumerate(out_args, start=1)]
        _InsertArguments(out_args, from_args_to_args)

        from_kwargs_to_args = []
        for key, value in kwargs.items():
            # Apply generic translation first, if any.
            key = generics.get(key, key)

            # Search for specific translation.
            if (translation := for_who_s_asking.get(key, -1)) == -1:
                # No translation needed; Keeping the passed kwarg.
                out_kwargs[key] = value
            elif translation is None:
                # The argument should be discarded.
                pass
            else:
                if isinstance(translation, list | tuple):
                    translation, NewConvertedValue = translation
                    value = NewConvertedValue(value)
                if isinstance(translation, str):
                    out_kwargs[translation] = value
                else:  # isinstance(translation, int)
                    from_kwargs_to_args.append([translation, value])

        _InsertArguments(out_args, from_kwargs_to_args)
        out_args = tuple(map(ItemAt(1), out_args))

        if (ApplyGlobalTranslation := generics.get(None)) is not None:
            ApplyGlobalTranslation(out_kwargs, who_s_asking)

        return out_args, out_kwargs

    def __str__(self) -> str:
        """"""
        return self.py_path


def _InsertArguments(
    current: list[list[int | h.Any]], new: list[list[int | h.Any]], /
) -> None:
    """
    Note: list[int | h.Any] should actually be mutable_tuple[int, h.Any].
    """
    # Note: It is important to sort from_args_to_args so that a higher-positioned
    # argument does not get shifted even higher by the insertion of a lower-positioned
    # argument dealt with later.
    for position, value in sorted(new, key=ItemAt(0)):
        for argument in current:
            if argument[0] >= position:
                argument[0] += 1
        current.append([position, value])


@d.dataclass(slots=True, repr=False, eq=False)
class backends_t(dict[str, backend_t]):

    def __post_init__(self) -> None:
        """"""
        parent = path_t(__file__).parent.parent.parent
        catalog_path = parent / path_t(*BACKEND_CATALOG_PY_PATH.split("."))
        for node in catalog_path.glob("*"):
            if node.name.startswith("_"):
                continue

            if node.is_dir():
                main = node / "main.py"
                if main.is_file():
                    node = main
                else:
                    continue

            py_path = ".".join(node.relative_to(parent).parent.parts + (node.stem,))

            self[node.stem[:-1]] = backend_t(path=node, py_path=py_path)

    def Activate(
        self, backend: str | path_t | None, /
    ) -> tuple[str | None, type | None]:
        """
        backends: Importing runtime BACKENDS currently creates an import cycle.
        """
        module = None
        if backend is None:
            backend = DEFAULT_BACKEND
        else:
            # Check if str | path_t corresponds to a file.
            path = path_t(backend)
            if path.is_file():
                # TODO: Check the exceptions that are raised when not a valid Python
                #     module (not found in the documentation).
                backend_stem = path.stem
                spec = mput.spec_from_file_location(backend_stem, path)

                module = mput.module_from_spec(spec)

                spec.loader.exec_module(module)
                s.modules[backend_stem] = module
            elif isinstance(backend, path_t):
                L.error(
                    f"{backend}: Unusable backend. "
                    f"Path does not point to a regular file."
                )
                return None, None

        if module is None:
            if backend in self:
                py_path = self[backend].py_path
            elif backend in BACKEND_FROM_ALIAS:
                py_path = self[BACKEND_FROM_ALIAS[backend]].py_path
            else:
                py_path = backend
            try:
                module = mprt.import_module(py_path)
            except ModuleNotFoundError as exception:
                L.error(
                    f"{backend}: Unusable backend. "
                    f"Might be due to backend not being installed "
                    f"or implementation error in backend:\n{exception}"
                )
                return None, None

        name = module.NAME
        plot_functions = module.PLOTS
        arguments_translations = getattr(module, "TRANSLATIONS", None)

        self[name].Activate(plot_functions, arguments_translations)

        return name, module.figure_t

    def PlotFunction(
        self,
        name: str,
        type_: plot_type_h | plot_function_h,
        frame_dim: int,
        /,
    ) -> h.Callable:
        """
        Returns the plot type callable for the given plot_e member and the dimension passed
        as "frame_dim". The available callables are passed as "plot_functions". The name of
        the backend, passed as "backend", is only used in error messages.
        """
        if isinstance(type_, str):
            type_ = plot_e.NewFromName(type_)

        if isinstance(type_, plot_e):
            return self[name].PlotFunction(type_, frame_dim)

        return type_

    def TranslatedArguments(
        self,
        name: str,
        args: h.Sequence[h.Any],
        kwargs: dict[str, h.Any],
        who_s_asking: str | h.Callable | None,
        /,
    ) -> tuple[h.Sequence[h.Any], dict[str, h.Any]]:
        """"""
        return self[name].TranslatedArguments(
            args,
            kwargs,
            who_s_asking,
        )

    def IsValid(self, name: str, /) -> bool:
        """"""
        return (name in self) or (name in BACKEND_FROM_ALIAS)

    def __str__(self) -> str:
        """"""
        names = sorted(filter(lambda _: _ not in BACKEND_FROM_ALIAS, self.keys()))
        names = str(names)[1:-1].replace("'", "")
        aliases = (f"{_als} -> {_nme}" for _als, _nme in BACKEND_FROM_ALIAS.items())

        output = [
            "Backends:",
            f"    Names: {names}",
            f"    Aliases: {', '.join(sorted(aliases))}",
            "",
        ]
        output.extend(f"    {_key}: {_vle}" for _key, _vle in self.items())

        return "\n".join(output)


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
