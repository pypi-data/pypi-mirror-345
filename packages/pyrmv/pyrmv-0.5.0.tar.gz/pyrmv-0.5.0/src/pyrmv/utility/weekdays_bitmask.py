from typing import OrderedDict


def weekdays_bitmask(data: OrderedDict[str, bool]) -> str:
    """Convert ordered dict with weekdays to a bitmask.

    ### Args:
        * data (OrderedDict[str, bool]): OrderedDict formatted as follows: OrderedDict(Monday=bool, Tuesday=bool, Wednesday=bool, Thursday=bool, Friday=bool, Saturday=bool, Sunday=bool)

    ### Returns:
        * str: _description_
    """
    if len(data) != 7:
        raise ValueError(
            "OrderedDict must be formatted as follows: OrderedDict(Monday=bool, Tuesday=bool, Wednesday=bool, Thursday=bool, Friday=bool, Saturday=bool, Sunday=bool)"
        )

    return "".join("1" if data[day] else "0" for day in data)
