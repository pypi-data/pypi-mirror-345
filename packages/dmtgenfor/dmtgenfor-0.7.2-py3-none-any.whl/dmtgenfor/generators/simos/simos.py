
"""Contains rules adapted from the SIMOS generator"""
from dmtgen.common.blueprint_attribute import BlueprintAttribute
from dmtgen.common.package import Blueprint
from .common import has_attribute

def is_destroyable(attribute: BlueprintAttribute):
    """Check if attribute is destroyable"""
    if not attribute.contained or attribute.is_blueprint() or attribute.is_string():
        return True
    if attribute.is_array():
        return not attribute.is_fixed_array()
    return False

def has_array(bp: Blueprint):
    """Check if blueprint has an array attribute"""
    return has_attribute(bp, lambda a: a.is_array())

def has_single_string(bp: Blueprint):
    """Check if blueprint has a single string attribute"""
    return has_attribute(bp, lambda a: a.is_string() and not a.is_array())

def has_boolean_array(bp: Blueprint):
    """check if blueprint has a boolean array attribute"""
    return has_attribute(bp, lambda a: a.is_boolean() and a.is_array())

def has_boolean(bp: Blueprint):
    """Check if blueprint has a boolean attribute"""
    return has_attribute(bp, lambda a: a.is_boolean())

def has_integer_array(bp: Blueprint):
    """Check if blueprint has an integer array attribute"""
    return has_attribute(bp, lambda a: a.is_integer() and a.is_array())

def has_default_init(attribute: BlueprintAttribute):
    """Check if attribute has a default init"""
    if attribute.is_array():
        return False
    if attribute.is_blueprint():
        return attribute.contained and attribute.is_required()
    return False

def is_allocatable(attribute: BlueprintAttribute, use_is_set: bool):
    """Check if attribute is allocatable"""
    return not attribute.get("transient", False) and (attribute.is_variable_array() or (attribute.optional and not use_is_set))

def is_atomic(attribute: BlueprintAttribute):
    """Check if attribute is atomic"""
    return attribute.is_primitive()

def has_non_atomic(bp: Blueprint):
    """Check if blueprint has a non-atomic attribute"""
    return has_attribute(bp, lambda a: not is_atomic(a))

def has_non_atomic_array(bp: Blueprint):
    """Check if blueprint has a non-atomic array attribute"""
    return has_attribute(bp, lambda a: not is_atomic(a) and a.is_array())

def has_atomic_array(bp: Blueprint):
    """Check if blueprint has an atomic array attribute"""
    return has_attribute(bp, lambda a: is_atomic(a) and a.is_array())
