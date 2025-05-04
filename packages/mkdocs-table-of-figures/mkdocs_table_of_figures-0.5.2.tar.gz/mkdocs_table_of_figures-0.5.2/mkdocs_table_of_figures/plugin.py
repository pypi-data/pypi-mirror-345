"""
File        : table_of_figures/plugin.py
Description : This is the mkdocs plugin that interface with mkdocs
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

import os
import re

from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page as MkDocsPage
from mkdocs.structure.files import Files as MkDocsFiles, File as MkDocsFile
from mkdocs.structure.nav import Section as MkDocsSection, Link as MkDocsLink

from .constants import MKDOCS_ENTRYPOINT

from .structure.directive import Directive, DirectivesCollection
from .structure.figure_type import FigureType, FigureTypes
from .structure.figure import Figure, FiguresCollection, FigureChangedException
from .translations import Translations

from .builder import Builder
from .config import TableOfFiguresConfig as PluginConfig

class TableOfFiguresPlugin(BasePlugin[PluginConfig]):
    PLUGIN_ENTRYPOINT = MKDOCS_ENTRYPOINT
    STYLES_DIRECTORY = 'assets/stylesheets/figures/'

    def __init__(self):
        self.logger = get_plugin_logger(__name__)

        self.config_dir = None
        self.custom_templates_dir = None
        self.translations_overrides_file = None

        self.builder = None

        self.translations = None
        
        self.figure_types = None
        self.figure_extra_css = None

        self.directives = None
        self.figures = None

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        self.logger.debug(self.config)

        # Retrieve user customs files and directories
        self.config_dir = os.path.dirname(config.config_file_path)
        if self.config.custom_templates_path:
            self.custom_templates_dir = os.path.normpath(os.path.join(self.config_dir, self.config.custom_templates_path))
        if self.config.translations_overrides_path:
            self.translations_overrides_file = os.path.normpath(os.path.join(self.config_dir, self.config.translations_overrides_path))

        # Set template builder with pottential user templates
        self.builder = Builder.init_from_config(self.custom_templates_dir)
        # Set translations according to theme language and pottential user overrides
        self.translations = Translations.init_from_config(config.theme.get('language') or config.theme.get('local') or 'none', self.config.translations_overrides_path)

        # Set Calsses attributes according to mkdocs config
        Directive.identifier = self.config.directive_identifier
        FigureType.translations = self.translations
        Figure.translations = self.translations
        Figure.caption_identifier_description_separator = self.config.caption_identifier_description_separator
        Figure.sections_breadcrumb_separator = self.config.sections_breadcrumb_separator

        # Retrieve figure types from figure type subconfig
        self.figure_types = FigureTypes.init_from_config(self.config.figure_types)
        self.logger.debug(f'Figures types [{self.figure_types.size}]: {self.figure_types.names}')

        # Initialize figure_extra_css list
        self.figure_extra_css = []

        # Collect existing CSS files based on enabled figure types
        for figure_type in self.figure_types:
            figure_css = os.path.join(self.STYLES_DIRECTORY, f'{figure_type.name}.css')
            if os.path.isfile(os.path.join(os.path.dirname(__file__), figure_css)):
                self.figure_extra_css.append(figure_css)

        # Prepend these existing CSS files to config['extra_css']
        # This ensure plugin CSS rules can be overriden by user CSS rules
        config['extra_css'] = self.figure_extra_css + config.get('extra_css', [])

        # Set
        self.directives = DirectivesCollection()
        self.figures = FiguresCollection()

        return config
    
    def on_nav(self, nav, config: MkDocsConfig, files: MkDocsFiles):
        def process_nav_item(item: MkDocsSection|MkDocsPage|MkDocsLink):
            if isinstance(item, MkDocsSection) and hasattr(item, 'children') and item.children:
                # It's a Section
                self.logger.debug(f'Processing childs of nav item (section): {item}')
                for child in item.children:
                    process_nav_item(child)
            elif isinstance(item, MkDocsPage) and hasattr(item, 'file') and item.file:
                # It's a Page
                self.logger.debug(f'Processing nav item (page): {item}')
                process_page(item)
            else:
                self.logger.debug(f'Skipping nav item: {item}')
        
        def process_page(page: MkDocsPage):
            def check_for_overlapsing_matches(existing_matches, target_match):
                """
                Check if the target match overlaps with existing matches.
                It prevent overlapsing figures that have similar pattern.
                """
                return any(existing_match.start() < target_match.end() and target_match.start() < existing_match.end() for _, existing_match, _ in existing_matches)
            
            matches = []

            # Add matches for each type of figure and order them by appearance
            for figure_type in self.figure_types:
                for match in re.finditer(figure_type.pattern, page.file.content_string):
                    if not check_for_overlapsing_matches(matches, match):
                        self.logger.debug(f'Found matching figure "{figure_type.name}" at [{match.start()}:{match.end()}]')
                        matches.append((match.start(), match, figure_type))
                    else:
                        self.logger.debug(f'Found an overlapsing matching figure "{figure_type.name}" at [{match.start()}:{match.end()}], It will be ignored')
            matches.sort(key=lambda x: x[0])

            # Loop trough each match and create a Figure entry (also saving match for futur replacement)
            for _, match, figure_type in matches:
                # Create new Figure entry to collection 
                new_figure = Figure(self.figures.size + 1, figure_type, match, page)
                self.figures.append(new_figure)
                self.logger.debug(f'New figure added to collection: {new_figure.page_uri}[{new_figure.match_start}:{new_figure.match_end}] - {new_figure.figure_type_name} "{new_figure.caption_description}"')

        for item in nav.items:
            process_nav_item(item)

    def on_files(self, files: MkDocsFiles, config: MkDocsConfig):
        # Add plugin styles to MkDocs files collection
        for css_file in self.figure_extra_css:
            file = MkDocsFile(path=css_file, src_dir=os.path.dirname(__file__), dest_dir=config['site_dir'], use_directory_urls=config['use_directory_urls'])
            # Mark file as generated by this plugin
            file.generated_by = self.PLUGIN_ENTRYPOINT
            files.append(file)

        return files
    
    def on_page_markdown(self, markdown: str, page: MkDocsPage, config: MkDocsConfig, files: MkDocsFiles) -> str | None:
        file_uri = page.file.src_uri
        offset = 0

        checkpoint_markdown = markdown
        try:
            # Adding figure to 
            for figure in self.figures:
                # Apply replacement process for each Figure on page
                if figure.page.file.src_uri == file_uri:
                    # Check that figure content in markdown content haven't been tempered with
                    if figure.content != markdown[figure.match_start + offset:figure.match_end + offset]:
                        raise FigureChangedException(f'The figure ({figure.index}) in {page} as been tempered with. modification to this page be ignored')

                    self.logger.debug(f'Replacing figure [{figure.index}]:')
                    [self.logger.debug(f'| - {line}') for line in figure.content.splitlines()]
                    [self.logger.debug(f'| + {line}') for line in figure.replacement.splitlines()]

                    markdown = markdown[:figure.match_start + offset] + figure.replacement + markdown[figure.match_end + offset:]
                    offset += len(figure.replacement) - len(figure.content)
        except FigureChangedException as error:
            # Reset modification in case of error
            markdown = checkpoint_markdown
            offset = 0
            self.logger.warning(error)

        self.logger.debug(f'Adding table of figures for each directive found')
        self.directives.appends_from_markdown(page, markdown)

        for directive in self.directives.filter_by_page(page):
            replacement = self.builder.build({'figures': self.figures, 'directive': directive, 'translations': self.translations, 'config': config})
            
            self.logger.debug(f'Placing table of figures:')
            self.logger.debug(f'| - {markdown[directive.context.start:directive.context.end]}')
            [self.logger.debug(f'| + {line}') for line in replacement.splitlines()]

            markdown = markdown[:directive.context.start] + replacement + markdown[directive.context.end:]
            offset += len(replacement) - (directive.context.end - directive.context.start)

        return markdown
