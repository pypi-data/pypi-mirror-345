from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class UpdateCompanyCommand(BaseModel):
    company_id: UUID
    name: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None

    def __str__(self):
        return f"UpdateCompanyCommand(name={self.name}, id={self.company_id})"