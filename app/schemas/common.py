from typing import ClassVar

from pydantic import BaseModel, ConfigDict, model_validator


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PatchModel(BaseModel):
    """Partial-update body: omitted fields are left alone.

    Fields listed in `non_nullable` may be omitted but not sent as null,
    since the matching database columns are NOT NULL.
    """

    non_nullable: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _reject_nulls(self):
        nulls = sorted(f for f in self.non_nullable if f in self.model_fields_set and getattr(self, f) is None)
        if nulls:
            raise ValueError(f"fields cannot be null: {', '.join(nulls)}")
        return self

    def changes(self) -> dict:
        return self.model_dump(exclude_unset=True)
