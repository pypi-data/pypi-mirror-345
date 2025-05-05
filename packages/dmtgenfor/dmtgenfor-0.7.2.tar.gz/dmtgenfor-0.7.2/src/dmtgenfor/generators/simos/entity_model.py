
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, Set, List

from dmtgen.common.blueprint_attribute import BlueprintAttribute
from dmtgen.common.package import Blueprint
from inflection import humanize
from . import resize_model as resize
from .common import TemplateConfig, to_file_name,path_to_type_name,to_field_name,to_module_name,to_type_path
from .simos import is_destroyable,has_default_init,is_allocatable


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


types = {"number": "real(dp)", "double": "real(dp)", "float": "real(sp)", "string": "character(:)", "char": "character",
            "integer": "integer", "short": "short", "boolean": "logical"}

def create_model(blueprint: Blueprint, config: dict, template_config: TemplateConfig):
    """Create entity model from blueprint"""
    model = {}
    if config is None:
        config = {}
    attr_name = blueprint.name
    model["name"] = attr_name
    attr_name = blueprint.name
    module = to_module_name(blueprint.get_path())
    model["name"] = attr_name
    model["type"] = blueprint.name
    model["module"] = module
    model["path"] = blueprint.get_path().replace("/",":")
    model["description"] = blueprint.description
    model["file_basename"] = to_file_name(blueprint)
    # TODO: When blueprint is shared, shouldnt everything be shared?
    is_shared = blueprint.content.get("shared", False)
    model["is_shared"] = is_shared
    model["is_writable"] = blueprint.content.get("writable", False)
    attributes = []
    model["attributes"]=attributes

    all_attributes = blueprint.all_attributes
    model["has_name"] = all_attributes.get("name") is not None

    model["resize"] = resize.create_model(blueprint)
    dependencies = {}
    for attribute in blueprint.all_attributes.values():
        attributes.append(
            __to_attribute_dict(
                blueprint,
                attribute,
                dependencies,
                config,
                template_config
            ))

    # TODO REMOVE WHEN DONE
    # Move name and description to the end
    for i, attribute in enumerate(attributes):
        if attribute["name"] == "name":
            # attribute["description"] = "variable name for named accessing"
            attributes.append(attributes.pop(i))
            break
    for i, attribute in enumerate(attributes):
        if attribute["name"] == "description":
            # attribute["description"] = "instance description"
            attributes.append(attributes.pop(i))
            break

    model["dependencies"]= dependencies
    return model


def __to_attribute_dict(
        blueprint: Blueprint,
        attribute: BlueprintAttribute,
        dependencies: Dependencies,
        config: dict,
        template_config: TemplateConfig):
    atype = __to_attribute_type(blueprint,attribute, dependencies, config)

    allocatable = is_allocatable(attribute, template_config.use_is_set)
    type_init = __attribute_init(attribute, atype, allocatable)
    if len(attribute.description)==0:
        attribute.description = humanize(attribute.name)

    if attribute.is_string() and attribute.is_array():
        raise ValueError("String arrays are not supported")

    adict = {
        "name": attribute.name,
        "fieldname": to_field_name(attribute.name),
        "is_required": attribute.is_required(),
        "type" : atype,
        "is_optional" : attribute.optional,
        "is_primitive" : attribute.is_primitive(),
        "is_string" : attribute.is_string(),
        "is_array" : attribute.is_array(),
        "type_init" : type_init,
        "is_allocatable" : allocatable,
        "has_default_init" : has_default_init(attribute),
        "is_destroyable" : is_destroyable(attribute),
        "is_variable_array" : attribute.is_variable_array(),
        "description" : attribute.description,
        "is_transient": attribute.get('transient', False)
    }

    is_shared = attribute.content.get("shared", False)
    # However name is always shared if blueprint is shared
    if attribute.name == "name" and blueprint.content.get("shared", False):
        is_shared = True

    adict["is_shared"] = is_shared

    if is_destroyable(attribute):
        adict["destroy"] = __attribute_destroy(attribute)

    if attribute.is_variable_array():
        adict["dimension_names"] = __dimension_names(attribute)

    return adict

def __to_attribute_type(
        blueprint: Blueprint,
        attribute: BlueprintAttribute,
        dependencies: Dependencies,
        config: dict):
    if attribute.is_string() and config.get("use_string", True):
        return "type(String)"
    elif attribute.type in types:
        return __map(attribute.type, types)
    else:
        add_depenency(
            dependencies,
            to_module_name(attribute.type),
            ModuleImport(
                path_to_type_name(attribute.type),
                to_type_path(attribute.type)
            )
        )
        return to_type_path(attribute.type)


def __dimension_names(attribute: BlueprintAttribute):
    return __names("idx", len(attribute.dimensions))

def __names(name, ndim):
    return ", ".join([name+str(i+1) for i in range(ndim)])

def __attribute_destroy(attribute: BlueprintAttribute):
    if attribute.is_variable_array() and (attribute.is_blueprint() or attribute.is_string()):
        dims = __dimension_names(attribute)
        # FIXME: This is a hack to get the first dimension name
        dim = "idx1"
        if dim != dims:
            raise ValueError("Only one dimension is supported")
        name = attribute.name
        return f"""
        !Internal variables
        integer :: {dims}
        if (allocated(this%{name})) then
            do {dim} = 1,size(this%{name}, 1)
                call this%{name}({dim})%destroy()
            end do
            deallocate(this%{name})
        end if""".lstrip()
    if attribute.is_string() or not attribute.is_primitive():
        return f"call this%{attribute.name}%destroy()"
    else:
        return f"if (allocated(this%{attribute.name})) deallocate(this%{attribute.name})"


def __attribute_init(attribute: BlueprintAttribute, atype: str, is_allocatable: bool):
    if attribute.is_blueprint():
        atype = f"type({atype})"
    if not attribute.get("contained", True):
        atype += ", pointer"
    if attribute.is_array():
        dims = ",".join(attribute.dimensions).replace("*", ":")
        if attribute.is_variable_array():
            return f"{atype}, dimension({dims})"
        else:
            return f"{atype}, dimension({dims})"
    return atype

def __map(key, values):
    converted = values[key]
    if not converted:
        raise ValueError("Unkown type " + key)
    return converted

def __convert_default(attribute: BlueprintAttribute, default_value):
    # converts json value to fortran value
    if isinstance(default_value,str):
        if default_value == '' or default_value == '""':
            return '""'
        elif attribute.is_integer():
            return int(default_value)
        elif attribute.is_number():
            return float(default_value)
        elif attribute.is_boolean():
            conversion = {
                "false": ".false.",
                "true": ".true.",
            }
            return conversion.get(default_value, default_value)
        else:
            return "'" + default_value + "'"


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
