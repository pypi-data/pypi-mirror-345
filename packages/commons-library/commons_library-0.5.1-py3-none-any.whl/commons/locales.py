from datetime import datetime, date, timedelta, time, tzinfo
from decimal import Decimal
from pathlib import Path
from typing import Optional, Literal

from babel.core import UnknownLocaleError
from babel import Locale as _BabelLocale


class Locale:
    _locale: Optional[_BabelLocale] = None

    def __init__(self, locale: str, root_directory: Optional[Path] = None):
        try:
            self._locale: _BabelLocale = _BabelLocale.parse(locale)
        except UnknownLocaleError as e:
            raise ValueError(e)

        if root_directory and root_directory.exists():
            import gettext
            self.compile(root_directory / str(self) / "LC_MESSAGES")
            self._translation = gettext.translation("messages", localedir=str(root_directory), languages=[str(self)], fallback=True)
        else:
            self._translation = None

    def __str__(self):
        return str(self._locale)

    @property
    def language(self) -> str:
        return self._locale.language

    @property
    def territory(self) -> Optional[str]:
        return self._locale.territory

    @property
    def display_name(self) -> str:
        return self._locale.display_name

    def languages(self, filter_by: list[str]) -> list[str]:
        return [self._locale.languages.get(lang) for lang in filter_by if lang]

    def format_number(self, number: int | float | Decimal, **kwargs) -> str:
        from babel.numbers import format_decimal
        return format_decimal(number=number, locale=self._locale, **kwargs)

    def format_currency(self, number: int | float | Decimal, currency_code: str, **kwargs) -> str:
        from babel.numbers import format_currency
        return format_currency(number=number, currency=currency_code, locale=self._locale, **kwargs)

    def format_timezone(self, timezone: str | tzinfo) -> str:
        from babel.dates import get_timezone_name
        if isinstance(timezone, str):
            # If timezone is a string, use it directly
            return get_timezone_name(timezone, locale=self._locale)
        elif isinstance(timezone, tzinfo):
            # If timezone is a tzinfo object, get its timezone name
            if hasattr(timezone, "zone"):
                return get_timezone_name(timezone.zone, locale=self._locale)
            else:
                raise ValueError("Unsupported tzinfo object")
        else:
            raise TypeError("Timezone must be a string or a tzinfo object")

    def format_datetime(self, value: datetime, format: Literal['full', 'long', 'medium', 'short'] | str = 'medium',
                        tzinfo: datetime.tzinfo = None) -> str:
        from babel.dates import format_datetime
        return format_datetime(datetime=value, locale=self._locale, format=format, tzinfo=tzinfo)

    def format_date(self, value: date, format: Literal['full', 'long', 'medium', 'short'] | str = 'medium') -> str:
        from babel.dates import format_date
        return format_date(date=value, locale=self._locale, format=format)

    def format_time(self, value: time, format: Literal['full', 'long', 'medium', 'short'] | str = 'medium',
                    tzinfo: datetime.tzinfo = None) -> str:
        from babel.dates import format_time
        return format_time(time=value, locale=self._locale, format=format, tzinfo=tzinfo)

    def format_interval(self, start: date | time, end: date | time, skeleton: Optional[str] = None,
                        tzinfo: datetime.tzinfo = None, **kwargs):
        from babel.dates import format_interval
        return format_interval(start=start, end=end, skeleton=skeleton, locale=self._locale, tzinfo=tzinfo, **kwargs)

    def format_timedelta(self, value: timedelta,
                         granularity: Literal['year', 'month', 'week', 'day', 'hour', 'minute', 'second'] = 'second',
                         format: Literal['narrow', 'short', 'medium', 'long'] = 'long', **kwargs):
        from babel.dates import format_timedelta
        return format_timedelta(delta=value, locale=self._locale, granularity=granularity, format=format, **kwargs)

    def format_list(self, items: list,
                    style: Literal['standard', 'standard-short', 'or', 'or-short', 'unit', 'unit-short', 'unit-narrow'] = 'standard'):
        from babel.lists import format_list
        return format_list(lst=items, locale=self._locale, style=style)

    @classmethod
    def compile(cls, directory: Path):
        # requires gettext at runtime
        if (directory / "messages.po").exists() and not (directory / "messages.mo").exists():
            from command_runner import command_runner
            command_runner(f"pybabel compile --directory={directory} --use-fuzzy "
                           f"--input-file={directory / 'messages.po'} "
                           f"--output-file={directory / 'messages.mo'}", live_output=True)

    def gettext(self, msgid: str):
        if self._translation:
            return self._translation.gettext(msgid)
        else:
            return msgid


class LocaleSettings:
    translations_directory: Path
    locales: dict[str, Locale]
    default_locale: Locale

    def __init__(self, supported_locales: list[str], translations_directory: Optional[Path] = None):
        if translations_directory and translations_directory.exists():
            self.translations_directory = translations_directory

        if supported_locales:
            self.locales = {}

            for locale in supported_locales:
                locale = Locale(locale, translations_directory)

                if locale and locale.territory:
                    # guarantee that both language and language + territory are registered as supported locales
                    self.locales[locale.language] = locale

                self.locales[str(locale)] = locale

            self.default_locale = self.locales.get(supported_locales[0])
        else:
            raise ValueError("Supported Locales were not provided.")

    def lookup(self, locale: str | Locale) -> Optional[Locale]:
        item: Optional[Locale] = None

        if type(locale) == str:
            locale = Locale(locale)

        item = self.locales.get(str(locale))
        if not item and locale.territory:
            item = self.locales.get(locale.language)

        return item

    @property
    def supported_languages(self) -> list[str]:
        return self.default_locale.languages(filter_by=[str(locale) for locale in self.locales])

    def extract_translatable_strings(self, directory: Path):
        raise NotImplementedError
