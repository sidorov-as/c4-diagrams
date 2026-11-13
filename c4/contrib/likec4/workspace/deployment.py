from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import TracebackType
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from c4.contrib.likec4._identifiers import check_identifier
from c4.contrib.likec4._metadata import (
    Link,
    MetadataValue,
    normalize_likec4_tags,
    normalize_links,
    normalize_metadata,
)
from c4.contrib.likec4._styles import (
    StyleValue,
    parse_element_style,
    parse_relationship_style,
)
from c4.contrib.likec4.workspace.elements import (
    Element,
    _RelationOperators,
    _set_title,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.likec4.workspace.project import Project


class DeploymentNode(_RelationOperators):
    """
    A deployment node of a declared deployment kind; nodes nest without limit.

    Nodes have their own FQN namespace, independent of the logical model.

    Attributes:
        kind: Declared deployment node kind.
        title: Display title.
        alias: Explicit identifier; derived from the title when omitted.
        parent: Parent node, or ``None`` for a root node.
        children: Child nodes in declaration order.
        instances: Instances held directly by this node.
        description: Markdown description.
        technology: Implementation technology.
        tags: Tags applied to the node, without ``#``.
        style: Node-local style properties.
        metadata: Custom metadata.
        links: Hyperlinks.
    """

    def __init__(
        self,
        deployment: Deployment,
        kind: str,
        title: str | None = None,
        *,
        alias: str | None = None,
        parent: DeploymentNode | None = None,
        description: str | None = None,
        technology: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        metadata: Mapping[str, Any] | None = None,
        links: list[Any] | tuple[Any, ...] | None = None,
        **style: Any,
    ) -> None:
        """
        Initialize a node; prefer ``Deployment.node``.

        Args:
            deployment: Deployment that owns the node.
            kind: Declared deployment node kind.
            title: Display title.
            alias: Explicit identifier.
            parent: Parent node.
            description: Markdown description.
            technology: Implementation technology.
            tags: Tags applied to the node, without ``#``.
            metadata: Custom metadata.
            links: Hyperlinks.
            **style: Node-local style properties.
        """
        if title is None and alias is None:
            raise ValueError("A deployment node needs a title or an alias.")

        if alias is not None:
            check_identifier(alias, "Deployment node alias")

        self._deployment: Deployment = deployment
        if parent is not None and parent._deployment is not deployment:
            raise ValueError("The parent node belongs to another deployment.")

        self.kind = check_identifier(kind, "Deployment node kind")
        self.title = title
        self.alias = alias
        self.parent = parent
        self.children: list[DeploymentNode] = []
        self.instances: list[DeploymentInstance] = []
        self.description = description
        self.technology = technology
        self.tags = normalize_likec4_tags(tags)
        self.style: dict[str, StyleValue] = parse_element_style(**style)
        self.metadata = normalize_metadata(metadata)
        self.links = normalize_links(links)

    def __repr__(self) -> str:
        return f"DeploymentNode({self.kind!r}, {self.title or self.alias!r})"

    def __enter__(self) -> Self:
        self._deployment._owner_stack.append(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._deployment._pop_owner(self)

    @property
    def name(self) -> str:
        """Return the title, or the alias when there is no title."""
        return self.title or self.alias or ""

    def node(
        self, kind: str, title: str | None = None, **kwargs: Any
    ) -> DeploymentNode:
        """
        Create a child node.

        Args:
            kind: Declared deployment node kind.
            title: Display title.
            **kwargs: Any other ``Deployment.node`` argument.
        """
        return self._deployment.node(kind, title, parent=self, **kwargs)

    def instance(
        self, element: Element, name: str | None = None, **kwargs: Any
    ) -> DeploymentInstance:
        """
        Add an instance of a model element to this node.

        Args:
            element: Model element to instantiate.
            name: Optional instance identifier.
            **kwargs: Any other ``Deployment.instance`` argument.
        """
        return self._deployment.instance(element, name, parent=self, **kwargs)

    def _relate(
        self,
        target: DeploymentNode | DeploymentInstance,
        title: str | None,
        **kwargs: Any,
    ) -> DeploymentRelationship:
        return self._deployment.relate(self, target, title, **kwargs)

    def ancestors(self) -> list[DeploymentNode]:
        """Return the parents from the nearest to the root."""
        result: list[DeploymentNode] = []
        node = self.parent

        while node is not None:
            result.append(node)
            node = node.parent

        return result

    def descendants(self) -> list[DeploymentNode]:
        """Return all nested nodes in depth-first declaration order."""
        result: list[DeploymentNode] = []

        for child in self.children:
            result.append(child)
            result.extend(child.descendants())

        return result


class DeploymentInstance(_RelationOperators):
    """
    An instance of a model element deployed on a node.

    Attributes:
        element: Instantiated model element.
        alias: Instance identifier, or ``None`` for an anonymous instance.
        parent: Node holding the instance.
        title: Optional title override.
        description: Markdown description.
        technology: Implementation technology.
        tags: Tags added to the element's own tags, without ``#``.
        style: Instance-local style properties.
        metadata: Custom metadata.
        links: Hyperlinks.
    """

    def __init__(
        self,
        deployment: Deployment,
        element: Element,
        name: str | None = None,
        *,
        parent: DeploymentNode,
        title: str | None = None,
        description: str | None = None,
        technology: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        metadata: Mapping[str, Any] | None = None,
        links: list[Any] | tuple[Any, ...] | None = None,
        **style: Any,
    ) -> None:
        """
        Initialize an instance; prefer ``DeploymentNode.instance``.

        Args:
            deployment: Deployment that owns the instance.
            element: Model element to instantiate.
            name: Optional instance identifier.
            parent: Node that holds the instance.
            title: Optional title override.
            description: Markdown description.
            technology: Implementation technology.
            tags: Tags added to the element's own tags, without ``#``.
            metadata: Custom metadata.
            links: Hyperlinks.
            **style: Instance-local style properties.
        """
        if not isinstance(element, Element):
            raise TypeError("An instance must reference a model Element.")

        if name is not None:
            check_identifier(name, "Instance name")

        self._deployment: Deployment = deployment
        if parent._deployment is not deployment:
            raise ValueError("The parent node belongs to another deployment.")

        self.element = element
        self.alias = name
        self.parent = parent
        self.title = title
        self.description = description
        self.technology = technology
        self.tags = normalize_likec4_tags(tags)
        self.style: dict[str, StyleValue] = parse_element_style(**style)
        self.metadata = normalize_metadata(metadata)
        self.links = normalize_links(links)

    def __repr__(self) -> str:
        return f"DeploymentInstance({self.alias or self.element.name!r})"

    @property
    def name(self) -> str:
        """Return the instance name, or the instantiated element's name."""
        return self.alias or self.element.name

    def _relate(
        self,
        target: DeploymentNode | DeploymentInstance,
        title: str | None,
        **kwargs: Any,
    ) -> DeploymentRelationship:
        return self._deployment.relate(self, target, title, **kwargs)


@dataclass
class DeploymentRelationship:
    """
    A relationship between deployment nodes or instances.

    Attributes:
        source: Initiating node or instance.
        target: Receiving node or instance.
        title: Relationship label.
        description: Longer Markdown description.
        technology: Technology used by the relationship.
        kind: Declared relationship kind, if any.
        bidirectional: Whether the relationship is declared with ``<->``.
        tags: Tags applied to the relationship, without ``#``.
        metadata: Custom metadata.
        links: Hyperlinks.
        style: Relationship-local style properties.
    """

    source: DeploymentNode | DeploymentInstance
    target: DeploymentNode | DeploymentInstance
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    kind: str | None = None
    bidirectional: bool = False
    tags: tuple[str, ...] = ()
    metadata: dict[str, MetadataValue] = field(default_factory=dict)
    links: tuple[Link, ...] = ()
    style: dict[str, StyleValue] = field(default_factory=dict)

    def __or__(self, title: str) -> DeploymentRelationship:
        """
        Set the title of an unlabeled relationship: ``a >> b | "title"``.

        Raises:
            ValueError: If the relationship already has a title.
        """
        if not isinstance(title, str):
            return NotImplemented

        _set_title(self, title)
        return self

    @classmethod
    def create(
        cls,
        source: DeploymentNode | DeploymentInstance,
        target: DeploymentNode | DeploymentInstance,
        title: str | None = None,
        *,
        description: str | None = None,
        technology: str | None = None,
        kind: str | None = None,
        bidirectional: bool = False,
        tags: list[str] | tuple[str, ...] | None = None,
        metadata: Mapping[str, Any] | None = None,
        links: list[Any] | tuple[Any, ...] | None = None,
        **style: Any,
    ) -> DeploymentRelationship:
        """Build a relationship, validating the supplied properties."""
        if kind is not None:
            check_identifier(kind, "Relationship kind")

        return cls(
            source=source,
            target=target,
            title=title,
            description=description,
            technology=technology,
            kind=kind,
            bidirectional=bidirectional,
            tags=normalize_likec4_tags(tags),
            metadata=normalize_metadata(metadata),
            links=normalize_links(links),
            style=parse_relationship_style(**style),
        )


class Deployment:
    """
    The deployment nodes, instances and relationships of a project.

    Attributes:
        nodes: Every node in creation order.
        instances: Every instance in creation order.
        relationships: Every deployment relationship in creation order.
    """

    def __init__(self, project: Project) -> None:
        """
        Initialize an empty deployment.

        Args:
            project: Project that owns the deployment.
        """
        self._project = project
        self._owner_stack: list[DeploymentNode] = []
        self.nodes: list[DeploymentNode] = []
        self.instances: list[DeploymentInstance] = []
        self.relationships: list[DeploymentRelationship] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    @property
    def roots(self) -> list[DeploymentNode]:
        """Return the top-level nodes in declaration order."""
        return [node for node in self.nodes if node.parent is None]

    def _pop_owner(self, node: DeploymentNode) -> None:
        if not self._owner_stack or self._owner_stack[-1] is not node:
            raise RuntimeError("LikeC4 deployment ownership context mismatch")

        self._owner_stack.pop()

    def node(
        self,
        kind: str,
        title: str | None = None,
        *,
        parent: DeploymentNode | None = None,
        **kwargs: Any,
    ) -> DeploymentNode:
        """
        Create a deployment node of a declared kind.

        Without ``parent`` the node nests into the innermost node whose
        ``with`` block is active, or becomes a root node.

        Args:
            kind: Declared deployment node kind.
            title: Display title.
            parent: Explicit parent node.
            **kwargs: Any other ``DeploymentNode`` argument.
        """
        if parent is None and self._owner_stack:
            parent = self._owner_stack[-1]

        node = DeploymentNode(self, kind, title, parent=parent, **kwargs)
        if parent is not None:
            parent.children.append(node)

        self.nodes.append(node)
        return node

    def instance(
        self,
        element: Element,
        name: str | None = None,
        *,
        parent: DeploymentNode | None = None,
        **kwargs: Any,
    ) -> DeploymentInstance:
        """
        Add an instance of a model element to a node.

        Args:
            element: Model element to instantiate.
            name: Optional instance identifier.
            parent: Node that holds the instance; defaults to the innermost
                node whose ``with`` block is active.
            **kwargs: Any other ``DeploymentInstance`` argument.
        """
        if parent is None and self._owner_stack:
            parent = self._owner_stack[-1]

        if parent is None:
            raise ValueError("An instance must be placed in a deployment node.")

        instance = DeploymentInstance(
            self, element, name, parent=parent, **kwargs
        )
        parent.instances.append(instance)
        self.instances.append(instance)
        return instance

    def relate(
        self,
        source: DeploymentNode | DeploymentInstance,
        target: DeploymentNode | DeploymentInstance,
        title: str | None = None,
        **kwargs: Any,
    ) -> DeploymentRelationship:
        """
        Create a relationship between nodes or instances of this deployment.

        Args:
            source: Initiating node or instance.
            target: Receiving node or instance.
            title: Relationship label.
            **kwargs: Any other ``DeploymentRelationship.create`` argument.
        """
        for end in (source, target):
            if (
                not isinstance(end, (DeploymentNode, DeploymentInstance))
                or end._deployment is not self
            ):
                raise ValueError(
                    f"Relationship endpoint {end!r} does not belong to this "
                    "deployment."
                )

        relationship = DeploymentRelationship.create(
            source, target, title, **kwargs
        )
        self.relationships.append(relationship)
        return relationship
