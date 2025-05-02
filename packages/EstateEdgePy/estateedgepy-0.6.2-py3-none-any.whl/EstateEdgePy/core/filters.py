import warnings
from typing import Union, List, Optional, Tuple

import pyarrow as pa
import pyarrow.compute as pc
from fastcore.basics import listify

from EstateEdgePy.src.logger import CustomLogger

warnings.warn(
    "This filters.py module is deprecated and will be removed in a future version.",
    category=DeprecationWarning,
    stacklevel=2
)

logging = CustomLogger().logger


def filter_sales_price(data: pa.Table, price: Union[str, List[str]]) -> pa.Table:
    forms = [str(item) for item in listify(price)]
    data = data.filter(pc.is_in(data["sale_price"], pa.array(forms)))
    return data


def filter_sales_price_range(
        data: pa.Table,
        price: Union[str, List[str]],
        min_price: Optional[Union[int, float]] = None,
        max_price: Optional[Union[int, float]] = None
) -> pa.Table:
    """Filter sales data, keeping only records where sale_price is within the given price range."""

    # Convert input price list to a set of unique float values
    try:
        valid_prices = {float(p) for p in (price if isinstance(price, list) else [price])}
    except ValueError:
        raise ValueError("Invalid price values; ensure all prices are numeric.")

    # Ensure sale_price column is numeric
    sale_price_col = pc.cast(data["sale_price"], pa.float64())

    # Build filter conditions
    conditions = [pc.is_in(sale_price_col, pa.array(list(valid_prices), pa.float64()))]

    if min_price is not None:
        conditions.append(pc.greater_equal(sale_price_col, min_price))
    if max_price is not None:
        conditions.append(pc.less_equal(sale_price_col, max_price))

    # Apply filtering
    if len(conditions) == 1:
        filtered_data = data.filter(conditions[0])  # Use single condition directly
    else:
        filtered_data = data.filter(pc.and_(*conditions))

    return filtered_data


def filter_min_max_price(data: pa.Table, column: str) -> pa.Table:
    column_data = data[column]  # get the column

    # convert to to numeric type
    if pa.types.is_string(column_data.type):
        column_data = pc.cast(column_data, pa.float64())

    # compute min and max prices
    min_prices = pc.min(column_data).as_py()
    max_prices = pc.max(column_data).as_py()

    # build filter condition
    condition = pc.is_in(column_data, pa.array([min_prices, max_prices], pa.float64()))

    return data.filter(condition)

def convert_to_timestamp(date_column: pa.Array) -> pa.Array:
    """Convert a PyArrow string column to timestamps."""
    return pc.strptime(date_column, format="%m-%d-%Y", unit="s")


def parse_date_range(date_input: str) -> tuple:
    """Parse a date range input (e.g., '12-06-2024:12-07-2024') into start and end dates."""
    start_date, end_date = date_input.split(":")
    return start_date.strip() or None, end_date.strip() or None


def filter_by_exact_date(data: pa.Table, date_str: str, column: str) -> pa.Table:
    """Filter a table for an exact sale_date match."""
    sale_date_col = convert_to_timestamp(data[column])
    target_date = pc.strptime(date_str, format="%m-%d-%Y", unit="s")
    return data.filter(pc.equal(sale_date_col, target_date))


def filter_by_date_range(data: pa.Table, date_range: str, column: str) -> pa.Table:
    """Filter a table based on a date range."""
    sale_date_col = convert_to_timestamp(data[column])
    start_date, end_date = parse_date_range(date_range)

    conditions = []
    if start_date:
        start_ts = pc.strptime(start_date, format="%m-%d-%Y", unit="s")
        conditions.append(pc.greater_equal(sale_date_col, start_ts))
    if end_date:
        end_ts = pc.strptime(end_date, format="%m-%d-%Y", unit="s")
        conditions.append(pc.less_equal(sale_date_col, end_ts))

    if conditions:
        mask = conditions[0] if len(conditions) == 1 else pc.and_(*conditions)
        return data.filter(mask)

    return data


def filter_by_date(data: pa.Table, date_input: str, date_column: str) -> pa.Table:
    """Main function to filter PyArrow Table by date (single date or range)."""
    if ":" in date_input:
        return filter_by_date_range(data, date_input, date_column)
    return filter_by_exact_date(data, date_input, date_column)


def filter_property_type(data: pa.Table, property_type: Union[str, List[str]]) -> pa.Table:
    property_types = [str(types) for types in listify(property_type)]
    data = data.filter(pc.is_in(data["property_type"], pa.array(property_types)))
    return data


def filter_real_estate_type(data: pa.Table, estate_type: Union[str, List[str]]) -> pa.Table:
    property_types = [str(types) for types in listify(estate_type)]
    data = data.filter(pc.is_in(data["real_estate_type"], pa.array(property_types)))
    return data


