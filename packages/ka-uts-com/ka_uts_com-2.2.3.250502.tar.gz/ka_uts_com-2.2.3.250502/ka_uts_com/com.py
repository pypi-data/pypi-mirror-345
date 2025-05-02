from typing import Any

# import os
import time
import calendar
from datetime import datetime

from ka_uts_equ.equ import AoEqu
from ka_uts_uts.utils.pacmod import PacMod

from ka_uts_com.app import App
from ka_uts_com.cfg import Cfg
from ka_uts_com.exit import Exit

from ka_uts_log.log import Log

TyAny = Any
TyDateTime = datetime
TyTimeStamp = int
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]

TnAny = None | Any
TnArr = None | TyArr
TnDic = None | TyDic
TnTimeStamp = None | TyTimeStamp
TnDateTime = None | TyDateTime
TnStr = None | str


class Com:
    """
    Communication Class
    """
    sw_init: bool = False
    tenant: TnStr = None
    cmd: TnStr = None
    d_com_pacmod: TyDic = {}
    d_app_pacmod: TyDic = {}

    ts: TnTimeStamp
    ts_start: TnDateTime = None
    ts_end: TnDateTime = None
    ts_etime: TnDateTime = None
    d_timer: TyDic = {}

    Cfg: TnDic = None
    Log: Any = None
    App: Any = None
    Exit: Any = None

    @classmethod
    def init(cls, kwargs: TyDic):
        # def init(cls, cls_app, kwargs: TyDic):
        """
        initialise static variables of Com class
        """
        if cls.sw_init:
            return
        cls.sw_init = True
        cls.tenant = kwargs.get('tenant')
        cls.cmd = kwargs.get('cmd')
        cls_app = kwargs.get('cls_app')
        cls.d_com_pacmod = PacMod.sh_d_pacmod(cls)
        cls.d_app_pacmod = PacMod.sh_d_pacmod(cls_app)
        cls.ts = calendar.timegm(time.gmtime())

        cls.Log = Log.sh(**kwargs)
        cls.Cfg = Cfg.sh(cls, **kwargs)
        cls.App = App.sh(cls, **kwargs)
        cls.Exit = Exit.sh(**kwargs)

    @classmethod
    def sh_kwargs(cls, cls_app, d_parms, *args) -> TyDic:
        """
        show keyword arguments
        """
        _kwargs: TyDic = AoEqu.sh_d_eq(*args, d_parms=d_parms)
        _kwargs['cls_app'] = cls_app
        _kwargs['com'] = cls

        cls.init(_kwargs)
        return _kwargs
