"""
## PythonRMV

Small module that makes your journey with RMV REST API somehow easier. Based fully on official RMV API reference and HAFAS documentation.

## Usage

```py
import pyrmv

# Define a Client with API key
client = pyrmv.Client("AcessId")

# Get origin's and destination's location
origin = client.stop_by_name("Frankfurt Hauptbahnhof", max_number=3)[0]
destination = client.stop_by_coords(50.099613, 8.685449, max_number=3)[0]

# Find a trip by locations got
trip = client.trip_find(origin_id=origin.id, dest_id=destination.id)
```
"""

__name__ = "pyrmv"
__version__ = "0.5.0"
__license__ = "MIT License"
__author__ = "Profitroll"

from . import classes, const, enums, errors, raw, utility
from .classes.client import Client
