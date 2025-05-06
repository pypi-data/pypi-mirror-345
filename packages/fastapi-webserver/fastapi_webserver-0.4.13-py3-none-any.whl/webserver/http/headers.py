from typing import Optional

from commons.locales import LocaleSettings, Locale

def get_locale(accept_language: str, locale_config: Optional[LocaleSettings]) -> Optional[Locale]:
    """
    Lookup for a Locale based on the `Accept-Language` header content.
    :param accept_language: `Accept-Language` header content
    :param locale_config: A locale configuration
    :return: the best match for the locale list, or else None
    """
    match: Optional[Locale] = None

    try:
        # Parse `Accept-Language` HTTP header into a valid Locales
        languages: list[Locale] = [
            Locale(lang_code.split(";")[0].replace("-", "_").strip(), locale_config.translations_directory)
            for lang_code in accept_language.split(",") if not lang_code.strip().startswith("*")
        ]

        # find the best match
        for lang in languages:
            match = locale_config.lookup(lang)
            if match:
                break
    except (ValueError, AttributeError):
        pass

    return locale_config.default_locale if (not match and locale_config) else match
