import math

from fastapi import Query


class Paginator:
    def __init__(
            self,
            per_page: int = Query(
                default=50, alias='page[size]', description='Количество элементов на странице', ge=1, le=500
            ),
            page: int = Query(default=1, alias='page[number]', description='Номер страницы', ge=1),
    ):
        self.per_page = per_page
        self.page = page

    @property
    def get_offset(self) -> int:
        return (self.page - 1) * self.per_page

    def get_total_pages(self, found: int) -> int:
        return math.ceil(found / self.per_page)
