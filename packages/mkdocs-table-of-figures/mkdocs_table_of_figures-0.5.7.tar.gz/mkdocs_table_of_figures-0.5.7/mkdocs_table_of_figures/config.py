"""
File        : mkdocs_table_of_figures/config.py
Description : This is the config class containing the plugin config schema 
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

import os
import yaml
from typing import Dict

from mkdocs.config.base import Config, BaseConfigOption, ValidationError
from mkdocs.config import config_options

# Import to resolve path of builtin figure types configs files (.yml)
from .structure.figure_type import builtin_configs

class FigureTypeConfig(Config):
    name = config_options.Type(str)
    pattern = config_options.Type(str)
    template = config_options.Optional(config_options.Type(str))
    metadata = config_options.Optional(config_options.Type(dict))

class FigureTypeOption(BaseConfigOption):
    SUBCONFIG = config_options.SubConfig(FigureTypeConfig)
    BUILTIN_TYPES_DIRECTORY = os.path.dirname(builtin_configs.__file__)

    _builtin_types: Dict[str, FigureTypeConfig]

    @property
    def builtin_types(self) -> Dict[str, FigureTypeConfig]:
        if not self._builtin_types:
            self._load_builtin_types()
        
        return self._builtin_types
    
    def __init__(self):
        self._builtin_types = {}

    def _load_builtin_types(self) -> None:
        self._builtin_types = {}
        
        for filename in os.listdir(self.BUILTIN_TYPES_DIRECTORY):
            if os.path.isfile(os.path.join(self.BUILTIN_TYPES_DIRECTORY, filename)) and os.path.splitext(filename)[1] in ['.yml', '.yaml']:
                name = os.path.splitext(filename)[0]
                path = os.path.join(self.BUILTIN_TYPES_DIRECTORY, filename)
                with open(path, 'r', encoding='utf8') as file:
                    try:
                        config = yaml.safe_load(file)
                        if isinstance(config, dict):
                            if 'name' not in config.keys():
                                config['name'] = name
                            self._builtin_types[name] = config
                    except yaml.YAMLError as e:
                        raise ValidationError(f"Error loading built-in type '{filename}': {e}")

    def run_validation(self, value):
        if isinstance(value, str):
            if value in self.builtin_types:
                return self.SUBCONFIG.validate(self.builtin_types[value])
            else:
                raise ValidationError(f"Unknown built-in figure type '{value}'. Available: {list(self.builtin_types.keys())}")
        elif isinstance(value, dict):
            return self.SUBCONFIG.validate(value)
        else:
            raise ValidationError(f"Expected a string or a dict for FigureTypeConfig, got: {value!r}")

class TableOfFiguresConfig(Config):
    DIRECTIVE_IDENTIFIER_DEFAULT = 'table-of-figures'
    FIGURE_TYPES_DEFAULT = ['image', 'table', 'codeblock']

    CUSTOM_TEMPLATES_PATH_DEFAULT = None
    TRANSLATIONS_OVERRIDES_PATH_DEFAULT = None

    CAPTION_IDENTIFIER_DESCRIPTION_SEPARATOR_DEFAULT = ' — '
    SECTIONS_BREADCRUMB_SEPARATOR_DEFAULT = ' > '
    
    directive_identifier = config_options.Type(str, default=DIRECTIVE_IDENTIFIER_DEFAULT)
    figure_types = config_options.ListOfItems(FigureTypeOption(), default=FIGURE_TYPES_DEFAULT)

    custom_templates_path = config_options.Optional(config_options.Type(str, default=CUSTOM_TEMPLATES_PATH_DEFAULT))
    translations_overrides_path = config_options.Optional(config_options.Type(str, default=TRANSLATIONS_OVERRIDES_PATH_DEFAULT))

    caption_identifier_description_separator = config_options.Type(str, default=CAPTION_IDENTIFIER_DESCRIPTION_SEPARATOR_DEFAULT)
    sections_breadcrumb_separator = config_options.Type(str, default=SECTIONS_BREADCRUMB_SEPARATOR_DEFAULT)
