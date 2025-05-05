from typing import Dict

# Constant is taken from source of PyRMVtransport:
# https://github.com/cgtobi/PyRMVtransport/blob/development/RMVtransport/const.py
PRODUCTS: Dict[str, int] = {
    "ice": 1,
    "ic": 2,
    "ec": 2,
    "r": 4,
    "rb": 4,
    "re": 4,
    "sbahn": 8,
    "ubahn": 16,
    "tram": 32,
    "bus": 64,
    "bus2": 128,
    "ferry": 256,
    "taxi": 512,
    "bahn": 1024,
}