def filter_transfer_type(data: pa.Table, transfer_type: Union[str, List[str]]) -> pa.Table:
    property_types = [str(types) for types in listify(transfer_type)]
    data = data.filter(pc.is_in(data["type_transfer_info"], pa.array(property_types)))
    return data


def filter_transfer_price(data: pa.Table, transfer_price: Union[str, List[str]]) -> pa.Table:
    property_types = [str(types) for types in listify(transfer_price)]
    data = data.filter(pc.is_in(data["price_transfer_info"], pa.array(property_types)))
    return data


def filter_location(
        data: pa.Table,
        state: Union[str, List[str]],
        county: Union[str, List[str]],
        street: Union[str, List[str]] = None,
        neighborhood: Union[str, List[str]] = None,
        zipcode: Union[str, List[str]] = None,
        case_sensitive: bool = True
) -> pa.Table:

    def normalize(values):
        if isinstance(values, str):
            values = [values]
        return [v.lower() for v in values] if not case_sensitive else values

    # Normalize parameters based on case sensitivity
    state_values = normalize(state)
    county_values = normalize(county)

    # Normalize dataset columns if case insensitive
    state_types = data["state"]
    county_types = data["county"]
    if not case_sensitive:
        state_types = pc.utf8_lower(state_types)
        county_types = pc.utf8_lower(county_types)

    conditions = [
        pc.is_in(state_types, pa.array(state_types, pa.string())),
        pc.is_in(county_types, pa.array(county_types, pa.string()))
    ]

    if street:
        street_values = normalize(street)
        street_col = data["street_location"]
        if not case_sensitive:
            street_col = pc.utf8_lower(street_col)
        conditions.append(pc.is_in(street_col, pa.array(street_values, pa.string())))

    if neighborhood:
        neighborhood_values = normalize(neighborhood)
        neighborhood_col = data["neighborhood"]
        if not case_sensitive:
            neighborhood_col = pc.utf8_lower(neighborhood_col)
        conditions.append(pc.is_in(neighborhood_col, pa.array(neighborhood_values, pa.string())))

    if zipcode:
        zip_values = normalize(zipcode)
        zipcode_col = data["zip_code"]
        if not case_sensitive:
            zipcode_col = pc.utf8_lower(zipcode_col)
        conditions.append(pc.is_in(zipcode_col, pa.array(zip_values, pa.string())))

    return data.filter(pc.and_(*conditions))


def filter_by_location_partial(
        data: pa.Table,
        state: Union[str, List[str], None] = None,
        county: Union[str, List[str], None] = None,
        street_location: Union[str, List[str], None] = None,
        neighborhood: Union[str, List[str], None] = None,
        zip_code: Union[str, List[str], None] = None,
        case_sensitive: bool = True
) -> pa.Table:
    """Filter sales data by state, county, street_location, neighborhood, and zip_code with partial matching.
    Supports string or list inputs and allows case-insensitive matching.
    """

    def normalize(values):
        if isinstance(values, str):
            values = [values]
        return [v.lower() for v in values] if not case_sensitive else values

    conditions = []

    if state:
        state_values = normalize(state)
        state_col = data["state"]
        if not case_sensitive:
            state_col = pc.utf8_lower(state_col)
        conditions.append(pc.match_substring(state_col, state_values[0]))

    if county:
        county_values = normalize(county)
        county_col = data["county"]
        if not case_sensitive:
            county_col = pc.utf8_lower(county_col)
        conditions.append(pc.match_substring(county_col, county_values[0]))

    if street_location:
        street_values = normalize(street_location)
        street_col = data["street_location"]
        if not case_sensitive:
            street_col = pc.utf8_lower(street_col)
        conditions.append(pc.match_substring(street_col, street_values[0]))

    if neighborhood:
        neighborhood_values = normalize(neighborhood)
        neighborhood_col = data["neighborhood"]
        if not case_sensitive:
            neighborhood_col = pc.utf8_lower(neighborhood_col)
        conditions.append(pc.match_substring(neighborhood_col, neighborhood_values[0]))

    if zip_code:
        zip_values = normalize(zip_code)
        zip_col = data["zip_code"]
        conditions.append(pc.match_substring(zip_col, zip_values[0]))

    return data.filter(pc.and_(*conditions))


def total_sales_price_over_period(data: pa.Table, date_range: str, column: str) -> float:
    #TODO: Work on this function and test it
    """Returns the total sum of sales price over a given date range."""
    filtered_data = filter_by_date_range(data, date_range, column)

    # Ensure sale_price is converted to float
    sale_price_col = pc.cast(filtered_data[column], pa.float64())

    return pc.sum(sale_price_col).as_py() if filtered_data.num_rows > 0 else 0.0