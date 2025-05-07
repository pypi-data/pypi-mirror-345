from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: int = 3
    offset: int = 0


async def get_pagination_params(limit: int = 3, offset: int = 0):
    return PaginationParams(limit=limit, offset=offset)
