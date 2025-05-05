# from inflection import underscore
from dataclasses import dataclass
from typing import Callable
from dmtgen.common.blueprint import Blueprint
from dmtgen.common.blueprint_attribute import BlueprintAttribute
from dmtgen.common.package import Package

@dataclass
class TemplateConfig:
    user_defined_code: bool
    generate_resize: bool
    generate_default_init: bool
    generate_allocate: bool
    generate_destroy: bool
    use_is_set: bool

def to_file_name(blueprint: Blueprint) -> str:
    """Convert blueprint name to source file name"""
    return blueprint.name + '.F90'

def to_type_name(blueprint: Blueprint) -> str:
    """Convert blueprint name to type name"""
     #TODO return underscore(name)+"_t"
    return blueprint.name

def path_to_type_name(path: str) -> str:
    return path.split('/')[-1]

def to_field_name(name: str) -> str:
    """Convert attribute name to field name"""
    #TODO: return underscore(name)
    return name

def to_type_path(path: str) -> str:
    """Convert to unverscored name"""
    return path.replace("/","_")

def to_module_name(path: str) -> str:
    """Convert to module name"""
    #TODO return underscore(blueprint.name)+"_mod"
    path=to_type_path(path)
    return f"class_{path}"

def has_attribute(bp: Blueprint, test: Callable[[BlueprintAttribute], bool]):
    """Check if blueprint has a attribute that passes the test"""
    for attribute in bp.all_attributes.values():
        if test(attribute):
            return True
    return False

def to_package_module_name(package: Package) -> str:
    """Convert Package to module name"""
    if package.parent:
        return to_package_module_name(package.parent) + '_' + package.name
    else:
        return package.name
