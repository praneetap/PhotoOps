"""
DDB Put Item
"""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PutDdbItemAction:
    '''Put DDB item action'''

    # FIXME: how do I ensure the Item has pk and sk attributes.
    Item: Any
