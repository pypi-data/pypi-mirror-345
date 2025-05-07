from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field


class CreateCompanyCommand(BaseModel):
    name: str
    provider_id: UUID
    registration_number: str
    address: str
    website: str | None = None
    status: str = Field(default="active")

    def __str__(self):
        return f"CreateCompanyCommand(name={self.name}, id={self.provider_id})"
