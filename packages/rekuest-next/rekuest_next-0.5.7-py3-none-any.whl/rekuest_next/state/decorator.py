"""Decorator to register a class as a state."""

from dataclasses import dataclass
from rekuest_next.state.predicate import get_state_name, is_state
from typing import Optional, Type, TypeVar, Callable, overload
from typing import Dict, Any
import inspect
from fieldz import fields
from rekuest_next.structures.registry import (
    StructureRegistry,
)

from rekuest_next.state.registry import (
    StateRegistry,
    get_default_state_registry,
)
from rekuest_next.api.schema import StateSchemaInput
from rekuest_next.structures.default import get_default_structure_registry

T = TypeVar("T")


def inspect_state_schema(
    cls: Type[T], structure_registry: StructureRegistry
) -> Optional[StateSchemaInput]:
    """Inspect the state schema of a class."""
    from rekuest_next.definition.define import convert_object_to_port

    ports = []

    for field in fields(cls):
        port = convert_object_to_port(field.type, field.name, structure_registry)
        ports.append(port)

    return StateSchemaInput(ports=ports, name=cls.__rekuest_state__)


@overload
def state(
    function_or_actor: T,
) -> T: ...


@overload
def state(
    name: Optional[str] = None,
    local_only: bool = False,
    registry: Optional[StateRegistry] = None,
    structure_reg: Optional[StructureRegistry] = None,
) -> Callable[[T], T]: ...


def state(
    *name_or_function: Type[T],
    local_only: bool = False,
    name: Optional[str] = None,
    registry: Optional[StateRegistry] = None,
    structure_reg: Optional[StructureRegistry] = None,
) -> Callable[[Type[T]], Type[T]]:
    """Decorator to register a class as a state.

    Args:
        name_or_function (Type[T]): The class to register
        local_only (bool): If True, the state will only be available locally.
        name (Optional[str]): The name of the state. If None, the class name will be used.
        registry (Optional[StateRegistry]): The state registry to use. If None, the current state registry will be used.
        structure_reg (Optional[StructureRegistry]): The structure registry to use. If None, the default structure registry will be used.


    Returns:
        Callable[[Type[T]], Type[T]]: The decorator function.


    """
    registry = registry or get_default_state_registry()
    structure_registry = structure_reg or get_default_structure_registry()

    if len(name_or_function) == 1:
        cls = name_or_function[0]
        return state(name=cls.__name__)(cls)

    if len(name_or_function) == 0:

        def wrapper(cls: Type[T]) -> Type[T]:
            try:
                fields(cls)
            except TypeError:
                cls = dataclass(cls)

            setattr(cls, "__rekuest_state__", name)
            setattr(cls, "__rekuest_state_local__", local_only)

            state_schema = inspect_state_schema(cls, structure_registry)

            registry.register_at_name(name, state_schema, structure_registry)

            return cls

        return wrapper


def prepare_state_variables(function: Callable) -> Dict[str, Any]:
    """Prepare the state variables for the function.

    Args:
        function (Callable): The function to prepare the state variables for.

    Returns:
        Dict[str, Any]: The state variables for the function.
    """
    sig = inspect.signature(function)
    parameters = sig.parameters

    state_variables = {}
    state_returns = {}

    for key, value in parameters.items():
        if is_state(value.annotation):
            state_variables[key] = get_state_name(value.annotation)

    returns = sig.return_annotation

    if hasattr(returns, "_name"):
        if returns._name == "Tuple":
            for index, cls in enumerate(returns.__args__):
                if is_state(cls):
                    state_returns[index] = get_state_name(value)
        else:
            if is_state(returns):
                state_returns[0] = get_state_name(value)

    return state_variables, state_returns
