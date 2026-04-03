from __future__ import annotations

import inspect
from inspect import cleandoc
from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel
from pydantic.json_schema import (
    CoreSchema,
    GetJsonSchemaHandler,
    JsonSchemaValue,
)

from c4.diagrams.core import BaseDiagramElement

TDiagramElement = TypeVar("TDiagramElement", bound=BaseDiagramElement)
TypeDiagramElement = type[TDiagramElement]


class JSONSchemaMixin:
    """
    Mixin that post-processes the generated JSON Schema.

    Removes redundant `description` fields when they duplicate the
    class docstring, keeping the schema output cleaner.
    """

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """
        Drop redundant JSON Schema description if it equals
        the class docstring.
        """
        json_schema = handler(core_schema)

        doc = cls.__doc__
        description = json_schema.get("description")

        if doc and description and cleandoc(doc) == description:
            json_schema.pop("description", None)

        return json_schema


class BaseSchemaItem(JSONSchemaMixin, BaseModel, Generic[TDiagramElement]):
    """
    Pydantic schema wrapper that can instantiate a diagram element
    from its fields.
    """

    __diagram_element__: TypeDiagramElement | None = None

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """
        Customize the generated JSON Schema for model.

        Sets the schema `title` to the name of the associated
        `__diagram_element__` class, if defined.

        If the generated `description` matches the model's docstring, it is
        removed to avoid duplicating documentation.
        """
        json_schema = super().__get_pydantic_json_schema__(
            core_schema,
            handler,
        )

        if cls.__diagram_element__:
            json_schema["title"] = cls.__diagram_element__.__name__

        return json_schema

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        cls.__diagram_element__ = cls._resolve_diagram_element_class()

    @classmethod
    def _resolve_diagram_element_class(cls) -> type[TDiagramElement] | None:
        """Resolve and validate the diagram element type for the subclass."""
        if cls.__diagram_element__:
            return cls.__diagram_element__

        meta = getattr(cls, "__pydantic_generic_metadata__", None)
        if not meta:  # pragma: no cover
            return None

        origin = meta.get("origin")
        args = meta.get("args", ())
        if (
            origin
            and inspect.isclass(origin)
            and issubclass(origin, BaseSchemaItem)
        ):
            for arg in args:
                if inspect.isclass(arg) and issubclass(arg, BaseDiagramElement):
                    return cast(type[TDiagramElement], arg)

        return None

    def _get_diagram_element_class(self) -> type[TDiagramElement] | None:
        """Return a validated diagram element class for this schema item."""
        return self.__diagram_element__

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """
        Convert schema fields into kwargs suitable for the element constructor.
        """
        data: dict[str, Any] = self.model_dump(mode="python")

        # Keep alias only if provided (avoid injecting None).
        alias = data.pop("alias", None)
        if alias:
            data["alias"] = alias

        return data

    @staticmethod
    def _allowed_init_params(
        element_cls: type[Any],
    ) -> frozenset[str]:
        """
        Return constructor parameter names for the target element class.
        """
        signature = inspect.signature(element_cls.__init__)
        return frozenset(signature.parameters.keys()) - {"self"}

    def to_diagram_element(self, **overrides: Any) -> BaseDiagramElement:
        """
        Instantiate the target diagram element using validated
        and filtered kwargs.
        """
        element_cls = self._get_diagram_element_class()
        if not element_cls:
            raise ValueError(
                f"__diagram_element__ not provided for {self.__class__!r}"
            )

        kwargs = self._to_diagram_element_kwargs()
        kwargs.update(overrides)

        allowed = self._allowed_init_params(element_cls)
        filtered = {
            key: value
            for key, value in kwargs.items()
            if key in allowed and value is not None
        }

        return element_cls(**filtered)
