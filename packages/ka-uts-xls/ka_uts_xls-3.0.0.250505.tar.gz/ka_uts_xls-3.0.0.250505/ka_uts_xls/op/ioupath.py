from typing import Any, TypeAlias

import openpyxl as op
import pandas as pd

from ka_uts_obj.path import Path
from ka_uts_xls.ioipath import IoiPathWbOp
from ka_uts_xls.op.wbop import WbOp

TyWbOp: TypeAlias = op.workbook.workbook.Workbook
TyPdDf: TypeAlias = pd.DataFrame

TyDic = dict[Any, Any]
TyDoPdDf = dict[Any, TyPdDf]
TyPath = str
TnWbOp = None | TyWbOp


class IouPathWbOp:

    @staticmethod
    def update_wb_with_dodf_using_tmpl(
            dodf: TyDoPdDf, path_tmpl: TyPath, path: TyPath, **kwargs) -> None:
        _wb_tmpl: TyWbOp = IoiPathWbOp.load(path_tmpl)
        wb: TnWbOp = WbOp.update_wb_with_dodf(_wb_tmpl, dodf, **kwargs)
        if wb is None:
            return
        Path.mkdir_from_path(path)
        wb.save(path)
