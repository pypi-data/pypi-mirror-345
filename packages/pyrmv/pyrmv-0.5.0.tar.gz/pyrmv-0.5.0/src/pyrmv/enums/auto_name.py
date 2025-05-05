# Class is taken from source code of Pyrogram:
# https://github.com/pyrogram/pyrogram/blob/master/pyrogram/enums/auto_name.py

from enum import Enum

from ..const import PRODUCTS


class AutoName(Enum):
    def __init__(self, code) -> None:
        self.code = code

    def _generate_next_value_(self, *args):
        return self.lower()

    def __repr__(self):
        return f"pyrmv.enums.{self}"


class AutoNameProduct(AutoName):
    def __init__(self, code) -> None:
        self.code = PRODUCTS[code]
