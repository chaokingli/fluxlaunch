"""GUI internationalization module."""

import json
import os
from pathlib import Path


class Translator:
    """Translation manager for GUI i18n."""

    def __init__(self, lang=None):
        """Initialize translator with optional language.

        Args:
            lang: Optional language code. If None, auto-detect from LANG env var.
        """
        self.lang = lang or self._detect_lang()
        self._strings = {}
        self.load(self.lang)

    def _detect_lang(self):
        """Detect language from environment variables.

        Checks LANG env var first, then defaults to 'en'.
        Extracts language code from format like 'en_US.UTF-8'.
        """
        lang = os.environ.get("LANG", "en")
        return lang.split("_")[0] if lang else "en"

    def load(self, lang):
        """Load translation JSON file for given language.

        Args:
            lang: Language code to load (e.g., 'en', 'zh').
        """
        translations_dir = Path(__file__).parent / "translations"
        file_path = translations_dir / f"{lang}.json"
        if file_path.exists():
            with open(file_path, encoding="utf-8") as f:
                self._strings = json.load(f)
        else:
            self._strings = {}

    def t(self, key, default=None):
        """Get translation for key with dot notation support.

        Args:
            key: Translation key in dot notation (e.g., 'menu.file', 'btn.start').
            default: Optional default value if key not found.

        Returns:
            Translated string or key/default if not found.
        """
        # Handle dot notation for nested keys
        parts = key.split(".")
        value = self._strings
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        return value if value is not None else (default or key)

    def __call__(self, key, default=None):
        """Make Translator callable as _(key).

        Args:
            key: Translation key in dot notation.
            default: Optional default value if key not found.

        Returns:
            Translated string or key/default if not found.
        """
        return self.t(key, default)

    def set_language(self, lang):
        """Change current language.

        Args:
            lang: New language code to load.
        """
        self.lang = lang
        self.load(lang)


# Global instance with default English
_ = Translator("en")
