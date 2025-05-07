from pydantic import BaseModel

from mixins.pagination import PaginationParams


class ListCompaniesQuery(BaseModel):
    pagination: PaginationParams

    def __str__(self):
        return f"ListCompaniesQuery(pagination={self.pagination})"