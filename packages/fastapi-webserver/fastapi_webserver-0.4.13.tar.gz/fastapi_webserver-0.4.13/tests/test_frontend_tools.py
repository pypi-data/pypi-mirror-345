import tempfile
import unittest
from pathlib import Path

from logging import Logger
from commons import logging

RESOURCES_FOLDER: Path = Path(__file__).parent / "resources"
TEMP_FOLDER: Path = Path(tempfile.gettempdir())

logging.config(level=logging.INFO)
LOGGER: Logger = logging.get_logger(__name__)
LOGGER.info(TEMP_FOLDER)


class TestFrontendTools(unittest.TestCase):
    def test_sass_compiler(self):
        from webserver.frontend import css

        cssfile: Path = TEMP_FOLDER / "styles.css"
        mapfile: Path = TEMP_FOLDER / "styles.css.map"

        css.compile(source=(RESOURCES_FOLDER / "assets/sass/theme.scss"), output=cssfile, verbose=True)

        self.assertTrue(cssfile.exists())
        self.assertTrue(mapfile.exists())
        self.assertEqual("html{color:#000 !important}/*# sourceMappingURL=styles.css.map */\n",
                         cssfile.read_text(encoding="utf-8"))
