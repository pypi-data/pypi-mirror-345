

from typing import Dict
from dmtgen.common.blueprint import Blueprint
from dmtgen.common.blueprint_attribute import BlueprintAttribute

from . import simos


def create_model(blueprint: Blueprint):
    """Create resize model from blueprint"""
    attributes = []
    for attribute in blueprint.all_attributes.values():
        if __has_resize(attribute):
            attributes.append(__create_resize_model(blueprint,attribute))

    return {
        "attributes": attributes,
    }

def __create_resize_model(blueprint: Blueprint,attribute: BlueprintAttribute) -> Dict:
    ftype = blueprint.name
    name = attribute.name
    dims = __dimension_names(attribute)

    model = {}
    model["name"] = name
    model["has_name"] = not simos.is_atomic(attribute)
    model ["dimension_names"] = dims

    res = True
    if res:
        return model

    lines = []

    init = f"""
    subroutine resize_{name}(this, {dims})
        class({ftype}) :: this
        integer,intent(in) :: {dims}
        !internal variables
        integer :: error, sv
        type(string) :: error_messages
    """
    lines.append(init)

    if not simos.is_atomic(attribute):
        lines.append("  type(String) :: name")
        for i in range(len(attribute.dimensions)):
            lines.append(f"  integer :: idx{i+1}")


    lines.append(f"""
        call this%destroy_{name}()
        if (allocated(this%{name})) deallocate(this%{name})
        allocate(this%{name}({dims}),stat=sv)
        if (sv.ne.0) then
            error=-1
            error_message = 'Error during resizing in {ftype}, error when trying to alloca&
                &te memory for {name}'
            call throw(illegal_state_exception(error_message%toChars()))
            return
        end if
    """.lstrip())


    if not simos.is_atomic(attribute):
        array_resize = f"""
        do idx1 = 1,size(this%{name}, 1)
            name = '{name}' + String("_") + to_string(idx1)
            call this%{name}(idx1)%default_init(name%toChars())
        end do
        """.rstrip()
        lines.append(array_resize)

    lines.append(f"end subroutine resize_{name}")

    body = "\n".join(lines)
    return {
        "resize": body
    }

def __has_resize(attribute: BlueprintAttribute):
    if attribute.is_primitive() and not attribute.is_string() or attribute.is_blueprint():
        return attribute.contained and attribute.is_array() and attribute.is_variable_array()
    return False

def __dimension_names(attribute: BlueprintAttribute):
    return __names("n", len(attribute.dimensions))

def __names(name, ndim):
    return ", ".join([name+str(i) for i in range(ndim)])
