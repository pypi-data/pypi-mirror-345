"""Basic generator, one template, one output file"""

import codecs
from pathlib import Path
from typing import Dict
from dmtgen import TemplateBasedGenerator
from dmtgen.package_generator import PackageGenerator
from dmtgen.common.package import Package
from dmtgen.common.blueprint import Blueprint
from jinja2 import Template
from .entity_model import create_model
from .common import to_file_name, to_package_module_name


class SimosSourcelistGenerator(TemplateBasedGenerator):
    """Basic generator, one template, one output file"""

    def generate(
        self,
        package_generator: PackageGenerator,
        template: Template,
        outputfile: Path,
        config: Dict,
    ):
        """Generate library source list"""
        outputdir = outputfile.parents[0] / "cmake"
        outputdir.mkdir(parents=True, exist_ok=True)
        root_package = package_generator.root_package
        sources = get_package_source_files(root_package, Path("."))
        filename = outputdir / "sources.cmake"
        # Render the template first to ensure no errors in the template
        rendered_template = template.render(sources=sources)
        render = True
        if filename.exists():
            # Check if the current generated source file is different from the rendered
            # source. If it hasn't changed we don't touch the file to avoid triggering a
            # CMake reconfiguration for no reason.
            with open(filename) as f:
                current_content = ''.join(f.readlines())
                render = rendered_template != current_content
        if render:
            with codecs.open(filename, "w", "utf-8") as file:
                file.write(rendered_template)


def get_package_source_files(package: Package, path: Path) -> list[str]:
    sources = []
    # Source files for types
    for blueprint in package.blueprints:
        sources.append(str(path / to_file_name(blueprint)))
    # Package module, if any
    if len(package.blueprints) > 0:
        sources.append(str(path / (to_package_module_name(package) + '.f90')))
    # Sources for subpackages
    for subpackage in package.packages:
        sources.extend(get_package_source_files(subpackage, path / Path(subpackage.name)))
    source_files = []
    for source in sources:
        source_files.append(source.replace('\\', '/'))
    return source_files
