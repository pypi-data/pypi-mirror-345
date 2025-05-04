"""
File        : mkdocs_table_of_figures/structure/figure.py
Description : This file contains the Figure and FiguresCollection classes,
              along with a special exception thrown when
              a figure match is tempered before being processed.
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

from re import Match
from typing import Dict, Optional, Any
from jinja2 import Template

from mkdocs.structure.pages import Page

from ..translations import Translations
from .figure_type import FigureType
from .collection import Collection

class Figure:
    """
    This represents a figure with its index, page, type, match, replacement, caption, etc.
    """
    # Constants
    CAPTION_IDENTIFIER_PREFIX_DEFAULT = 'Figure '
    CAPTION_IDENTIFIER_SUFFIX_DEFAULT = ''

    TRANSLATIONS_DEFAULT = None

    ID_PREFIX_DEFAULT = '__figure_'
    CLASSES_PREFIX_DEFAULT = 'figure figure-'
    CAPTION_IDENTIFIER_DESCRIPTION_SEPARATOR_DEFAULT = ' - '
    SECTIONS_BREADCRUMB_SEPARATOR_DEFAULT = ' / '

    # Class attributes
    translations: Optional[Translations] = TRANSLATIONS_DEFAULT

    id_prefix: str = ID_PREFIX_DEFAULT
    classes_prefix: str = CLASSES_PREFIX_DEFAULT
    caption_identifier_description_separator: str = CAPTION_IDENTIFIER_DESCRIPTION_SEPARATOR_DEFAULT
    sections_breadcrumb_separator: str = SECTIONS_BREADCRUMB_SEPARATOR_DEFAULT

    # Attributes
    index: int
    figure_type: FigureType
    match: Match
    page: Page

    # Properties
    @property
    def id(self) -> str:
        return f'{self.id_prefix}{self.index}'
    
    @property
    def classes(self) -> str:
        return f'{self.classes_prefix}{self.figure_type_name}'
    
    @property
    def caption_identifier_prefix(self) -> str:
        output = self.CAPTION_IDENTIFIER_PREFIX_DEFAULT
        
        # If translation exist use it instead of default value
        if self.translations and self.translations['caption.index.prefix']:
            output = self.translations['caption.index.prefix']

        return output
    
    @property
    def caption_identifier_suffix(self) -> str:
        output = self.CAPTION_IDENTIFIER_SUFFIX_DEFAULT
        
        # If translation exist use it instead of default value
        if self.translations and self.translations['caption.index.suffix']:
            output = self.translations['caption.index.suffix']

        return output
    
    @property
    def caption_identifier(self) -> str:
        return f'{self.caption_identifier_prefix}{self.index}{self.caption_identifier_suffix}'
    
    @property
    def caption_description(self) -> str:
        return self.match_groups['caption'] or ''
    
    @property
    def caption(self) -> str:
        output = f'{self.caption_identifier}'

        # If an empty caption was provided only show identifier (without separator)
        if self.caption_description:
            output += f'{self.caption_identifier_description_separator}{self.caption_description}'
        
        return output
    
    @property
    def figure_type_name(self) -> str:
        return self.figure_type.name
    
    @property
    def figure_type_label(self) -> str:
        return self.figure_type.label
    
    @property
    def figure_type_metadata(self) -> Dict[str, Any]:
        return self.figure_type.metadata
    
    @property
    def page_uri(self) -> str:
        return f'{self.page.file.src_uri}'
    
    @property
    def page_header(self) -> str:
        output = ''

        for line in self.page.file.content_string.splitlines():
            if line.startswith("# "):
                output = line[2:].strip()
                break
        
        return output
    
    @property
    def sections_breadcrumb(self) -> str:
        output = self.page.title or self.page_header

        section = self.page.parent
        while section:
            output = f'{section.title}{self.sections_breadcrumb_separator}{output}'
            section = section.parent

        return output
    
    @property
    def uri(self) -> str:
        return f'{self.page_uri}#{self.id}'
    
    @property
    def content(self) -> str:
        return self.match.group(0)
    
    @property
    def match_start(self) -> int:
        return self.match.start()
    
    @property
    def match_end(self) -> int:
        return self.match.end()
    
    @property
    def match_groups(self) -> dict:
        return self.match.groupdict()
    
    @property
    def replacement(self) -> str:
        context = {'figure': self}
        template = Template(self.figure_type.template)

        return template.render(context)
    
    # Constructors
    def __init__(self, index: int, figure_type: FigureType, match: Match, page: Page):
        self.index = index
        self.figure_type = figure_type
        self.match = match
        self.page = page
    
    # Methods
    def __str__(self) -> str:
        f'<Figure index={self.index} type={self.figure_type_name} caption={self.caption_description}>'

class FiguresCollection(Collection[Figure]):
    """
    This is a Collection of Figure.
    """
    # Nothing change from base collection
    pass

class FigureChangedException(Exception):
    """
    Exception raised when a figure match has been tampered with before processing.
    """
    # Nothing change from base Exception
    pass
