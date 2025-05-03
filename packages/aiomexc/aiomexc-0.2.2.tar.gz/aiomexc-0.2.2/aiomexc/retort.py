from adaptix import NameStyle, Retort, name_mapping

from aiomexc.methods import (
    MexcMethod,
    QueryOrder,
    CreateListenKey,
    GetListenKeys,
    ExtendListenKey,
    DeleteListenKey,
)
from aiomexc.types import Order, AccountInformation, TickerPrice, ListenKey, ListenKeys

type_recipes = [
    name_mapping(
        mexc_type,
        name_style=NameStyle.CAMEL,
    )
    for mexc_type in [
        Order,
        AccountInformation,
        TickerPrice,
        ListenKey,
        ListenKeys,
    ]
]

_retort = Retort(
    recipe=[
        name_mapping(
            MexcMethod,
            name_style=NameStyle.CAMEL,
            omit_default=True,
        ),
        name_mapping(
            QueryOrder,
            name_style=NameStyle.CAMEL,
            omit_default=True,
        ),
        name_mapping(
            CreateListenKey,
            name_style=NameStyle.CAMEL,
            omit_default=True,
        ),
        name_mapping(
            GetListenKeys,
            name_style=NameStyle.CAMEL,
            omit_default=True,
        ),
        name_mapping(
            ExtendListenKey,
            name_style=NameStyle.CAMEL,
            omit_default=True,
        ),
        name_mapping(
            DeleteListenKey,
            name_style=NameStyle.CAMEL,
            omit_default=True,
        ),
    ]
    + type_recipes,
)

__all__ = ["_retort"]
