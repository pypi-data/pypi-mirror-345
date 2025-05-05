"""Basic generator, one template, one output file"""

import codecs
from pathlib import Path
from typing import Dict
from dmtgen import TemplateBasedGenerator
from dmtgen.package_generator import PackageGenerator
from dmtgen.common.package import Package
from jinja2 import Template
from .common import blueprint_to_module_name, package_to_module_name, to_fortran_typename

class PackageGenerator(TemplateBasedGenerator):
    """Basic generator, one template, one output file"""

    def generate(
        self,
        package_generator: PackageGenerator,
        template: Template,
        outputfile: Path,
        config: Dict,
    ):
        """Generate package modules"""
        outputdir = outputfile.parents[0]
        root_package = package_generator.root_package
        self.__generate_package_files(root_package, template, outputdir)

    def __generate_package_files(self, package: Package, template: Template, pkg_dir):
        if len(package.blueprints) > 0:
            self.__generate_package_file(package, template, pkg_dir)

        for package in package.packages:
            name = package.name
            sub_dir = pkg_dir / name
            self.__generate_package_files(package, template, sub_dir)

    def __generate_package_file(self, package: Package, template: Template, pkg_dir: Path):
        module_model = {}
        module_model["name"] = package_to_module_name(package)
        module_model["types"] = [{
            "name": to_fortran_typename(blueprint.name),
            "module": blueprint_to_module_name(blueprint)
        } for blueprint in package.blueprints]

        pkg_dir.mkdir(parents=True, exist_ok=True)
        filename = pkg_dir / (package.name + ".f90")
        # Render the template first to ensure no errors in the template
        rendered_template = template.render(module=module_model)
        render = True
        if filename.exists():
            # Check if the current generated source file is different from the rendered
            # source. If it hasn't changed we don't touch the file to avoid triggering a
            # cascade of files needing to be rebuilt for no reason.
            with open(filename) as f:
                current_content = ''.join(f.readlines())
                render = rendered_template != current_content
        if render:
            with codecs.open(filename, "w", "utf-8") as file:
                file.write(rendered_template)
