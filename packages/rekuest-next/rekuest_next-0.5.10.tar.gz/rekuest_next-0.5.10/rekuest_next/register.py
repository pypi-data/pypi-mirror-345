"""Register a function or actor with the definition registry"""

from rekuest_next.actors.sync import SyncGroup
from rekuest_next.actors.types import Actifier, ActorBuilder, OnUnprovide, OnProvide
from rekuest_next.actors.vars import is_inside_assignation
from rekuest_next.definition.hash import hash_definition
from rekuest_next.structures.registry import (
    StructureRegistry,
)
from rekuest_next.structures.default import (
    get_default_structure_registry,
)
from rekuest_next.definition.registry import (
    DefinitionRegistry,
    get_default_definition_registry,
)
from rekuest_next.api.schema import (
    AssignWidgetInput,
    DefinitionInput,
    DependencyInput,
    PortGroupInput,
    ReturnWidgetInput,
    EffectInput,
    ImplementationInput,
    ValidatorInput,
)
from typing import (
    Dict,
    List,
    Callable,
    Optional,
    Awaitable,
    Any,
    Tuple,
    TypeVar,
    Union,
    overload,
)
import inflection
from rekuest_next.actors.actify import reactify
from functools import wraps


def register_func(
    function_or_actor: Callable,
    structure_registry: StructureRegistry,
    definition_registry: DefinitionRegistry,
    interface: str = None,
    stateful: bool = False,
    name: str = None,
    actifier: Actifier = reactify,
    dependencies: List[DependencyInput] = None,
    port_groups: Optional[List[PortGroupInput]] = None,
    validators: Optional[Dict[str, List[ValidatorInput]]] = None,
    collections: List[str] = None,
    is_test_for: Optional[List[str]] = None,
    logo: Optional[str] = None,
    widgets: Dict[str, AssignWidgetInput] = None,
    effects: Dict[str, List[EffectInput]] = None,
    interfaces: List[str] = [],
    on_provide: OnProvide = None,
    on_unprovide: OnUnprovide = None,
    dynamic: bool = False,
    in_process: bool = False,
    sync: Optional[SyncGroup] = None,
    **actifier_params: Dict[str, object],
) -> Tuple[DefinitionInput, ActorBuilder]:
    """Register a function or actor with the definition registry

    Register a function or actor with the definition registry. This will
    create a definition for the function or actor and register it with the
    definition registry.

    If first parameter is a function, it will be wrapped in an actorBuilder
    through the actifier. If the first parameter is an actor, it will be
    used as the actorBuilder (needs to have the dunder __definition__) to be
    detected as such.

    Args:
        function_or_actor (Union[Actor, Callable]): _description_
        actifier (Actifier, optional): _description_. Defaults to None.
        interface (str, optional): _description_. Defaults to None.
        widgets (Dict[str, WidgetInput], optional): _description_. Defaults to {}.
        interfaces (List[str], optional): _description_. Defaults to [].
        on_provide (_type_, optional): _description_. Defaults to None.
        on_unprovide (_type_, optional): _description_. Defaults to None.
        structure_registry (StructureRegistry, optional): _description_. Defaults to None.
    """

    interface = interface or inflection.underscore(
        function_or_actor.__name__
    )  # convert this to camelcase

    definition, actor_builder = actifier(
        function_or_actor,
        structure_registry,
        on_provide=on_provide,
        on_unprovide=on_unprovide,
        widgets=widgets,
        is_test_for=is_test_for,
        collections=collections,
        logo=logo,
        name=name,
        stateful=stateful,
        port_groups=port_groups,
        effects=effects,
        sync=sync,
        validators=validators,
        interfaces=interfaces,
        in_process=in_process,
        **actifier_params,
    )

    definition_registry.register_at_interface(
        interface,
        ImplementationInput(
            interface=interface,
            definition=definition,
            dependencies=dependencies or [],
            logo=logo,
            dynamic=dynamic,
        ),
        actor_builder,
    )

    return definition, actor_builder


T = TypeVar("T")


@overload
def register(
    function_or_actor: T,
) -> T:
    """Register a function or actor to the default definition registry."""
    ...


