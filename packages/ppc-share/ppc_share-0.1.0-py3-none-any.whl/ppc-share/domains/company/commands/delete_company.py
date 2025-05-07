from pydantic import BaseModel
from uuid import UUID


class DeleteCompanyCommand(BaseModel):
    company_id: UUID

    def __str__(self):
        return f"DeleteCompanyCommand(id={self.company_id})"
