"""Module for logging utilities."""

import logging

__all__ = ["format_table_log"]

logger = logging.getLogger(__name__)


def format_table_log(title: str, legend: list[dict], data: list[dict], include_row_separators: bool = False) -> str:
    """Formats data into a string table based on a legend mapping keys to headers/widths."""
    if not data:
        return f"{title}\n(No data to display)"
    if not legend:
        return f"{title}\n(Legend is empty)"

    headers = [item["header"] for item in legend]
    widths = [item["width"] for item in legend]

    # Validate legend items
    for item in legend:
        if not all(k in item for k in ("data_key", "header", "width")):
            raise ValueError("Each legend item must contain 'data_key', 'header', and 'width'")
        if not isinstance(item["width"], int) or item["width"] <= 0:
            raise ValueError(f"Width for '{item['header']}' must be a positive integer")

    header_parts = [f"{h:<{w}}" for h, w in zip(headers, widths)]
    header_str = "| " + " | ".join(header_parts) + " |"

    separator = "+" + "-" * (len(header_str) - 2) + "+"

    table_rows = [title, separator, header_str, separator]

    for i, item in enumerate(data):
        row_parts = []
        for entry in legend:
            key = entry["data_key"]
            width = entry["width"]
            if key not in item:
                logger.warning("Key '%s' not found in data. Substituting empty string.", key)
            value = item.get(key, "")

            if isinstance(value, float):
                formatted_value = f"{value:.1f}"
                if len(formatted_value) > width:
                    try:
                        precision = max(0, width - len(str(int(value))) - 1)
                        formatted_value = f"{value:.{precision}f}"
                        if len(formatted_value) > width:
                            formatted_value = formatted_value[: width - 1] + "."
                    except Exception:
                        logger.warning("Error formatting float value '%s' for width %d", value, width)
                        formatted_value = str(value)[: width - 1] + "."
                else:
                    formatted_value = f"{formatted_value:<{width}}"

            else:
                formatted_value = f"{str(value):<{width}}"

            if len(formatted_value) > width:
                formatted_value = formatted_value[: width - 1] + "."
            elif len(formatted_value) < width:
                formatted_value = f"{formatted_value:<{width}}"

            row_parts.append(formatted_value)

        row_str = "| " + " | ".join(row_parts) + " |"

        if len(row_str) < len(header_str):
            row_str = row_str[:-2] + " " * (len(header_str) - len(row_str)) + " |"
        elif len(row_str) > len(header_str):
            row_str = row_str[: len(header_str) - 2] + " |"

        table_rows.append(row_str)
        if include_row_separators and i < len(data) - 1:
            table_rows.append(separator)

    table_rows.append(separator)

    return "\n".join(table_rows)
