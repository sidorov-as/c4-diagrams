from __future__ import annotations

from inspect import cleandoc

from pydantic.json_schema import (
    CoreSchema,
    GetJsonSchemaHandler,
    JsonSchemaValue,
)


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
