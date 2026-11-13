from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from c4.contrib.likec4 import Project
from c4.contrib.likec4._styles import StyleValue
from c4.converters.json.mixins import JSONSchemaMixin

Metadata = dict[str, str | list[str]]


class _LikeC4Schema(JSONSchemaMixin, BaseModel):
    """Strict base class for the LikeC4 project JSON contract."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class LikeC4LinkSchema(_LikeC4Schema):
    """A hyperlink attached to an element, relationship or view."""

    url: str = Field(min_length=1)
    title: str | None = None


class LikeC4ElementKindSchema(_LikeC4Schema):
    """A declared element or deployment node kind."""

    name: str = Field(min_length=1)
    title: str | None = None
    technology: str | None = None
    description: str | None = None
    notation: str | None = None
    tags: list[str] = Field(default_factory=list)
    style: dict[str, StyleValue] = Field(default_factory=dict)


class LikeC4RelationshipKindSchema(_LikeC4Schema):
    """A declared relationship kind."""

    name: str = Field(min_length=1)
    technology: str | None = None
    description: str | None = None
    style: dict[str, StyleValue] = Field(default_factory=dict)


class LikeC4TagSchema(_LikeC4Schema):
    """A declared tag; the name is written without ``#``."""

    name: str = Field(min_length=1)
    color: str | None = None


class LikeC4ColorSchema(_LikeC4Schema):
    """A custom named color."""

    name: str = Field(min_length=1)
    value: str = Field(min_length=1)


class LikeC4SpecificationSchema(_LikeC4Schema):
    """The vocabulary of a project: kinds, tags and custom colors."""

    elements: list[LikeC4ElementKindSchema] = Field(default_factory=list)
    relationships: list[LikeC4RelationshipKindSchema] = Field(
        default_factory=list
    )
    deployment_nodes: list[LikeC4ElementKindSchema] = Field(
        default_factory=list
    )
    tags: list[LikeC4TagSchema] = Field(default_factory=list)
    colors: list[LikeC4ColorSchema] = Field(default_factory=list)


