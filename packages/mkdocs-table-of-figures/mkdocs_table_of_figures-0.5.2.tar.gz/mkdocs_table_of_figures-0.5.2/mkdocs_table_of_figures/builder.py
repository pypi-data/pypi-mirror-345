"""
File        : mkdocs_table_of_figures/builder.py
Description : This is the builder class that will be used to build markdown content in documentation using Jinja2 templates
Author      : Thibaud Briard - BRT, <thibaud.briard@outlook.com>
"""

import os
from typing import Optional

from jinja2 import Environment, Template, FileSystemLoader

class Builder:
    SCRIPT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    CUSTOM_TEMPLATES_PATH_DEFAULT = None
    TEMPLATES_PATH_FALLBACK = os.path.join(SCRIPT_DIR_PATH, 'templates/')
    OUTPUT_TEMPLATE_FILE = 'output.md.j2'

    templates_path: str
    loader: FileSystemLoader
    env: Environment

    @property
    def output_template(self) -> Template:
        return self.env.get_template(self.OUTPUT_TEMPLATE_FILE)

    def __init__(self, templates_path: str):
        self.templates_path = templates_path
        self.loader = FileSystemLoader(self.templates_path)
        self.env = Environment(loader=self.loader)

    @classmethod
    def init_from_config(cls, custom_templates_path: Optional[str] = CUSTOM_TEMPLATES_PATH_DEFAULT) -> 'Builder':
        template_path = custom_templates_path or cls.TEMPLATES_PATH_FALLBACK

        return Builder(template_path)


    def build(self, context: dict) -> str:
        return self.output_template.render(context)
