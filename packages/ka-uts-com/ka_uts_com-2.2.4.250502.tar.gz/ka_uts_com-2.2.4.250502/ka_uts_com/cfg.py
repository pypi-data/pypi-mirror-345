# coding=utf-8
from typing import Any

from ka_uts_uts.ioc.yaml_ import Yaml_
from ka_uts_uts.utils.pacmod import PacMod

TyAny = Any
TyTimeStamp = int
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]


class Cfg:
    """Configuration Class
    """
    sw_init: TyBool = False
    cfg: Any = None

    @classmethod
    def init(cls, cls_com, **kwargs) -> None:
        if cls.sw_init:
            return
        cls.sw_init = True
        _cls_app = kwargs.get('cls_app')
        _path = PacMod.sh_path_cfg_yml(_cls_app)
        if _path:
            cls.cfg = Yaml_.read_with_safeloader(_path)

    @classmethod
    def sh(cls, cls_com, **kwargs) -> Any:
        if cls.sw_init:
            return cls
        cls.init(cls_com, **kwargs)
        return cls.cfg
