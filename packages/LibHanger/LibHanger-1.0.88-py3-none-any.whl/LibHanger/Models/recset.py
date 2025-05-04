from __future__ import annotations # annotationsはファイルの先頭でimportする必要がある為位置を変更しないこと

import inspect
import pandas as pd
import copy
import json
import LibHanger.Library.uwLogger as Logger
from typing import TypeVar, Generic, Union
from enum import Enum
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import and_, or_, asc
from sqlalchemy.orm.attributes import InstrumentedAttribute
from LibHanger.Models.fields import fields
from LibHanger.Library.DataAccess.Base.uwDataAccess import uwDataAccess
from LibHanger.Library.uwDeclare import uwDeclare as en
from LibHanger.Models.saJoin import saJoin
from LibHanger.Models.saWhere import saWhere
from LibHanger.Models.saOrderBy import saOrderBy
from LibHanger.Models.Base.BaseModel import baseModel

T = TypeVar("T")

class recset(Generic[T]):
    """
    レコードセットクラス
    """

    __SA_INSTANCE_STATE__ = "_sa_instance_state"
    """ _sa_instance_state ColumnName"""

    __ROW_STATE__ = "rowState"
    """ rowState ColumnName"""

    class rowState(Enum):
        """
        行状態クラス
        """

        noChanged = 0
        """ 変更なし """

        added = 1
        """ 追加 """

        modified = 2
        """ 変更 """

        deleted = 3
        """ 削除 """

    class findOption(Enum):
        """
        検索モード
        """

        cacheOnly = 0
        """ キャッシュのみ検索 """

        dataBase = 1
        """ DBを検索 """

    class upsertResult:
        """
        upsert処理結果クラス
        """

        result = en.resultRegister.success
        """ 処理結果 """

        exceptInfo = None
        """ 例外情報 """

    def __init__(self, t: baseModel, __da: uwDataAccess = None, __where=None) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        t : baseModel
            Modelクラス基底
        __da : uwDataAccess
            データアクセスクラスインスタンス
        __where : Any
            Where条件
        """

        # Modelクラス
        self.modelType = t

        # DataAccessクラス保持
        self.__da = __da

        # カラム情報
        self.__columns = self.__getColumnAttr()

        # 主キー情報
        self.__primaryKeys = self.__getPrimaryKeys()

        # 行情報初期化
        self.__rows: list[baseModel] = []
        if (
            not self.__da is None
            and not self.__da.session is None
            and not __where is None
        ):
            self.filter(__where)
        else:
            self.__initRows()

        # 現在行位置初期化
        self.__currentRowIndex = -1

        # フィールドクラス
        self.__fields = fields(self.__rows)

        # 一時セッションフラグ
        self.__tempSessionFlg = False

    @property
    def recSetName(self) -> str:
        """
        レコードセット名
        """

        return self.modelType.__tablename__

    @property
    def recordCount(self):
        """
        レコード数
        """

        return len(self.rows)

    @property
    def session(self):
        """
        DBセッション
        """

        return self.__da.session

    @property
    def rows(self):
        """
        行情報(List)
        """

        return self.__rows

    @property
    def columns(self):
        """
        カラム情報
        """

        return self.__columns

    @property
    def primaryKeys(self):
        """
        主キー情報プロパティ
        """

        return self.__primaryKeys

    @property
    def State(self) -> rowState:
        """
        行状態(getter)
        """

        return self.__rows[self.__currentRowIndex].rowState

    @State.setter
    def State(self, __rowState: rowState):
        """
        行状態(setter)

        Parameters
        ----------
        __rowState : rowState
            行状態列挙体
        """

        # rowsのカレント行の行状態をmodifiedに変更
        if self.__rows[self.__currentRowIndex].rowState == self.rowState.noChanged:
            self.__rows[self.__currentRowIndex].rowState = __rowState

    def fields(self, __column: Union[InstrumentedAttribute, str]):
        """
        レコードセットフィールド情報

        Parameters
        ----------
        __column : Any
            ColumnオブジェクトまたはColumn名称
        """

        # カラム名をfieldsに渡す
        if type(__column) is InstrumentedAttribute:
            self.__fields.columnName = __column.key
        elif type(__column) is str:
            self.__fields.columnName = __column

        # カレント行インデックスをfieldsに渡す
        self.__fields.currentRowIndex = self.__currentRowIndex

        return self.__fields

    def __getColumnAttr(self):
        """
        モデルクラスのインスタンス変数(列情報)取得

        Parameters
        ----------
        None

        """

        # インスタンス変数取得
        attributes = inspect.getmembers(
            self.modelType, lambda x: not (inspect.isroutine(x))
        )

        # 特定のインスタンス変数を除外してリストとしてインスタンス変数を返す
        return list(
            filter(
                lambda x: not (
                    x[0].startswith("__")
                    or x[0].startswith("_")
                    or x[0] == "metadata"
                    or x[0] == "registry"
                    or x[0] == "rowState"
                ),
                attributes,
            )
        )

    def __getPrimaryKeys(self):
        """
        主キー情報取得

        Parameters
        ----------
        None

        """

        # 主キーリスト作成
        primaryKeys = []
        for col in self.__columns:

            memberInvoke = getattr(self.modelType, col[0])
            if memberInvoke.primary_key == True:
                primaryKeys.append(col[0])

        # 主キー情報を返す
        return primaryKeys

    def __getPKeyFilter_sa(self, row: baseModel):
        """
        主キー条件取得(SQL Alchemy用)

        row : Any
            行情報
        """

        # 主キー条件リスト初期化
        pKeyList = []

        # 主キーのみで条件を組み立て
        for key in self.__getPrimaryKeys():
            w = getattr(self.modelType, key) == getattr(row, key)
            pKeyList.append(w)

        # 主キー条件リストをtupleに変換して返す
        return and_(*tuple(pKeyList))

    def __getatterByModel(self, modelType, colName) -> InstrumentedAttribute:
        """
        Modelのインスタンス変数を取得する

        Parameters
        ----------
        modelType : baseModel
            モデルクラス基底
        colName : str
            カラム名
        """
        return getattr(modelType, colName)

    def __rowSetting(self, row: baseModel):
        """
        行情報を生成する

        Parameters
        ----------
        row : baseModel
            行情報
        """

        for col in self.__columns:

            # Modelのインスタンス変数取得
            memberInvoke = self.__getatterByModel(self.modelType, col[0])
            # 既定値の設定
            setattr(row, col[0], memberInvoke.default.arg)

        # 生成した行を返す
        return row

    def __addRecrow(self):
        """
        レコードセット行追加処理
        """

        # カレント行インデックス++
        self.__currentRowIndex += 1

        # 行生成
        row: baseModel = self.modelType()

        # 行状態を初期化
        row.rowState = self.rowState.noChanged

        # RowList - add
        self.__rows.append(self.__rowSetting(row))

        # 行状態をaddedに変更
        self.State = self.rowState.added

    def __editRecrow(self):
        """
        レコードセットを編集状態にする
        """

        # 行状態をmodifiedに変更
        self.State = self.rowState.modified

    def __initRows(self):
        """
        行情報をリセットする
        """

        self.__rows: list[baseModel] = []

    def __deepCopyRow(self, rows: list[baseModel]) -> list[baseModel]:
        """
        行情報をコピーする

        Parameters
        ----------
        rows : list
            行情報リスト
        """

        # 行インスタンスをDeepCopy
        targetRows = copy.deepcopy(rows)
        # DataFrame化で不要な列を削除
        for rowInstance in targetRows:
            if hasattr(rowInstance, self.__SA_INSTANCE_STATE__):
                delattr(rowInstance, self.__SA_INSTANCE_STATE__)
            if hasattr(rowInstance, self.__ROW_STATE__):
                delattr(rowInstance, self.__ROW_STATE__)

        return targetRows

    def __getKeyTuple(self, row):
        """
        rowのキー値をtupleで取得

        Parameters
        ----------
        row : Any
            行情報
        """

        # 主キー値リスト初期化
        pKeyValueList = []

        # 主キー値をリストに追加
        for key in self.__getPrimaryKeys():
            pKeyValueList.append(getattr(row, key))

        # tupleに変換(dictrowのKeyにする)
        return tuple(pKeyValueList)

    def __checkSessionOpen(self, __autoCommit=True, __beginTransaction=False):
        """
        セッションチェック(Open)

        Parameters
        ----------
        __autoCommit : bool
            AutoCommit
        __beginTransaction : bool
            Sessionを開いた時にトランザクションを開始するか

        """

        # sessionがNoneの場合はautocommit=Onで接続を開く
        if self.__da.session is None:
            self.__da.openSession(__autoCommit)
            self.__da.beginTransaction()
            self.__tempSessionFlg = True
        else:
            # autocommit=Onの場合はtransactionを開始する
            if (
                self.__da.autoCommit
                and self.__da.session.transaction is None
                and __beginTransaction
            ):
                self.__da.beginTransaction()

    def __checkSessionClose(self):
        """
        セッションチェック(Close)

        Parameters
        ----------
        None

        """

        if not self.__da.session is None and self.__tempSessionFlg:
            self.__da.closeSession()
            self.__tempSessionFlg = False

    def setDA(self, __da: uwDataAccess):
        """
        DataAccessクラスインスタンスセット

        Parameters
        ----------
        __da : uwDataAccess
            DataAccessクラスインスタンス
        """

        # daインスタンスセット
        if self.__da is None or not self.__da is __da:
            self.__da = __da

    def newRow(self):
        """
        新規行を生成する

        Parameters
        ----------
        None

        """

        # 新規行情報生成
        self.__addRecrow()

    def editRow(self):
        """
        レコードセットを編集状態にする

        Parameters
        ----------
        None

        """

        # 編集状態にする
        self.__editRecrow()

    def delRow(self):
        """
        レコードセットのカレント行を削除対象とする
        """

        # 行状態をdeletedに変更
        self.State = self.rowState.deleted

    def first(self):
        """
        カレント行を先頭にする
        """

        self.__currentRowIndex = -1

    def eof(self):
        """
        レコードセットの行情報有無を返す

        Parameters
        ----------
        None

        """

        # カレント行インデックス++
        self.__currentRowIndex += 1

        return False if len(self.__rows) > self.__currentRowIndex else True

    def nexteof(self):
        """
        次レコードの行情報有無を返す

        Parameters
        ----------
        None

        """

        return False if len(self.__rows) > self.__currentRowIndex + 1 else True

    def toJson(self, collectionName=None):
        """
        レコードセットをJSON形式に変換する

        Parameters
        ----------
        None

        """

        # レコードセットをDataFrameに変換
        df = self.getDataFrameForDatasource()

        # DataFrameをJSON形式に変換
        pd_json = df.to_json(orient="records")
        
        # JSON形式に変換
        if collectionName is None:
            return pd_json
        else:
            new_collection = {collectionName:[]}
            for record in json.loads(pd_json):
                new_collection[collectionName].append(record)
            
            return json.dumps(new_collection)
    
    def getDataFrameForDatasource(self):
        """
        データソース用のDataFrameを取得する
        """
        return self.getDataFrame(keyDrop=False)
    
    def getDataFrame(self, __rows=None, keyDrop = True):
        """
        Model⇒DataFrameに変換する

        Parameters
        ----------
        __rows : list
            行情報リスト
        keyDrop : bool
            DataFrameからインデックスを削除するか
        """

        rows = self.__rows if __rows is None else __rows
        collist = []
        if len(rows) == 0:
            for column in self.__columns:
                collist.append(column[0])
        else:

            # 行情報コピー
            targetRows = self.__deepCopyRow(rows)

            # 行インスタンスをリスト化
            rowlist = list(map(lambda f: vars(f), targetRows))

        # rowlistをDataFrame変換
        df = pd.DataFrame(rowlist) if len(rows) > 0 else pd.DataFrame(columns=collist)
        
        # DataFrameに主キー設定
        if len(self.__primaryKeys) > 0 and len(rows) > 0:
            df = df.set_index(self.__primaryKeys, drop=keyDrop)

        # 戻り値を返す
        return df

    def outerjoinFilter(self, j: saJoin, w: saWhere, s: saOrderBy):
        """
        外部結合

        Parameters
        ----------
        j : saJoin
            結合条件
        w : saWhere
            Where条件
        s : saOrderBy
            ソート条件
        """

        self.joinFilter(j, True, w, s)

    def innerjoinFilter(self, j: saJoin, w: saWhere, s: saOrderBy):
        """
        内部結合

        Parameters
        ----------
        j : saJoin
            結合条件
        w : saWhere
            Where条件
        s : saOrderBy
            ソート条件
        """

        self.joinFilter(j, False, w, s)

    def joinfilterExpr(
        self, joinTable: dict, columns: tuple, isouter, w: saWhere, s: saOrderBy
    ):
        """
        テーブル結合

        Parameters
        ----------
        joinTable : dict
            結合対象テーブル情報
        columns : tuple[column]
            取得列
        isouter : bool
            外部結合フラグ(True:外部結合 False:内部結合)
        w : any | asWhere
            where条件
        s : Any | asOrderBy
            ソート順
        """

        # メインデータソースと取得列
        q = self.__da.session.query(self.modelType, *columns)

        # テーブル結合
        for jt in joinTable:
            jk = and_(*tuple(joinTable[jt]))
            q = q.join(jt, jk, isouter=isouter)

        # where条件
        # -AND
        if w != None and len(w.andList) > 0:
            q = q.filter(and_(*tuple(w.andList)))

        # -OR
        if w != None and len(w.orList) > 0:
            q = q.filter(or_(*tuple(w.orList)))

        # ソート条件
        if s != None and len(s.orderBy) > 0:
            # keyでソート
            sort_orderBy = sorted(s.orderBy.items())
            for sortKey in sort_orderBy:
                q = q.order_by(sortKey[1])
        return q

    def joinFilter(self, j: saJoin, isouter: bool, w: saWhere, s: saOrderBy):
        """
        結合したレコードセットをフィルタする
        結果セットはdbから取得

        Parameters
        ----------
        j : saJoin
            結合条件
        isouter : bool
            外部結合フラグ(True:外部結合 False:内部結合)
        w : any | asWhere
            where条件
        s : Any | asOrderBy
            ソート順
        """

        # 行情報初期化
        self.__initRows()
        
        # フィールドクラス
        self.__fields = fields(self.__rows)

        # セッションチェック
        self.__checkSessionOpen(False, False)

        # クエリ実行
        rowIndex = 0
        q:list[baseModel] = self.joinfilterExpr(j.joinTable, j.columns, isouter, w, s).all()
        for row in q:

            # fieldリスト作成
            fldList = []
            for fldIdx in range(1, len(row._fields)):
                fldList.append(row._fields[fldIdx])
            fldList.append(self.__SA_INSTANCE_STATE__)

            # メインテーブルの行情報コピー
            mainRow:baseModel = copy.deepcopy(row[0])
            # 行情報のメンバ取得
            attributes = inspect.getmembers(
                row[0], lambda x: not (inspect.isroutine(x))
            )
            rowInfoMember = list(
                filter(
                    lambda x: not (
                        x[0].startswith("__")
                        or x[0].startswith("_")
                        or x[0] == "metadata"
                        or x[0] == "registry"
                        or x[0] == "rowState"
                    ),
                    attributes,
                )
            )
            # 抽出列以外はメンバを削除
            for attr in rowInfoMember:
                if attr[0] in fldList:
                    continue
                delattr(mainRow, attr[0])

            # 行状態をnoChangedに変更
            mainRow.rowState = self.rowState.noChanged
            # joinテーブルの行情報をmainRowにマージ
            for fldIdx in range(1, len(row._fields)):
                setattr(mainRow, row._fields[fldIdx], row._data[fldIdx])
            # rowsにクエリ結果を追加
            self.__rows.append(mainRow)
            # rowIndex++
            rowIndex += 1

        # セッションチェック
        self.__checkSessionClose()

        # カレント行インデックス初期化
        self.__currentRowIndex = -1

    def filterExpr(self, w, s=None):
        """
        フィルタ条件適用

        Parameters
        ----------
        w : Any | asWhere
            抽出条件
        s : Any | asOrderBy
            ソート順
        """

        # Where条件
        if not type(w) is saWhere:
            q = self.__da.session.query(self.modelType).filter(w)
        else:
            q = self.__da.session.query(self.modelType)

            # where条件キャスト
            wx: saWhere = w

            # AND
            if len(wx.andList) > 0:
                q = q.filter(and_(*tuple(wx.andList)))

            # OR
            if len(wx.orList) > 0:
                q = q.filter(or_(*tuple(wx.orList)))

        # Sort順
        if s is None:
            for pKey in self.__primaryKeys:
                q = q.order_by(asc(getattr(self.modelType, pKey)))
        elif not type(s) is saOrderBy:
            q = q.order_by(s)
        else:

            # OrderByキャスト
            sx: saOrderBy = s

            # OrderBy 組み立て
            if len(sx.orderBy) > 0:
                # keyでソート
                sort_orderBy = sorted(sx.orderBy.items())
                for sortKey in sort_orderBy:
                    q = q.order_by(sortKey[1])

        # 戻り値を返す
        return q

    def filter(self, w, s=None, searchOption=findOption.dataBase):
        """
        レコードセットをフィルタする
        結果セットはdbから取得

        Parameters
        ----------
        w : any | asWhere
            where条件
        s : Any | asOrderBy
            ソート順
        searchOption : findOption
            検索オプション
        """

        if searchOption == self.findOption.dataBase:

            # 行情報初期化
            self.__initRows()

            # フィールドクラス
            self.__fields = fields(self.__rows)

            # セッションチェック
            self.__checkSessionOpen(False, False)

            # クエリ実行
            rowIndex = 0
            q:list[baseModel] = self.filterExpr(w, s).all()
            for row in q:
                # 行状態をnoChangedに変更
                row.rowState = self.rowState.noChanged
                # rowsにクエリ結果を追加
                self.__rows.append(row)
                # rowIndex++
                rowIndex += 1

            # セッションチェック
            self.__checkSessionClose()

        elif searchOption == self.findOption.cacheOnly:

            # rows⇒DataFrameに変換してフィルタ
            df = self.getDataFrame()
            dfw = self.convertDataFrameExpr(df, w)
            df: pd.DataFrame = df[dfw]

            # rows初期化
            rowsTempDict = {}
            rowsTemp = []

            # __rowsをフィルタする
            for row in self.__rows:
                keyValue = ""
                for key in self.__getPrimaryKeys():
                    keyValue += getattr(row, key)
                rowsTempDict[keyValue] = row
            for _, item in df.iterrows():
                keyValue = ""
                for key in self.__getPrimaryKeys():
                    keyValue += item[key]
                if keyValue in rowsTempDict:
                    rowsTemp.append(rowsTempDict[keyValue])

            # rows再セット
            self.__rows = rowsTemp

            # dfw解放
            dfw = None

            # フィールドクラス
            self.__fields = fields(self.__rows)

        # カレント行インデックス初期化
        self.__currentRowIndex = -1

    def convertDataFrameExpr(self, df, w):
        """
        sqlAlchemyのfilter条件をDataFrameのfilter条件に変換

        df : DataFrame
            対象DataFrame
        w : any | asWhere
            where条件
        """

        if not type(w) is saWhere:
            return w
        else:
            # where条件キャスト
            wx: saWhere = w

            # 条件格納用リスト初期化
            andExprList = []
            orExprList = []

            # AND
            if len(wx.andList) > 0:
                for expr in wx.andList:
                    andExpr: BinaryExpression = expr
                    if not type(andExpr.right.value) is list:
                        if andExpr.operator.__name__ == "eq":
                            andExprList.append(
                                df[andExpr.left.key] == andExpr.right.value
                            )
                        elif andExpr.operator.__name__ != "ne":
                            andExprList.append(
                                df[andExpr.left.key] != andExpr.right.value
                            )
                        elif andExpr.operator.__name__ != "gt":
                            andExprList.append(
                                df[andExpr.left.key] > andExpr.right.value
                            )
                        elif andExpr.operator.__name__ != "lt":
                            andExprList.append(
                                df[andExpr.left.key] < andExpr.right.value
                            )
                        elif andExpr.operator.__name__ != "ge":
                            andExprList.append(
                                df[andExpr.left.key] >= andExpr.right.value
                            )
                        elif andExpr.operator.__name__ != "le":
                            andExprList.append(
                                df[andExpr.left.key] <= andExpr.right.value
                            )
                    else:
                        dfInExpr = None
                        for rval in andExpr.right.value:
                            dfInExprTmp = df[andExpr.left.key] == rval
                            dfInExpr = (
                                (dfInExpr | dfInExprTmp)
                                if not dfInExpr is None
                                else dfInExprTmp
                            )
                        andExprList.append(dfInExpr)
            # OR
            if len(wx.orList) > 0:
                for expr in wx.orList:
                    orExpr: BinaryExpression = expr
                    orExprList.append(df[orExpr.left.key] == orExpr.right.value)

            # DataFrame用のwhere条件組み立て
            retExpr = None
            for expr in andExprList:
                retExpr = retExpr & expr if not retExpr is None else expr
            for expr in orExprList:
                retExpr = retExpr | expr if not retExpr is None else expr

            # 戻り値を返す
            return retExpr

    def find(self, w, searchOption=findOption.cacheOnly):
        """
        現在保持しているレコードセットに指定した条件に合致するレコードが存在するか返す

        Parameters
        ----------
        w : Any
            抽出条件
        searchOption : findOption
            検索方法
        """

        # filter
        if searchOption == self.findOption.cacheOnly:
            # rows⇒DataFrame変換
            df = self.getDataFrame()

            # 条件抽出
            dfw = self.convertDataFrameExpr(df, w)

            # 戻り値を返す
            dfCheck = df[dfw]
            return True if len(dfCheck) > 0 else False
        elif searchOption == self.findOption.dataBase:

            # セッションチェック
            self.__checkSessionOpen(False, False)
            # クエリ実行
            q = self.filterExpr(w).all()
            # セッションチェック
            self.__checkSessionClose()
            # 戻り値を返す
            return True if len(q) > 0 else False

    def existsPKeyRec(self, row, sessionCheck=False):
        """
        対象行に対して主キー制約に違反しているか

        Parameters
        ----------
        row : Any
            行情報
        """

        # セッションチェック
        if sessionCheck:
            self.__checkSessionOpen(False, False)

        # 主キーを条件として該当レコードが存在するか確認
        w = self.__getPKeyFilter_sa(row)
        q = self.__da.session.query(self.modelType).filter(w).all()
        for qrow in q:

            dictRow = vars(row)
            dictRow_sorted = sorted(dictRow.items())
            for col in dictRow_sorted:
                if col[0] == self.__SA_INSTANCE_STATE__:
                    continue
                setattr(qrow, col[0], getattr(row, col[0]))

            self.__rows.append(qrow)
            self.rows.remove(row)

        # セッションチェック
        if sessionCheck:
            self.__checkSessionClose()

        # 結果を返す
        return len(q) > 0

    def merge(self, srcRecset:recset[baseModel], sort=True):
        """
        レコードセットをマージする

        Parameters
        ----------
        srcRecset : Any
            マージ元レコードセット

        Notes
        -----
            マージ先に同一のキー情報が存在した場合はマージ対象から除外
        """

        # rows⇒dict変換
        dictrows = dict()
        if sort:
            for row in self.__rows:

                # tupleに変換(dictrowのKeyにする)
                pKeyTuple = self.__getKeyTuple(row)

                # rowをdictrowsにセット
                if not pKeyTuple in dictrows:
                    dictrows[pKeyTuple] = row

        # マージ対象レコードセットをrowsに追加
        for mergeRow in srcRecset.rows:

            # rowのキー値取得
            pKeyTuple = self.__getKeyTuple(mergeRow)

            # キー値がdictrowに無ければ__dictrowsに追加
            if not pKeyTuple in dictrows:
                dictrows[pKeyTuple] = mergeRow

        # dictrowsをソート
        rows_sorted = sorted(dictrows.items())

        if sort:

            # rows再構築
            self.__rows.clear()
            for row in rows_sorted:
                self.__rows.append(row[1])

        else:

            # rows追加
            for row in rows_sorted:
                self.__rows.append(row[1])

        # fields再構築
        self.__fields = fields(self.__rows)

    def upsert(self):
        """
        データ更新(upsert用)

        Notes
        -----
            rowState = addedとした行を追加する際に主キー違反している場合、強制的にmodifiedとして扱う。\n
            recsetに存在する追加行(rowState = added)全てに対して存在チェックが走るので \n
            件数によっては更新にかなりの時間を要する。
            削除行に関してはレコード抽出後にdeleteメソッドを走らせるはずなので存在チェックは行っていない。
        """

        return self.update(True)

    def update(self, upsert=False) -> upsertResult:
        """
        データ更新(通常用)

        Notes
        -----
            rowState = addedとした行を追加する際に主キー違反していればSQLAlchemyErrorとなる。\n
            recset側でDBとの制約を解決していればupsertよりこちらのほうが速度は上
        """

        # 処理結果クラスインスタンス
        upResult = self.upsertResult()

        try:

            # セッションチェック
            self.__checkSessionOpen(True, True)

            # 新規行はaddする
            newRows = [
                row for row in self.__rows if row.rowState == self.rowState.added
            ]
            for newRow in newRows:
                # 主キー違反していない行のみadd
                if upsert == False or not self.existsPKeyRec(newRow):
                    self.__da.session.add(newRow)

            # 削除行はdeleteする
            delRows = [
                row for row in self.__rows if row.rowState == self.rowState.deleted
            ]
            for delRow in delRows:
                self.__da.session.delete(delRow)

            # flush
            self.__da.session.flush()

            # Commit
            if self.__da.autoCommit and not self.__da.session.transaction is None:
                self.__da.session.commit()

            # セッションチェック
            self.__checkSessionClose()

            # 処理結果セット
            upResult.result = en.resultRegister.success

        except SQLAlchemyError as e:

            # エラーログ出力
            Logger.logging.error(e)

            # 処理結果セット
            upResult.result = en.resultRegister.failure
            upResult.exceptInfo = e

            # Rollback
            if self.__da.autoCommit:
                self.__da.session.rollback()

        # 処理結果を返す
        return upResult