@overload
def register(
    actifier: Actifier = reactify,
    interface: str = None,
    stateful: bool = False,
    widgets: Dict[str, AssignWidgetInput] = None,
    dependencies: List[DependencyInput] = None,
    interfaces: List[str] = [],
    collections: List[str] = None,
    port_groups: Optional[List[PortGroupInput]] = None,
    effects: Dict[str, List[EffectInput]] = None,
    is_test_for: Optional[List[str]] = None,
    logo: Optional[str] = None,
    on_provide: OnProvide = None,
    on_unprovide: OnUnprovide = None,
    validators: Optional[Dict[str, List[ValidatorInput]]] = None,
    structure_registry: StructureRegistry = None,
    definition_registry: DefinitionRegistry = None,
    in_process: bool = False,
    dynamic: bool = False,
    sync: Optional[SyncGroup] = None,
    **actifier_params: Dict[str, object],
) -> Callable[[T], T]:
    """Register a function or actor to the default definition registry.

    You can use this decorator to register a function or actor to the default
    definition registry. There is also a function version of this decorator,
    which is more convenient to use.

    Example:
        >>> @register
        >>> def hello_world(string: str):

        >>> @register(interface="hello_world")
        >>> def hello_world(string: str):



    """

    ...


def register(
    *func,
    actifier: Actifier = reactify,
    interface: str = None,
    stateful: bool = False,
    widgets: Dict[str, AssignWidgetInput] = None,
    dependencies: List[DependencyInput] = None,
    interfaces: List[str] = [],
    collections: List[str] = None,
    port_groups: Optional[List[PortGroupInput]] = None,
    effects: Dict[str, List[EffectInput]] = None,
    is_test_for: Optional[List[str]] = None,
    logo: Optional[str] = None,
    on_provide=None,
    on_unprovide=None,
    validators: Optional[Dict[str, List[ValidatorInput]]] = None,
    structure_registry: StructureRegistry = None,
    definition_registry: DefinitionRegistry = None,
    in_process: bool = False,
    dynamic: bool = False,
    sync: Optional[SyncGroup] = None,
    **actifier_params: Dict[str, object],
):
    """Register a function or actor to the default definition registry.

    You can use this decorator to register a function or actor to the default
    definition registry. There is also a function version of this decorator,
    which is more convenient to use.

    Example:
        >>> @register
        >>> def hello_world(string: str):

        >>> @register(interface="hello_world")
        >>> def hello_world(string: str):

    Args:
        function_or_actor (Union[Callable, Actor]): The function or Actor
        builder (ActorBuilder, optional): An actor builder (see ActorBuilder). Defaults to None.
        package (str, optional): The package you want to register this function in. Defaults to standard app package    .
        interface (str, optional): The name of the function. Defaults to the functions name.
        widgets (Dict[str, WidgetInput], optional): A dictionary of parameter key and a widget. Defaults to the default widgets as registered in the structure registry .
        interfaces (List[str], optional): Interfaces that this action adheres to. Defaults to [].
        on_provide (Callable[[Provision], Awaitable[dict]], optional): Function that shall be called on provide (in the async eventloop). Defaults to None.
        on_unprovide (Callable[[], Awaitable[dict]], optional): Function that shall be called on unprovide (in the async eventloop). Defaults to None.
        structure_registry (StructureRegistry, optional): The structure registry to use for this Actor (used to shrink and expand inputs). Defaults to None.
    """
    definition_registry = definition_registry or get_default_definition_registry()
    structure_registry = structure_registry or get_default_structure_registry()

    if len(func) > 1:
        raise ValueError("You can only register one function or actor at a time.")
    if len(func) == 1:
        function_or_actor = func[0]

        @wraps(function_or_actor)
        def wrapped_function(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            return function_or_actor(*args, **kwargs)

        definition, actor_builder = register_func(
            function_or_actor,
            structure_registry=structure_registry,
            definition_registry=definition_registry,
            dependencies=dependencies,
            validators=validators,
            actifier=actifier,
            stateful=stateful,
            interface=interface,
            is_test_for=is_test_for,
            widgets=widgets,
            logo=logo,
            effects=effects,
            collections=collections,
            interfaces=interfaces,
            on_provide=on_provide,
            on_unprovide=on_unprovide,
            port_groups=port_groups,
            in_process=in_process,
            dynamic=dynamic,
            sync=sync,
            **actifier_params,
        )

        wrapped_function.__definition__ = definition
        wrapped_function.__definition_hash__ = hash_definition(definition)
        wrapped_function.__actor_builder__ = actor_builder

        return wrapped_function

    else:

        def real_decorator(function_or_actor: T) -> T:
            # Simple bypass for now
            @wraps(function_or_actor)
            def wrapped_function(*args, **kwargs):  # noqa: ANN202, ANN003, ANN002
                return function_or_actor(*args, **kwargs)

            definition, actor_builder = register_func(
                function_or_actor,
                structure_registry=structure_registry,
                definition_registry=definition_registry,
                actifier=actifier,
                interface=interface,
                validators=validators,
                stateful=stateful,
                dependencies=dependencies,
                is_test_for=is_test_for,
                widgets=widgets,
                effects=effects,
                collections=collections,
                interfaces=interfaces,
                on_provide=on_provide,
                logo=logo,
                on_unprovide=on_unprovide,
                port_groups=port_groups,
                dynamic=dynamic,
                in_process=in_process,
                sync=sync,
                **actifier_params,
            )

            wrapped_function.__definition__ = definition
            wrapped_function.__definition_hash__ = hash_definition(definition)
            wrapped_function.__actor_builder__ = actor_builder

            return wrapped_function

        return real_decorator


T = TypeVar("T")


def structure(
    *cls: T,
    identifier: str = None,
    aexpand: Callable[
        [
            str,
        ],
        Awaitable[Any],
    ] = None,
    ashrink: Callable[
        [
            any,
        ],
        Awaitable[str],
    ] = None,
    convert_default: Callable[[Any], str] = None,
    default_widget: AssignWidgetInput = None,
    default_returnwidget: ReturnWidgetInput = None,
    registry: StructureRegistry = None,
    **kwargs: Dict[str, Any],
) -> T:
    """Register a global structure to the default structure registry.

    This will register the structure with the given identifier and
    the given shrink and expand functions. The identifier will be
    used to identify the structure in the registry. The shrink and
    expand functions will be used to shrink and expand the structure
    when it is passed to and from an actor.

    Args:
        cls (Structure): The structure class
        name (str, optional): The name of the structure. Defaults to the class name.
    """
    if len(cls) > 1:
        raise ValueError("You can only register one function or actor at a time.")
    if len(cls) == 1:
        function_or_actor = cls[0]

        sregistry = registry or get_default_structure_registry()

        sregistry.register_as_structure(
            function_or_actor,
            identifier=identifier,
            ashrink=ashrink or getattr(function_or_actor, "ashrink", None),
            aexpand=aexpand or getattr(function_or_actor, "aexpand", None),
            convert_default=convert_default,
            default_widget=default_widget,
            default_returnwidget=default_returnwidget,
            **kwargs,
        )

        return cls

    else:

        def real_decorator(cls):  # noqa: ANN202, ANN001
            # Simple bypass for now

            sregistry = registry or get_default_structure_registry()

            sregistry.register_as_structure(
                cls,
                identifier=identifier,
                ashrink=ashrink or getattr(cls, "ashrink", None),
                aexpand=aexpand or getattr(cls, "aexpand", None),
                convert_default=convert_default,
                default_widget=default_widget,
                default_returnwidget=default_returnwidget,
                **kwargs,
            )

            return cls

        return real_decorator


def test(
    tested_action: Union[str, Callable],
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> T:
    """Register a test for a function or actor

    It should check if the function or actor expects implementations as an input,
    and if so register the test for that implementation.

    Args:
        for (Callable): The function or actor to test
        name (Optional[str], optional): The name of the test. Defaults to None.
        description (Optional[str], optional): The description of the test. Defaults to None.
    """

    def registered_function(func: Callable) -> T:
        @wraps(func)
        def wrapped_function(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            if is_inside_assignation():
                raise NotImplementedError("You cannot run tests inside an assignation.")

            return func(*args, **kwargs)

        assert hasattr(tested_action, "__definition_hash__"), (
            "The to be tested function or actor should be registered with the register decorator. Or have a __definition__ attribute."
        )

        register(
            func,
            is_test_for=[tested_action.__definition_hash__],
            interface=name or func.__name__,
        )

        return wrapped_function

    return registered_function
