from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import TYPE_CHECKING, Any, TypeVar, overload

from typing_extensions import Self

from c4.contrib.structurizr._styles import (
    parse_style_metadata,
)
from c4.contrib.structurizr.workspace.elements import (
    Component,
    Container,
    ContainerInstance,
    DeploymentNode,
    InfrastructureNode,
    Person,
    Relationship,
    SoftwareSystem,
    SoftwareSystemInstance,
    StructurizrElement,
    _DeploymentInstance,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.structurizr.workspace.workspace import Workspace


_ElementT = TypeVar("_ElementT", bound=StructurizrElement)
_InstanceT = TypeVar("_InstanceT", bound=_DeploymentInstance)
_SoftwareSystem = SoftwareSystem
_Container = Container
_DeploymentNode = DeploymentNode


class DeploymentEnvironment:
    """
    A named deployment environment and its root deployment nodes.

    Attributes:
        name: Environment name.
        nodes: Root deployment nodes in the environment.
    """

    def __init__(self, model: Model, name: str) -> None:
        """
        Initialize a deployment environment.

        Args:
            model: Model that owns the environment.
            name: Environment name.
        """
        self._model = model
        self.name = name
        self.nodes: list[DeploymentNode] = []

    def __enter__(self) -> Self:
        self._model._environment_stack.append(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._model._environment_stack.pop()

    def DeploymentNode(self, name: str, **kwargs: Any) -> DeploymentNode:
        """
        Add a root deployment node to this environment.

        Args:
            name: Display name of the deployment node.
            **kwargs: Element metadata accepted by ``DeploymentNode``.
        """
        return self._model.DeploymentNode(name, environment=self.name, **kwargs)


_DeploymentEnvironment = DeploymentEnvironment


class Model:
    """
    The elements, relationships, and deployment topology of a workspace.

    Attributes:
        people: People declared in the model.
        software_systems: Software systems declared in the model.
        containers: Containers declared in the model.
        components: Components declared in the model.
        deployment_nodes: Deployment and infrastructure nodes in the model.
        deployment_environments: Named deployment environments in the model.
        _relationships: Relationships declared in the model.
    """

    def __init__(self, workspace: Workspace) -> None:
        """
        Initialize an empty model for ``workspace``.

        Args:
            workspace: Workspace that owns this model.
        """
        self._workspace = workspace
        self._aliases: set[str] = set()
        self._owner_stack: list[StructurizrElement] = []
        self._environment_stack: list[DeploymentEnvironment] = []
        self.people: list[Person] = []
        self.software_systems: list[SoftwareSystem] = []
        self.containers: list[Container] = []
        self.components: list[Component] = []
        self.deployment_nodes: list[DeploymentNode] = []
        self.software_system_instances: list[SoftwareSystemInstance] = []
        self.container_instances: list[ContainerInstance] = []
        self.deployment_environments: list[DeploymentEnvironment] = []
        self._relationships: list[Relationship] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    @property
    def relationships(self) -> list[Relationship]:
        return self._relationships

    def _pop_owner(self, element: StructurizrElement) -> None:
        """Remove ``element`` from the active ownership context."""
        if not self._owner_stack or self._owner_stack[-1] is not element:
            raise RuntimeError("Structurizr model ownership context mismatch")

        self._owner_stack.pop()

    @overload
    def _owner(
        self,
        owner: StructurizrElement | None,
        expected: type[_ElementT],
    ) -> _ElementT | None: ...  # pragma: no cover

    @overload
    def _owner(
        self,
        owner: StructurizrElement | None,
        expected: None = None,
    ) -> StructurizrElement | None: ...  # pragma: no cover

    def _owner(
        self,
        owner: StructurizrElement | None,
        expected: type[StructurizrElement] | None = None,
    ) -> StructurizrElement | None:
        """Resolve and validate an explicit or contextual element owner."""
        value = owner or (self._owner_stack[-1] if self._owner_stack else None)
        if value is not None and (
            value._model is not self
            or (expected is not None and not isinstance(value, expected))
        ):
            raise ValueError("Owner must belong to this workspace model")

        return value

    def _new(
        self,
        cls: type[_ElementT],
        name: str,
        *,
        owner: StructurizrElement | None = None,
        **kwargs: Any,
    ) -> _ElementT:
        """Create an element with its resolved owner."""
        return cls(self, name, parent=owner, **kwargs)

    def Person(self, name: str, **kwargs: Any) -> Person:
        """
        Add a person to the model.

        Args:
            name: Display name of the person.
            **kwargs: Element metadata accepted by ``Person``.
        """
        result = self._new(Person, name, **kwargs)
        self.people.append(result)
        return result

    def SoftwareSystem(self, name: str, **kwargs: Any) -> SoftwareSystem:
        """
        Add a software system to the model.

        Args:
            name: Display name of the software system.
            **kwargs: Element metadata accepted by ``SoftwareSystem``.
        """
        result = self._new(SoftwareSystem, name, **kwargs)
        self.software_systems.append(result)
        return result

    def Container(
        self, name: str, *, owner: _SoftwareSystem | None = None, **kwargs: Any
    ) -> Container:
        """
        Add a container to a software system.

        Args:
            name: Display name of the container.
            owner: Owning software system, or the active context owner.
            **kwargs: Element metadata accepted by ``Container``.
        """
        result = self._new(
            Container, name, owner=self._owner(owner, _SoftwareSystem), **kwargs
        )
        self.containers.append(result)
        return result

    def Component(
        self, name: str, *, owner: _Container | None = None, **kwargs: Any
    ) -> Component:
        """
        Add a component to a container.

        Args:
            name: Display name of the component.
            owner: Owning container, or the active context owner.
            **kwargs: Element metadata accepted by ``Component``.
        """
        result = self._new(
            Component, name, owner=self._owner(owner, _Container), **kwargs
        )
        self.components.append(result)
        return result

    def DeploymentEnvironment(self, name: str) -> DeploymentEnvironment:
        """
        Return the named deployment environment, creating it if needed.

        Args:
            name: Deployment environment name.
        """
        existing = self.get_deployment_environment(name)
        if existing is not None:
            return existing

        result = DeploymentEnvironment(self, name)
        self.deployment_environments.append(result)
        return result

    def get_deployment_environment(
        self, name: str
    ) -> _DeploymentEnvironment | None:
        """
        Return the named deployment environment, or ``None``.

        Args:
            name: Deployment environment name.
        """
        return next(
            (
                item
                for item in self.deployment_environments
                if item.name == name
            ),
            None,
        )

    def DeploymentNode(
        self,
        name: str,
        *,
        parent: _DeploymentNode | None = None,
        environment: str | None = None,
        **kwargs: Any,
    ) -> DeploymentNode:
        """
        Add a deployment node to the model or active environment.

        Args:
            name: Display name of the deployment node.
            parent: Optional parent deployment node.
            environment: Optional deployment environment name.
            **kwargs: Element metadata accepted by ``DeploymentNode``.
        """
        owner = self._owner(parent)
        env = environment or (
            self._environment_stack[-1].name
            if self._environment_stack
            else None
        )

        result = DeploymentNode(
            self, name, parent=owner, environment=env, **kwargs
        )
        self.deployment_nodes.append(result)

        if isinstance(owner, DeploymentNode):
            owner.deployment_nodes.append(result)
        elif env:
            self.DeploymentEnvironment(env).nodes.append(result)

        return result

    def InfrastructureNode(
        self, name: str, *, parent: _DeploymentNode | None = None, **kwargs: Any
    ) -> InfrastructureNode:
        """
        Add an infrastructure node below a deployment node.

        Args:
            name: Display name of the infrastructure node.
            parent: Parent deployment node, or the active context owner.
            **kwargs: Element metadata accepted by ``InfrastructureNode``.
        """
        owner = self._owner(parent, _DeploymentNode)
        result = self._new(InfrastructureNode, name, owner=owner, **kwargs)
        self.deployment_nodes.append(result)

        if owner:
            owner.infrastructure_nodes.append(result)

        return result

    def _instance(
        self,
        cls: type[_InstanceT],
        target: StructurizrElement,
        parent: _DeploymentNode | None,
        **kwargs: Any,
    ) -> _InstanceT:
        """Create a deployment instance under its validated parent node."""
        owner = self._owner(parent, _DeploymentNode)
        if owner is None:
            raise TypeError("Deployment instances require a deployment node")

        if target._model is not self:
            raise ValueError(
                "Instance target must belong to this workspace model"
            )

        result = cls(self, target, parent=owner, **kwargs)
        if isinstance(result, SoftwareSystemInstance):
            owner.software_system_instances.append(result)
        elif isinstance(result, ContainerInstance):
            owner.container_instances.append(result)
        else:  # pragma: no cover - constrained by the private factory API
            raise TypeError("Unsupported deployment instance type")

        return result

    def SoftwareSystemInstance(
        self,
        target: _SoftwareSystem,
        *,
        parent: _DeploymentNode | None = None,
        **kwargs: Any,
    ) -> SoftwareSystemInstance:
        """
        Add an instance of a software system to a deployment node.

        Args:
            target: Software system represented by the instance.
            parent: Parent deployment node, or the active context owner.
            **kwargs: Instance metadata.
        """
        if not isinstance(target, SoftwareSystem):
            raise TypeError(
                "SoftwareSystemInstance requires a SoftwareSystem target"
            )

        result = self._instance(
            SoftwareSystemInstance, target, parent, **kwargs
        )
        self.software_system_instances.append(result)

        return result

    def ContainerInstance(
        self,
        target: _Container,
        *,
        parent: _DeploymentNode | None = None,
        **kwargs: Any,
    ) -> ContainerInstance:
        """
        Add an instance of a container to a deployment node.

        Args:
            target: Container represented by the instance.
            parent: Parent deployment node, or the active context owner.
            **kwargs: Instance metadata.
        """
        if not isinstance(target, Container):
            raise TypeError("ContainerInstance requires a Container target")

        result = self._instance(ContainerInstance, target, parent, **kwargs)
        self.container_instances.append(result)

        return result

    def _relationship(
        self,
        source: StructurizrElement,
        destination: StructurizrElement,
        description: str | None,
        technology: str | None = None,
        tags: tuple[str, ...] = (),
        properties: Mapping[str, Any] | None = None,
        url: str | None = None,
        style: Mapping[str, Any] | None = None,
    ) -> Relationship:
        """Create and register a relationship between local model elements."""
        if source._model is not self or destination._model is not self:
            raise ValueError(
                "Relationship endpoints must belong to this workspace model"
            )

        result = Relationship(
            source=source,
            destination=destination,
            description=description,
            technology=technology,
            tags=tags,
            properties=dict(properties or {}),
            url=url,
            style=dict(parse_style_metadata(style)),
        )
        self._relationships.append(result)

        return result
