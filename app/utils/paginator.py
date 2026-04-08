from typing import TypeVar, List, Tuple
from sqlalchemy.orm import Query

T = TypeVar("T")


def paginate(query: Query, page: int, page_size: int) -> Tuple[int, List]:
    """
    Generic helper to apply offset/limit pagination to a SQLAlchemy query.

    Args:
        query: An active SQLAlchemy Query object (pre-filtered).
        page: 1-indexed page number.
        page_size: Number of records per page.

    Returns:
        A tuple of (total_count, items_on_current_page).
    """
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items
