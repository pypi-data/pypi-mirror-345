from uuid import UUID
from pydantic import BaseModel


class GetCompanyByIdQuery(BaseModel):
    company_id: UUID

    def __str__(self):
        return f"GetCompanyByIdQuery(company_id={self.company_id})"
