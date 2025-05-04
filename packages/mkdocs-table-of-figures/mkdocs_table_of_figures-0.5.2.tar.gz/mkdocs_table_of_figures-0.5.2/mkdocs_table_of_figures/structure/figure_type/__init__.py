"""
File        : mkdocs_table_of_figures/structure/type_figure/__init__.py (type_figure.py)
Description : This file contains the FigureType and FigureTypesCollection classes.
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

from typing import Dict, List, Optional, Any

from ...translations import Translations
from ..collection import Collection

class FigureType:
    """
    Represents a type of figure with a pattern used to find it and a template used to replace it.
    """
    # Constants
    TEMPLATE_DEFAULT = \
'''<figure id="{{ figure.id }}" class="{{ figure.classes }}" markdown="block">
{{ figure.content }}
<figcaption markdown="span">{{ figure.caption }}</figcaption>
</figure>'''
    TRANSLATIONS_DEFAULT = None
    METADATA_DEFAULT = {}

    # Class attributes
    translations: Optional[Translations] = TRANSLATIONS_DEFAULT

    # Attributes
    name: str
    pattern: str
    template: str
    metadata: Dict[str, Any]

    # Properties
    @property
    def label(self) -> str:
        output = self.name
        
        # If translation exist use it instead of default value
        if self.translations and self.translations[f'figure_types.{self.name}']:
            output = self.translations[f'figure_types.{self.name}']

        return output

    # Constructors
    def __init__(self, name: str, pattern: str, template: str = TEMPLATE_DEFAULT, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.pattern = rf'{pattern}'
        self.template = rf'{template}'
        self.metadata = metadata if metadata is not None else dict(self.METADATA_DEFAULT) # Ensure creation of a copy of default dict
    
    @classmethod
    def init_from_config(cls, config: Dict[str, Any]) -> "FigureType":
        # NOTE: config.get('template', cls.TEMPLATE_DEFAULT) don't work it return 'None'
        return cls(config['name'], config['pattern'], config.get('template') or cls.TEMPLATE_DEFAULT, config.get('metadata'))

    # Method
    def __str__(self) -> str:
        return f"<FigureType name={self.name} pattern=r'{self.pattern}'>"

class FigureTypes(Collection[FigureType]):
    """
    This is a Collection of FigureType with additional properties 'names'.
    """
    # Constants
    ITEMS_STR_PREVIEW_SEPARATOR = '|'

    # Attributes
    # ...
    
    # Properties
    @property
    def names(self) -> List[str]:
        return [item.name for item in self]
    
    # Constructors
    # ...

    # Class Methods
    @classmethod
    def init_from_config(cls, config: List[Any]) -> "FigureTypes":
        items = []

        for entry in config:
            items.append(FigureType.init_from_config(entry))
        
        return cls(items)

    # Methods
    # ...
