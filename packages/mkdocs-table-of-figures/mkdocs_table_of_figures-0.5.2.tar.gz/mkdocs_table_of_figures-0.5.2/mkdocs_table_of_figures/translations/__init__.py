"""
File        : mkdocs_table_of_figures/translations/__init__.py (translations.py)
Description : This file contains the translations handler.
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

import os
import json

from typing import Dict, Union, Optional

class TranslationsEntries:
    """
    A tree-like structure holding translation entries, supporting dotted key access
    """
    # Constants
    ENTRIES_KEY_SEPARATOR = '.'

    # Attributes
    entries: Dict[str, Union[str, 'TranslationsEntries']]

    # Properties
    # ...

    # Constructors
    def __init__(self, entries: Dict[str, Union[str, dict]]):
        self.entries = {}

        for key, value in entries.items():
            if isinstance(value, dict):
                value = TranslationsEntries(value)
            self.entries[key] = value

    # Methods
    def __getitem__(self, key) -> Optional[Union[str, 'TranslationsEntries']]:
        """
        Supports dot-separated key lookup for nested entries.
        """

        def _recursive_getitem(item: 'TranslationsEntries', key) -> Optional[Union[str, 'TranslationsEntries']]:
            value = item.entries.get(key)

            if self.ENTRIES_KEY_SEPARATOR in key:
                current_key, rest_keys = key.split(self.ENTRIES_KEY_SEPARATOR, 1)
                value = item.entries.get(current_key)
                
                if isinstance(value, TranslationsEntries) and rest_keys:
                    value = _recursive_getitem(value, rest_keys)

            return value

        return _recursive_getitem(self, key)


class Translations(TranslationsEntries):
    """
    Translation handler that loads language files, supports fallbacks,
    and allows entry override at load time.
    """
    # Constants
    TRANSLATIONS_DIRECTORY = os.path.dirname(__file__)
    TRANSLATIONS_FILE_FORMAT = 'json'
    FALLBACK_LANG = 'en'
    USE_FALLBACK_DEFAULT = True

    # Attributes
    lang: str

    # Properties
    # ...

    # Constructors
    def __init__(self, lang: str, entries: Dict[str, Union[str, dict]]):
        super().__init__(entries)
        self.lang = lang

    # NOTE: These 2 constructors are a little bit confusing. Might be good to change them.
    @classmethod
    def init_from_json(cls, lang: str, use_fallback: bool = USE_FALLBACK_DEFAULT, *overrides: Dict[str, Union[str, dict]]) -> 'Translations':
        fallback_dict = cls._load_json_file(cls._get_lang_file(cls.FALLBACK_LANG)) if use_fallback else {}
        lang_dict = cls._load_json_file(cls._get_lang_file(lang))

        merged_dict = cls._deep_merge(fallback_dict, lang_dict)
        for override in overrides:
            merged_dict = cls._deep_merge(merged_dict, override)

        return cls(lang, merged_dict)
    
    @classmethod
    def init_from_config(cls, lang: str, overrides_path: str) -> 'Translations':
        overrides_dict = cls._load_json_file(overrides_path) if overrides_path is not None else {}

        return cls.init_from_json(lang, cls.USE_FALLBACK_DEFAULT, overrides_dict)
    
    # Class methods
    @classmethod
    def _get_lang_file(cls, lang: str) -> str:
        return os.path.join(cls.TRANSLATIONS_DIRECTORY, f'{lang}.{cls.TRANSLATIONS_FILE_FORMAT}')

    @classmethod
    def _load_json_file(cls, filepath: str) -> Dict[str, Union[str, dict]]:
        data = {}

        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError(f"{filepath} must contain a top-level JSON object")
        
        return data
    
    @classmethod
    def _deep_merge(cls, base: Dict[str, Union[str, dict]], override: Dict[str, Union[str, dict]]) -> Dict[str, Union[str, dict]]:
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value

        return result
