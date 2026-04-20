from __future__ import annotations

from typing import Any, ClassVar

from pydantic import ConfigDict

from c4.converters.json.schemas.base import BaseSchemaItem

TypeAny = type[Any]


class RenderOptionsItem(BaseSchemaItem):
    """
    Base schema model for render option items that can be converted
    into renderer-side dataclass models.

    Subclasses are expected to declare ``__model__`` with the target
    runtime model class.
    """

    model_config = ConfigDict(frozen=True)

    __model__: ClassVar[type[Any]]

    def to_model(self) -> Any:
        """
        Convert this schema object into its corresponding runtime model.

        The model is first dumped to a plain Python dictionary. Only fields
        accepted by the target model's initializer are kept.
        """
        kwargs: dict[str, Any] = self.model_dump(mode="python")

        allowed = self._allowed_init_params(self.__model__)
        filtered = {}
        for key, value in kwargs.items():
            if key in allowed:
                filtered[key] = value

        return self.__model__(**filtered)
