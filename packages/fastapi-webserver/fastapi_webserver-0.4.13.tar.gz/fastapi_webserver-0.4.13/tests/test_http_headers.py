import tempfile
import unittest
from pathlib import Path

RESOURCES_FOLDER: Path = Path(__file__).parent / "resources"
TEMP_FOLDER: Path = Path(tempfile.gettempdir())


class TestHTTPTools(unittest.TestCase):
    def test_lang_lookup(self):
        from webserver.http.headers import get_locale
        from commons.locales import LocaleSettings

        accept_lang_header_val = "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5"

        assert get_locale(accept_lang_header_val, LocaleSettings(translations_directory=TEMP_FOLDER,
                                                               supported_locales=["fr", "en"])).language == "fr"
        assert get_locale(accept_lang_header_val, LocaleSettings(translations_directory=TEMP_FOLDER,
                                                               supported_locales=["pt", "de"])).language == "de"
        assert get_locale(accept_lang_header_val, LocaleSettings(translations_directory=TEMP_FOLDER,
                                                               supported_locales=["en_US"])).language == "en"
        assert get_locale(accept_lang_header_val, LocaleSettings(translations_directory=TEMP_FOLDER,
                                                               supported_locales=["pt_BR"])).language == "pt"
