from typing import List
from itertools import chain

from sqlalchemy import Table


def get_fields_for_json_build_object(table: Table) -> List:
    columns = [[col.name, col] for col in table.c]
    return chain.from_iterable(columns)
