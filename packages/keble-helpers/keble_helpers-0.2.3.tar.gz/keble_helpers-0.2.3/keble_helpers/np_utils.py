import math
from typing import Optional

import numpy as np


# You can use this helper function to check if a value is NaN or infinity
def is_invalid_float(value: Optional[float]) -> bool:
    if value is None:
        return False
    return math.isnan(value) or math.isinf(value)


def guard_invalid_float(value: float | None | np.floating) -> float | None:
    """
    Checks if the value is an invalid float (NaN, Infinity, -Infinity).
    If invalid, replaces it with None.

    Parameters:
    - value: The value to check, can be a float or a numpy float.

    Returns:
    - None if the value is invalid (NaN, inf, -inf), otherwise returns the value.
    """
    # Check for NaN or Infinity using numpy's functions
    if isinstance(value, np.floating):  # Handle np.float32, np.float64, etc.
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    elif isinstance(value, float):  # Handle Python native floats
        if np.isnan(value) or np.isinf(value):
            return None
    return value
