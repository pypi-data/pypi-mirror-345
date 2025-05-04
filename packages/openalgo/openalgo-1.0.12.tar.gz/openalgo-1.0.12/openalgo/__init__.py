# -*- coding: utf-8 -*-
"""
OpenAlgo Python Library
"""

from .orders import OrderAPI
from .data import DataAPI
from .account import AccountAPI
from .strategy import Strategy

class api(OrderAPI, DataAPI, AccountAPI):
    """
    OpenAlgo API client class
    """
    pass

__version__ = "1.0.12"
