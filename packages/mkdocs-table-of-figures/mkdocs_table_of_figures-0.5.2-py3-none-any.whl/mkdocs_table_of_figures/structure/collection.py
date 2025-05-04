"""
File        : mkdocs_table_of_figures/structure/collection.py
Description : This file contains the base class Collection
              used by FiguresCollection, FigureTypesCollection and DirectivesCollection.
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

from typing import List, Iterator, Optional, TypeVar, Generic

T = TypeVar('T')

class Collection(Generic[T]):
    """
    A generic base class representing a list-like collection of objects of the same type.
    """
    # Constants
    ITEMS_DEFAULT = []

    ITEMS_STR_PREVIEW_NUMBER = 3
    ITEMS_STR_PREVIEW_SEPARATOR = ', '
    ITEMS_STR_PREVIEW_MORE = '...'

    # Attributes
    items: List[T]

    # Properties
    @property
    def size(self) -> int:
        return len(self.items)
    
    @property
    def _items_str_preview(self) -> str:
        output = self.ITEMS_STR_PREVIEW_SEPARATOR.join(repr(item) for item in self.items[:3])

        # Only output the first few items, adding suspension if there are more
        if self.size > self.ITEMS_STR_PREVIEW_NUMBER:
            output += f'{self.ITEMS_STR_PREVIEW_SEPARATOR}{self.ITEMS_STR_PREVIEW_MORE}'
        
        return output

    # Constructors
    def __init__(self, items: Optional[List[T]] = None):
        self.items = items if items is not None else list(self.ITEMS_DEFAULT) # Ensure creation of a copy of default list

    # Methods
    def __iter__(self) -> Iterator[T]:
        return iter(self.items)
    
    def __getitem__(self, index: int) -> T:
        return self.items[index]
    
    def __str__(self) -> str:
        return f'<{self.__class__.__name__} size={self.size} items=[{self._items_str_preview}]>'

    def append(self, item: T):
        self.items.append(item)