class _LikeC4NodeSchema(_LikeC4Schema):
    """Properties shared by model elements and deployment nodes."""

    id: str = Field(min_length=1)
    alias: str | None = None
    kind: str = Field(min_length=1)
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    links: list[LikeC4LinkSchema] = Field(default_factory=list)
    style: dict[str, StyleValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_name(self) -> _LikeC4NodeSchema:
        """Require a title or an alias, as the authoring API does."""
        if self.title is None and self.alias is None:
            raise ValueError(f"{self.id!r}: an element needs a title or alias")
        return self


class LikeC4ElementSchema(_LikeC4NodeSchema):
    """A model element; children nest without limit."""

    summary: str | None = None
    icon: str | None = None
    elements: list[LikeC4ElementSchema] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_icon(self) -> LikeC4ElementSchema:
        """Keep the element icon in its own field, not in the style."""
        if "icon" in self.style:
            raise ValueError(f"{self.id!r}: use the icon field, not style.icon")
        return self


class LikeC4RelationshipSchema(_LikeC4Schema):
    """A model relationship using c4-diagrams ``from``/``to`` spelling."""

    from_: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    kind: str | None = None
    bidirectional: bool = False
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    links: list[LikeC4LinkSchema] = Field(default_factory=list)
    style: dict[str, StyleValue] = Field(default_factory=dict)
    navigate_to: str | None = None


class LikeC4ModelSchema(_LikeC4Schema):
    """The element hierarchy and relationships of a project."""

    elements: list[LikeC4ElementSchema] = Field(default_factory=list)
    relationships: list[LikeC4RelationshipSchema] = Field(default_factory=list)


class LikeC4InstanceSchema(_LikeC4Schema):
    """An instance of a model element deployed on a node."""

    id: str | None = None
    name: str | None = None
    element: str = Field(min_length=1)
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    links: list[LikeC4LinkSchema] = Field(default_factory=list)
    style: dict[str, StyleValue] = Field(default_factory=dict)


class LikeC4DeploymentNodeSchema(_LikeC4NodeSchema):
    """A deployment node; nodes nest and hold instances."""

    nodes: list[LikeC4DeploymentNodeSchema] = Field(default_factory=list)
    instances: list[LikeC4InstanceSchema] = Field(default_factory=list)


class LikeC4DeploymentRelationshipSchema(_LikeC4Schema):
    """A relationship between deployment nodes or instances."""

    from_: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    kind: str | None = None
    bidirectional: bool = False
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    links: list[LikeC4LinkSchema] = Field(default_factory=list)
    style: dict[str, StyleValue] = Field(default_factory=dict)


class LikeC4DeploymentSchema(_LikeC4Schema):
    """The deployment nodes, instances and relationships of a project."""

    nodes: list[LikeC4DeploymentNodeSchema] = Field(default_factory=list)
    relationships: list[LikeC4DeploymentRelationshipSchema] = Field(
        default_factory=list
    )


class LikeC4WildcardSchema(_LikeC4Schema):
    """The ``*`` predicate."""

    type: Literal["wildcard"]


class LikeC4ElementRefSchema(_LikeC4Schema):
    """A reference to a model element, node or instance by id."""

    type: Literal["element"]
    id: str = Field(min_length=1)


class LikeC4ChildrenSchema(_LikeC4Schema):
    """The direct children of an item (``item.*``)."""

    type: Literal["children"]
    of: str = Field(min_length=1)


class LikeC4DescendantsSchema(_LikeC4Schema):
    """All nested items of an item (``item.**``)."""

    type: Literal["descendants"]
    of: str = Field(min_length=1)


class LikeC4RawPredicateSchema(_LikeC4Schema):
    """Predicate text emitted verbatim."""

    type: Literal["raw"]
    text: str = Field(min_length=1)


LikeC4BasicItemSchema = Annotated[
    LikeC4WildcardSchema
    | LikeC4ElementRefSchema
    | LikeC4ChildrenSchema
    | LikeC4DescendantsSchema,
    Field(discriminator="type"),
]


class LikeC4WhereSchema(_LikeC4Schema):
    """``item where tag is #tag and kind is kind`` filter."""

    type: Literal["where"]
    item: LikeC4BasicItemSchema
    tag: str | None = None
    kind: str | None = None

    @model_validator(mode="after")
    def validate_condition(self) -> LikeC4WhereSchema:
        """Require at least one condition."""
        if self.tag is None and self.kind is None:
            raise ValueError("where needs a tag or a kind condition")
        return self


class LikeC4BetweenSchema(_LikeC4Schema):
    """Relationship predicate ``source -> target`` (``<->`` with ``both``)."""

    type: Literal["between"]
    source: LikeC4BasicItemSchema
    target: LikeC4BasicItemSchema
    both: bool = False


class LikeC4IncomingSchema(_LikeC4Schema):
    """Relationship predicate ``-> item``."""

    type: Literal["incoming"]
    item: LikeC4BasicItemSchema


class LikeC4OutgoingSchema(_LikeC4Schema):
    """Relationship predicate ``item ->``."""

    type: Literal["outgoing"]
    item: LikeC4BasicItemSchema


class LikeC4InOutSchema(_LikeC4Schema):
    """Relationship predicate ``-> item ->``."""

    type: Literal["inout"]
    item: LikeC4BasicItemSchema


LikeC4PredicateSchema = Annotated[
    LikeC4WildcardSchema
    | LikeC4ElementRefSchema
    | LikeC4ChildrenSchema
    | LikeC4DescendantsSchema
    | LikeC4WhereSchema
    | LikeC4BetweenSchema
    | LikeC4IncomingSchema
    | LikeC4OutgoingSchema
    | LikeC4InOutSchema
    | LikeC4RawPredicateSchema,
    Field(discriminator="type"),
]


class LikeC4IncludeRuleSchema(_LikeC4Schema):
    """``include items [with { navigateTo key }]`` rule."""

    rule: Literal["include"]
    items: list[LikeC4PredicateSchema] = Field(min_length=1)
    navigate_to: str | None = None


class LikeC4ExcludeRuleSchema(_LikeC4Schema):
    """``exclude items`` rule."""

    rule: Literal["exclude"]
    items: list[LikeC4PredicateSchema] = Field(min_length=1)


class LikeC4StyleRuleSchema(_LikeC4Schema):
    """``style targets { ... }`` rule."""

    rule: Literal["style"]
    targets: list[LikeC4PredicateSchema] = Field(min_length=1)
    properties: dict[str, StyleValue] = Field(min_length=1)


class LikeC4AutoLayoutRuleSchema(_LikeC4Schema):
    """``autoLayout direction [rank_sep [node_sep]]`` rule."""

    rule: Literal["auto_layout"]
    direction: Literal["TopBottom", "LeftRight", "BottomTop", "RightLeft"] = (
        "TopBottom"
    )
    rank_sep: int | None = Field(None, ge=0)
    node_sep: int | None = Field(None, ge=0)


LikeC4ViewRuleSchema = Annotated[
    LikeC4IncludeRuleSchema
    | LikeC4ExcludeRuleSchema
    | LikeC4StyleRuleSchema
    | LikeC4AutoLayoutRuleSchema,
    Field(discriminator="rule"),
]


class LikeC4ViewSchema(_LikeC4Schema):
    """Properties shared by every view type."""

    key: str = Field(min_length=1)
    title: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    links: list[LikeC4LinkSchema] = Field(default_factory=list)


class LikeC4ElementViewSchema(LikeC4ViewSchema):
    """A view over model elements."""

    type: Literal["element"]
    of: str | None = None
    rules: list[LikeC4ViewRuleSchema] = Field(default_factory=list)


class LikeC4DeploymentViewSchema(LikeC4ViewSchema):
    """A view over deployment nodes and instances."""

    type: Literal["deployment"]
    rules: list[LikeC4ViewRuleSchema] = Field(default_factory=list)


class LikeC4DynamicStepSchema(_LikeC4Schema):
    """One flat interaction of a dynamic view; blocks are not supported."""

    from_: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    notes: str | None = None
    navigate_to: str | None = None
    color: str | None = None
    backward: bool = False


class LikeC4DynamicViewSchema(LikeC4ViewSchema):
    """A dynamic view: an ordered, flat list of steps."""

    type: Literal["dynamic"]
    variant: Literal["diagram", "sequence"] = "diagram"
    steps: list[LikeC4DynamicStepSchema] = Field(default_factory=list)


class LikeC4ViewsSchema(_LikeC4Schema):
    """Declared views in authoring order."""

    items: list[
        Annotated[
            LikeC4ElementViewSchema
            | LikeC4DeploymentViewSchema
            | LikeC4DynamicViewSchema,
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)


class LikeC4RenderOptionsSchema(_LikeC4Schema):
    """LikeC4 renderer options."""

    view_key: str | None = Field(
        None,
        description="View exported as an image when none is chosen otherwise.",
    )


def _walk_elements(
    elements: list[LikeC4ElementSchema], path: str
) -> list[tuple[LikeC4ElementSchema, str]]:
    result: list[tuple[LikeC4ElementSchema, str]] = []
    for index, element in enumerate(elements):
        element_path = f"{path}[{index}]"
        result.append((element, element_path))
        result.extend(
            _walk_elements(element.elements, f"{element_path}->elements")
        )
    return result


def _walk_nodes(
    nodes: list[LikeC4DeploymentNodeSchema], path: str
) -> list[tuple[LikeC4DeploymentNodeSchema, str]]:
    result: list[tuple[LikeC4DeploymentNodeSchema, str]] = []
    for index, node in enumerate(nodes):
        node_path = f"{path}[{index}]"
        result.append((node, node_path))
        result.extend(_walk_nodes(node.nodes, f"{node_path}->nodes"))
    return result


def _register(registry: set[str], value: str, path: str, what: str) -> None:
    if value in registry:
        raise ValueError(f"{path}: Duplicate {what} id: {value!r}")
    registry.add(value)


def _require(registry: set[str], value: str, path: str, what: str) -> None:
    if value not in registry:
        raise ValueError(f"{path}: Unknown {what} id {value!r}")


class _ReferenceValidator:
    """Check that every id used in a project document is declared."""

    def __init__(self, schema: LikeC4ProjectSchema) -> None:
        self.schema = schema
        self.elements: set[str] = set()
        self.deployment: set[str] = set()
        self.views: dict[str, str] = {}

    def validate(self) -> None:
        self._collect_elements()
        self._collect_deployment()
        self._collect_views()
        self._check_model()
        self._check_deployment()
        self._check_views()
        self._check_render_options()

    def _collect_elements(self) -> None:
        for element, path in _walk_elements(
            self.schema.model.elements, "model->elements"
        ):
            _register(self.elements, element.id, f"{path}->id", "element")

    def _collect_deployment(self) -> None:
        for node, path in _walk_nodes(
            self.schema.deployment.nodes, "deployment->nodes"
        ):
            _register(
                self.deployment, node.id, f"{path}->id", "deployment node"
            )
            for index, instance in enumerate(node.instances):
                if instance.id is not None:
                    _register(
                        self.deployment,
                        instance.id,
                        f"{path}->instances[{index}]->id",
                        "deployment instance",
                    )

    def _collect_views(self) -> None:
        for index, view in enumerate(self.schema.views.items):
            path = f"views->items[{index}]->key"
            if view.key in self.views:
                raise ValueError(f"{path}: Duplicate view key: {view.key!r}")

            self.views[view.key] = view.type

    def _check_model(self) -> None:
        for index, relationship in enumerate(self.schema.model.relationships):
            path = f"model->relationships[{index}]"
            _require(
                self.elements, relationship.from_, f"{path}->from", "element"
            )
            _require(self.elements, relationship.to, f"{path}->to", "element")
            self._check_navigate(
                relationship.navigate_to, f"{path}->navigate_to", "dynamic"
            )

    def _check_deployment(self) -> None:
        for node, path in _walk_nodes(
            self.schema.deployment.nodes, "deployment->nodes"
        ):
            for index, instance in enumerate(node.instances):
                _require(
                    self.elements,
                    instance.element,
                    f"{path}->instances[{index}]->element",
                    "element",
                )

        for index, relationship in enumerate(
            self.schema.deployment.relationships
        ):
            path = f"deployment->relationships[{index}]"
            _require(
                self.deployment,
                relationship.from_,
                f"{path}->from",
                "deployment node or instance",
            )
            _require(
                self.deployment,
                relationship.to,
                f"{path}->to",
                "deployment node or instance",
            )

    def _check_views(self) -> None:
        for index, view in enumerate(self.schema.views.items):
            path = f"views->items[{index}]"
            if isinstance(view, LikeC4ElementViewSchema):
                if view.of is not None:
                    _require(self.elements, view.of, f"{path}->of", "element")
                self._check_rules(view.rules, path, self.elements, "element")

            elif isinstance(view, LikeC4DeploymentViewSchema):
                self._check_rules(
                    view.rules,
                    path,
                    self.deployment,
                    "deployment node or instance",
                )
            else:
                self._check_steps(view, path)

    def _check_steps(self, view: LikeC4DynamicViewSchema, path: str) -> None:
        for index, step in enumerate(view.steps):
            step_path = f"{path}->steps[{index}]"
            _require(self.elements, step.from_, f"{step_path}->from", "element")
            _require(self.elements, step.to, f"{step_path}->to", "element")
            self._check_navigate(
                step.navigate_to, f"{step_path}->navigate_to", "dynamic"
            )

    def _check_rules(
        self,
        rules: list[Any],
        path: str,
        registry: set[str],
        what: str,
    ) -> None:
        for index, rule in enumerate(rules):
            rule_path = f"{path}->rules[{index}]"
            if isinstance(rule, LikeC4IncludeRuleSchema):
                self._check_items(rule.items, rule_path, registry, what)
                self._check_navigate(
                    rule.navigate_to, f"{rule_path}->navigate_to", None
                )
            elif isinstance(rule, LikeC4ExcludeRuleSchema):
                self._check_items(rule.items, rule_path, registry, what)
            elif isinstance(rule, LikeC4StyleRuleSchema):
                self._check_items(rule.targets, rule_path, registry, what)

    def _check_items(
        self,
        items: list[Any],
        path: str,
        registry: set[str],
        what: str,
    ) -> None:
        for index, item in enumerate(items):
            self._check_item(item, f"{path}->items[{index}]", registry, what)

    def _check_item(
        self, item: Any, path: str, registry: set[str], what: str
    ) -> None:
        if isinstance(item, LikeC4ElementRefSchema):
            _require(registry, item.id, f"{path}->id", what)
        elif isinstance(item, (LikeC4ChildrenSchema, LikeC4DescendantsSchema)):
            _require(registry, item.of, f"{path}->of", what)
        elif isinstance(item, LikeC4WhereSchema):
            self._check_item(item.item, f"{path}->item", registry, what)
        elif isinstance(item, LikeC4BetweenSchema):
            for side in ("source", "target"):
                self._check_item(
                    getattr(item, side), f"{path}->{side}", registry, what
                )
        elif isinstance(
            item,
            (LikeC4IncomingSchema, LikeC4OutgoingSchema, LikeC4InOutSchema),
        ):
            self._check_item(item.item, f"{path}->item", registry, what)

    def _check_navigate(
        self, key: str | None, path: str, required_type: str | None
    ) -> None:
        if key is None:
            return

        if key not in self.views:
            raise ValueError(f"{path}: Unknown view key {key!r}")

        if required_type is not None and self.views[key] != required_type:
            raise ValueError(
                f"{path}: View {key!r} must be a {required_type} view"
            )

    def _check_render_options(self) -> None:
        options = self.schema.render_options
        if (
            options is not None
            and options.view_key is not None
            and options.view_key not in self.views
        ):
            raise ValueError(
                "render_options->view_key: Unknown view key "
                f"{options.view_key!r}"
            )


class LikeC4ProjectSchema(_LikeC4Schema):
    """A c4-diagrams, backend-specific LikeC4 project document."""

    backend: Literal["likec4"] = Field(
        ...,
        description=(
            "Required discriminator for the LikeC4 project JSON format."
        ),
    )
    name: str | None = Field(None, description="Optional project title.")
    specification: LikeC4SpecificationSchema = Field(
        default_factory=LikeC4SpecificationSchema
    )
    model: LikeC4ModelSchema = Field(default_factory=LikeC4ModelSchema)
    deployment: LikeC4DeploymentSchema = Field(
        default_factory=LikeC4DeploymentSchema
    )
    views: LikeC4ViewsSchema = Field(default_factory=LikeC4ViewsSchema)
    render_options: LikeC4RenderOptionsSchema | None = None

    @model_validator(mode="after")
    def validate_project_references(self) -> LikeC4ProjectSchema:
        """Reject unresolved references before a project is constructed."""
        _ReferenceValidator(self).validate()
        return self

    def to_project(self) -> Project:
        """Convert this complete project document into a Project."""
        from c4.contrib.likec4.converters.json.converter import (
            JSONToLikeC4ProjectConverter,
        )

        return JSONToLikeC4ProjectConverter(self).convert()


LikeC4ElementSchema.model_rebuild()
LikeC4DeploymentNodeSchema.model_rebuild()
