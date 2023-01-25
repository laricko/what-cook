from typing import List
from itertools import chain

from sqlalchemy import Table


def get_fields_for_json_build_object(table: Table) -> List:
    """
    Using with jsonb_build_object aggregation in sql query.
    Note that you can't use database object to execute query, you need use session from sqlalchemy
    """
    columns = [[col.name, col] for col in table.c]
    return chain.from_iterable(columns)
