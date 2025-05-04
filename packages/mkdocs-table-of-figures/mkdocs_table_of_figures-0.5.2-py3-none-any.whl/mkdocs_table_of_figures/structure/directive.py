"""
File        : mkdocs_table_of_figures/structure/directive.py
Description : This file contains the Directive and DirectivesCollection classes,
              and a custom decorator to define class-level property.
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

import re
from typing import List

from mkdocs.structure.pages import Page as MkDocsPage

from ..constants import MKDOCS_ENTRYPOINT
from .collection import Collection

class classproperty(property):
    """
    Custom decorator to define a class-level property.
    """
    def __get__(self, obj, cls):
        return self.fget(cls)

class Directive:
    """
    A directive block detected in the Markdown content.
    """
    PATTERN_OPENING = r'<!--\s*?'
    PATTERN_CLOSING = r'\s*?-->'

    identifier: str = MKDOCS_ENTRYPOINT

    @classproperty
    def pattern(cls) -> str:
        return rf'{cls.PATTERN_OPENING}(?P<identifier>{cls.identifier})(?:\s*?(?P<options>\[.*?\]))?{cls.PATTERN_CLOSING}'

    options: 'DirectiveOptions'
    context: 'DirectiveContext'

    def __init__(self, options: 'DirectiveOptions', context: 'DirectiveContext'):
        self.options = options
        self.context = context
    
    @classmethod
    def init_from_match(cls, page: MkDocsPage, match: re.Match) -> 'Directive':
        options = DirectiveOptions()
        context = DirectiveContext(page, match)

        return cls(options, context)

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} options={self.options} context={self.context}>'

class DirectiveOptions:
    """
    Class for options users may provide to customize rendering.
    """
    # TODO Provides options for users to customize the rendering
    def __init__(self):
        pass

class DirectiveContext:
    """
    Contextual information about where the directive appears in the page.
    """
    # Constants
    # ...

    # Attributes
    page: MkDocsPage
    match: re.Match

    # Properties
    @property
    def page_content(self) -> str:
        return self.page.file.content_string
    
    @property
    def page_content_before(self) -> str:
        return self.page_content[:self.start]
    
    @property
    def page_lines_before(self) -> List[str]:
        return self.page_content_before.splitlines()
    
    @property
    def page_content_after(self) -> str:
        return self.page_content[self.end:]
    
    @property
    def page_lines_after(self) -> List[str]:
        return self.page_content_after.splitlines()
    
    @property
    def span(self) -> tuple[int, int]:
        return self.match.span()

    @property
    def start(self) -> int:
        return self.match.start()
    
    @property
    def end(self) -> int:
        return self.match.end()

    @property
    def start_line(self) -> int:
        # Count number of line breaks before the end index
        return 1 + self.page_content[:self.start].count('\n')
    
    @property
    def start_column(self) -> int:
        # Column are counted from the last \n before the match
        return self.start - self.page_content[:self.start].rfind('\n')
    
    @property
    def end_line(self) -> int:
        # Count number of line breaks before the end index
        return 1 + self.page_content[:self.end].count('\n')

    @property
    def end_column(self) -> int:
        # Column is offset from the last newline before the end index
        return self.end - self.page_content[:self.end].rfind('\n')
    
    @property
    def match_index(self) -> int:
        return len(list(re.finditer(Directive.pattern, self.page_content_before)))
    
    @property
    def current_heading_level(self) -> int:
        value = 0

        for line in reversed(self.page_lines_before):
            stripped = line.strip()
            if stripped.startswith("#"):
                match_heading = re.match(r'^(#+)\s+', stripped)
                if match_heading:
                    value = len(match_heading.group(1))
        
        return value
    
    # Constructors
    def __init__(self, page: MkDocsPage, match: re.Match):
        self.page = page
        self.match = match

    # Methods

class DirectivesCollection(Collection[Directive]):
    """
    A collection of Directive objects with helpers to extract and filter them.
    """
    # Constants, Attributes, Properties, Constructors
    # ...

    # Methods
    def appends_from_markdown(self, page: MkDocsPage, markdown: str):
        for match in re.finditer(Directive.pattern, markdown):
            self.append(Directive.init_from_match(page, match))

    def filter_by_page(self, target_page: MkDocsPage) -> 'DirectivesCollection':
        filtered = DirectivesCollection()
        for directive in self:
            if directive.context.page == target_page:
                filtered.append(directive)
        return filtered
