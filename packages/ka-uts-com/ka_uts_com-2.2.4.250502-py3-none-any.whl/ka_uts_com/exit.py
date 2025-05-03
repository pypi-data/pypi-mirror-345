# coding=utf-8
from typing import Any

TyAny = Any
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]

TnAny = None | Any
TnArr = None | TyArr
TnBool = None | bool
TnDic = None | TyDic


class Exit:
    """Exit Class
    """
    sw_init: TyBool = False
    sw_critical: bool = False
    sw_stop: bool = False
    sw_interactive: bool = False

    @classmethod
    def init(cls, **kwargs) -> None:
        if cls.sw_init:
            return
        cls.sw_init = True
        cls.sw_critical = kwargs.get('sw_critical', False)
        cls.sw_stop = kwargs.get('sw_stop', False)
        cls.sw_interactive = kwargs.get('sw_interactive', False)

    @classmethod
    def sh(cls, **kwargs) -> Any:
        if cls.sw_init:
            return cls
        cls.init(**kwargs)
        return cls
