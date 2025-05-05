"""Basic generator, one template, one output file"""
import sys
import codecs
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set
from dmtgen import TemplateBasedGenerator
from dmtgen.package_generator import PackageGenerator
from dmtgen.common.package import Package
from dmtgen.common.blueprint import Blueprint
from dmtgen.common.blueprint_attribute import BlueprintAttribute
from jinja2 import Template
from .common import attribute_to_module_name, blueprint_to_module_name, package_to_module_name, to_fortran_typename, to_fortran_filename

@dataclass(eq = True, frozen = True)
class ModuleImport:
    '''Description of the import of a symbol from a module, optionally with a local alias'''
    name: str
    rename: str | None

@dataclass
class ModuleDependency:
    '''Dependencies to symbols exported from the same module'''
    imports: Set[ModuleImport] = field(default_factory=set)

Dependencies = Dict[str, ModuleDependency]
'''Collection of modules the generated code depends on'''


@dataclass
class Attribute:
    name: str
    description: List[str]
    bare_type: str
    type_decl: str
    primitive: bool
    allocatable: bool
    shape: List[str]
    shared: bool

    @property
    def rank(self):
        return len(self.shape)


@dataclass
class Type:
    blueprint_path: str
    description: List[str]
    attributes: List[Attribute]
    shared: bool
    writable: bool

    @property
    def name(self) -> str:
        return to_fortran_typename(self.blueprint_path.split('/')[-1])

    @property
    def qualified_name(self) -> str:
        # Note that this does not use the Fortran naming convention (snake case + _t)
        # like .name
        return self.blueprint_path.replace('/', ':')


@dataclass
class Module:
    name: str
    type: Type
    dependencies: Dependencies


class TypeGenerator(TemplateBasedGenerator):
    """Basic generator, one template, one output file"""
    def __init__(self, config: Dict[str, Any]):
        # TODO: string type configurability from config?
        self.__type_mapping = {
            "number": "real(real64)",
            "double": "real(real64)",
            "float": "real(sp)",
            "string": "type(string_t)",
            "char": "character",
            "integer": "integer",
            "short": "short",
            "boolean": "logical"
        }

    def generate(
            self,
            package_generator: PackageGenerator,
            template: Template,
            outputfile: Path,
            config: Dict):
        """Generate blueprint class"""
        outputdir = outputfile.parents[0]
        root_package = package_generator.root_package
        self.__generate_package(root_package, template, outputdir)

    def __generate_package(
            self,
            package: Package,
            template,
            pkg_dir):
        for blueprint in package.blueprints:
            self.__generate_entity(blueprint, package, template, pkg_dir)

        for package in package.packages:
            name = package.name
            sub_dir = pkg_dir / name
            self.__generate_package(package, template, sub_dir)

    def __generate_entity(
            self,
            blueprint: Blueprint,
            package: Package,
            template: Template,
            outputdir: Path):
        deps: Dependencies = dict()
        typ = Type(
            blueprint_path = blueprint.get_path(),
            description = [blueprint.description],
            attributes = [],
            shared = blueprint.content.get("shared", False),
            writable = blueprint.content.get("writable", False)
        )
        for attr in blueprint.all_attributes.values():
            typ.attributes.append(Attribute(
                name = attr.name,
                description = [attr.description],
                bare_type = attr.type,
                type_decl = to_type_decl(attr, self.__type_mapping, deps),
                primitive = attr.is_primitive() and attr.type != 'string',
                allocatable = attr.is_optional() or attr.is_variable_array(),
                shape = to_shape(attr.dimensions),
                shared = attr.content.get("shared", False),
            ))

        # TODO: If it is ever needed, we can traverse the dependencies list here to
        #       look for name clashes. These can be resolved by introducing renames
        #       which is already supported by the template.

        module = Module(blueprint_to_module_name(blueprint), typ, deps)
        # Render the template first to ensure no errors in the template
        rendered_template = template.render(module=module)
        outputdir.mkdir(parents=True, exist_ok=True)
        filename = outputdir / to_fortran_filename(blueprint.name)
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

def to_type_decl(
        attr: BlueprintAttribute,
        type_mapping: Dict[str, str],
        dependencies: Dependencies) -> str:
    if attr.is_primitive():
        return type_mapping[attr.type]
    else:
        typename = to_fortran_typename(attr.type.split('/')[-1])
        add_depenency(
            dependencies,
            attribute_to_module_name(attr),
            ModuleImport(
                typename,
                None
            )
        )
        return f'type({typename})'

def to_shape(dimensions: List[str]) -> List[str]:
    return [comp.replace('*', ':') for comp in dimensions]

def add_depenency(
        dependencies: Dependencies,
        module: str,
        module_import: ModuleImport):
    '''
    Add a module import statement to the list of dependencies
    '''
    if module not in dependencies:
        dependencies[module] = ModuleDependency()
    dependencies[module].imports.add(module_import)
