from typing import List, Dict, Any, Union

import pyarrow as pa
import pandas as pd

from EstateEdgePy.src._errors import PropertyError


def convert_to_table(data: List[Dict[str, Any]]) -> Union[pd.DataFrame, pa.Table]:
    """Get the properties"""
    # Your implementation here
    if not data:
        return pa.Table({})

    data = pa.Table.from_pylist(data)
    return data


def normalize_state(state: str) -> str:
    agency = state.lower().strip()
    if not len(agency) == 2:
        raise PropertyError(message="""
        You are to pass the ISO CODE of the state you want.
        For example: Maryland = md""", status_code=411, error_code="411")
    return agency
