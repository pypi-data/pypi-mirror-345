"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import gzip
import os as ostm
import sys as s
import tempfile as tmpf
import time
import typing as h

from babelplot.constant.project import NAME
from babelplot.type.figure import figure_t
from PyQt6.QtCore import QUrl as url_t  # noqa
from PyQt6.QtWebEngineWidgets import QWebEngineView as web_view_t  # noqa
from PyQt6.QtWidgets import QApplication as application_t  # noqa
from PyQt6.QtWidgets import QStackedWidget as stack_t  # noqa

TOO_BIG_OF_AN_HTML = 5_000_000
PATIENCE = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html, body {
                height: 100%;
            }
            div {
                width: 100%;
                height: 100%;
                display: table;
                text-align: center;
            }
            p {
                display: table-cell;
                vertical-align: middle;
                font-size: 4vw;
                font-weight: bold;
                font-family: monospace;
                color: darkgrey;
            }
        </style>
    </head>
    <body>
        <div>
            <p>Preparing Plot...</p>
        <div/>
    </body>
    </html>
"""


def ShowHTMLPlotWithPyQt(html: str | bytes, /) -> None:
    """"""

    def _SetURLIfNeeded(success: bool, /) -> None:
        """
        From: https://doc.qt.io/qtforpython-6/PySide6/QtWebEngineWidgets/QWebEngineView.html
              #PySide6.QtWebEngineWidgets.PySide6.QtWebEngineWidgets.QWebEngineView.setHtml
            Content larger than 2 MB cannot be displayed[...]
            [...]
            Thereby, the provided code becomes a URL that exceeds the 2 MB limit set by
            Chromium. If the content is too large, the loadFinished() signal is
            triggered with success=False.
        Solution: Use a temporary file (with html extension) and setUrl.
        """
        if success:
            if main is not web_view:
                main.setCurrentWidget(web_view)
            return

        transfer = tmpf.NamedTemporaryFile(mode="w", suffix=".html", delete=False)
        with open(transfer.name, "w") as accessor:
            accessor.write(html)
        url = url_t.fromLocalFile(transfer.name)

        web_view.setUrl(url)
        web_view.closeEvent = lambda _: ostm.remove(transfer.name)

    if isinstance(html, bytes):
        html = gzip.decompress(html).decode()

    application = application_t(s.argv)
    application.setApplicationName(NAME)  # Useful for window manager.

    web_view = web_view_t()
    web_view.loadFinished.connect(_SetURLIfNeeded)
    web_view.setHtml(html)  # Now attempt to set HTML; If failure, then _SetURLIfNeeded.

    if html.__len__() > TOO_BIG_OF_AN_HTML:
        patience = web_view_t()
        patience.setHtml(PATIENCE)

        main = stack_t()
        main.addWidget(web_view)
        main.addWidget(patience)
        main.setCurrentWidget(patience)
    else:
        main = web_view

    main.show()
    application.exec()


def ShowFigures(figures: h.Sequence[figure_t], /) -> None:
    """"""
    if figures.__len__() == 0:
        return

    for figure in figures[1:]:
        figure.Show(modal=False)
    figures[0].Show(modal=True)

    still_running = tuple(_ for _ in figures if _.showing_process is not None)
    if still_running.__len__() == 0:
        return

    while still_running.__len__() > 0:
        time.sleep(0.1)
        still_running = tuple(_ for _ in still_running if _.showing_process.is_alive())

    for figure in figures:
        figure.showing_process = None


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
