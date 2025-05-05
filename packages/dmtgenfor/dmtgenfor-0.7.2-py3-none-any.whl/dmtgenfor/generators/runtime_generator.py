#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Code generator for fortran runtime library
'''

import shutil
from pathlib import Path
from typing import Dict

from dmtgen import BaseGenerator, TemplateBasedGenerator, NoneGenerator

from .simos.simos_entity_generator import SimosEntityGenerator
from .simos.simos_package_generator import SimosPackageGenerator
from .simos.simos_sourcelist_generator import SimosSourcelistGenerator
from .dmt.type_generator import TypeGenerator
from .dmt.package_generator import PackageGenerator


class RuntimeGenerator(BaseGenerator):
    """ Generates a fortran runtime library to access the entities as plain objects """

    # @override
    def get_template_generator(self, template: Path, config: Dict) -> TemplateBasedGenerator:
        """ Override in subclasses """
        if config.get("simos", False):
            # Only generate simos entities
            if template.name == "simos.F90.jinja":
                return SimosEntityGenerator()
            elif template.name == "simos_package.F90.jinja":
                return SimosPackageGenerator()
            elif template.name == "simos_sources.cmake.jinja":
                return SimosSourcelistGenerator()
            return NoneGenerator()
        else:
            if template.name.startswith("simos"):
                # Skip simos templates
                return NoneGenerator()
            if template.name == "type.f90.jinja":
                return TypeGenerator(config)
            if template.name == "package.f90.jinja":
                return PackageGenerator()
            raise RuntimeError(f'Unhandled template: {template.name}')

    def copy_templates(self, template_root: Path, output_dir: Path):
        """Copy template folder to output folder"""
        shutil.copytree(str(template_root), str(output_dir),  dirs_exist_ok=True)
