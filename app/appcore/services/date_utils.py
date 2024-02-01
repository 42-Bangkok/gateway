"""
Inserts cadet data
"""

from calendar import month_name
from datetime import date


def prev_n_months(n: int) -> list[str]:
    """
    Returns a list of the names of the previous n months.

    Args:
        n (int): The number of previous months to retrieve.

    Returns:
        list[str]: A list of the names of the previous n months, in lowercase.

    Example:
        >>> prev_n_months(3)
        ['may', 'april', 'march']
    """
    current_month_idx = date.today().month - 1
    ret = []
    for i in range(1, n + 1):
        previous_month_idx = (current_month_idx - i) % 12
        m = int(previous_month_idx + 1)
        ret.append(month_name[m].lower())
    return ret


def next_n_months(n: int) -> list[str]:
    """
    Returns a list of the names of the next n months.

    Args:
        n (int): The number of months to generate.

    Returns:
        list[str]: A list of the names of the next n months.
    """
    current_month_idx = date.today().month - 1
    ret = []
    for i in range(1, n + 1):
        next_month_idx = (current_month_idx + i) % 12
        m = int(next_month_idx + 1)
        ret.append(month_name[m].lower())
    return ret


def month_range_from_now(n: int) -> list[str]:
    """
    Returns a list of months from n months ago to n months from now, including the current month.
    Args:
        n (int): Number of months to go back and forward.
    Returns:
        list[str]: List of months.
    """
    return (
        prev_n_months(n) + [month_name[(date.today().month)].lower()] + next_n_months(n)
    )
