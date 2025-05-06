import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from commons.locales import Locale, LocaleSettings


class TestLocales(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_messages_po(self):
        messages_dir = self.temp_dir / "en" / "LC_MESSAGES"
        messages_dir.mkdir(parents=True, exist_ok=True)
        (messages_dir / "messages.po").write_text('msgid "Hello"\nmsgstr "Hello, World!"')

    # ----- Locale Tests -----
    def test_locale_initialization(self):
        locale = Locale("en")
        self.assertIsInstance(locale, Locale)
        self.assertEqual(locale.language, "en")

    def test_locale_with_translations_directory(self):
        self._create_messages_po()
        locale = Locale("en", self.temp_dir)
        self.assertIsInstance(locale, Locale)
        self.assertTrue(locale._translation is not None)

    def test_locale_gettext(self):
        self._create_messages_po()
        locale = Locale("en", self.temp_dir)
        self.assertEqual(locale.gettext("Hello"), "Hello, World!")

    def test_locale_languages_method(self):
        locale = Locale("en")
        result = locale.languages(filter_by=["pt_BR", "es_ES"])
        self.assertEqual(result, ["Brazilian Portuguese", "European Spanish"])

    def test_locale_format_number(self):
        locale = Locale("pt_BR")
        self.assertEqual(locale.format_number(1234.56), "1.234,56")

    def test_locale_format_currency(self):
        locale = Locale("pt_BR")
        self.assertEqual(locale.format_currency(1234.56, "BRL"), "R$\u00A01.234,56")

    def test_locale_format_date(self):
        locale = Locale("pt_BR")
        test_date = date(2025, 8, 4)
        self.assertEqual(locale.format_date(test_date), "4 de ago. de 2025")
        self.assertEqual(locale.format_date(test_date, format="short"), "04/08/2025")

    def test_locale_format_datetime(self):
        locale = Locale("pt_BR")
        test_datetime = datetime(2025, 8, 4, 12, 43, 22)
        self.assertEqual(locale.format_datetime(test_datetime), "4 de ago. de 2025 12:43:22")
        self.assertEqual(locale.format_datetime(test_datetime, format="short"), "04/08/2025 12:43")

    def test_locale_format_timedelta(self):
        locale = Locale("pt_BR")
        delta = timedelta(days=4)
        self.assertEqual(locale.format_timedelta(delta), "4 dias")

    def test_invalid_locale_raises_error(self):
        with self.assertRaises(ValueError):
            Locale("invalid")

    # ----- LocaleConfig Tests -----
    def test_locale_config_initialization(self):
        config = LocaleSettings(supported_locales=["en"])
        self.assertIsInstance(config, LocaleSettings)

    def test_locale_config_default_locale(self):
        config = LocaleSettings(supported_locales=["en", "en_US"])
        self.assertEqual(config.default_locale.language, "en")

    def test_locale_config_supported_languages(self):
        config = LocaleSettings(supported_locales=["en", "en_US"])
        self.assertEqual(config.supported_languages, ["English", "American English"])

    def test_locale_config_locales(self):
        config = LocaleSettings(supported_locales=["en", "en_US"])
        self.assertEqual(list(config.locales.keys()), ["en", "en_US"])

    def test_locale_config_lookup(self):
        config = LocaleSettings(supported_locales=["en"])
        self.assertEqual(str(config.lookup("en_US")), "en")

        config = LocaleSettings(supported_locales=["en_US"])
        self.assertEqual(str(config.lookup("en")), "en_US")

    def test_locale_config_invalid_supported_locales(self):
        with self.assertRaises(ValueError):
            LocaleSettings(supported_locales=[])

        with self.assertRaises(ValueError):
            LocaleSettings(supported_locales=["invalid_locale"])

    # ----- Edge Cases -----
    def test_locale_without_translations(self):
        locale = Locale("en", Path("/invalid/path"))
        self.assertEqual(locale.gettext("Hello"), "Hello")

    def test_locale_config_with_nonexistent_translations_dir(self):
        config = LocaleSettings(supported_locales=["en"], translations_directory=Path("/invalid/path"))
        self.assertFalse(hasattr(config, "translations_directory"))

    @patch('commons.locales.Locale.compile')
    def test_locale_compile_method(self, mock_compile):
        messages_dir = self.temp_dir / "fr" / "LC_MESSAGES"
        messages_dir.mkdir(parents=True, exist_ok=True)
        (messages_dir / "messages.po").write_text("msgid 'Bonjour'")
        Locale("fr", self.temp_dir)
        mock_compile.assert_called_once_with(messages_dir)

    def test_locale_format_interval(self):
        locale = Locale("pt_BR")
        start = date(2025, 8, 4)
        end = date(2025, 10, 8)
        self.assertEqual(
            locale.format_interval(start, end, skeleton="ddMMyyyy"),
            "04/08/2025\u2009–\u200908/10/2025"
        )

    def test_locale_format_list(self):
        locale = Locale("pt_BR")
        self.assertEqual(locale.format_list(["1", "2", "3"]), "1, 2 e 3")
