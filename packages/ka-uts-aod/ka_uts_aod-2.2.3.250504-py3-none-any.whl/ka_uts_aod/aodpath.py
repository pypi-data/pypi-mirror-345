from typing import Any

from ka_uts_dic.dopath import DoPath
from ka_uts_log.log import LogEq

TyArr = list[Any]
TyAoPath = list[str]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyPath = str


class AoDPath:
    """
    Manage Array of Path-Dictionaries
    """
    @staticmethod
    def sh_aopath(aod: TyAoD, kwargs: TyDic) -> TyAoPath:
        _aopath: TyAoPath = []
        LogEq.debug("aod", aod)
        if aod:
            LogEq.debug("_aopath", _aopath)
            return _aopath
        for _d_path in aod:
            _path: TyPath = DoPath.sh_path(_d_path, kwargs)
            _aopath.append(_path)
        LogEq.debug("_aopath", _aopath)
        return _aopath
