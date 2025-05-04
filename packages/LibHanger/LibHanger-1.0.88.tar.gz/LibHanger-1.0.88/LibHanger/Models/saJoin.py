from __future__ import annotations

class saJoin():

    __joinTable = dict()
    """ joinテーブル格納用ディクショナリ """
    
    __columns = []
    """ 取得カラム格納用配列 """

    @property
    def joinTable(self):
        return self.__joinTable

    @property
    def columns(self):
        return self.__columns
    
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        # 初期化
        self.clear()
    
    def clear(self):
        
        """
        初期化
        """
        
        self.__joinTable.clear()
        self.__columns.clear()
        
    def joinTable_(self, joinModel, joinKey) -> saJoin:

        """ 
        joinTablelist追加 
        
        Parameters
        ----------
        t : Any
            joinテーブル
        """

        # dict追加
        self.__joinTable[joinModel] = joinKey

        # 戻り値を返す
        return self
    
    def columns_(self, c) -> saJoin:

        """ 
        columnlist追加 
        
        Parameters
        ----------
        c : Any
            カラム
        """

        # list追加
        self.__columns.append(c)

        # 戻り値を返す
        return self

    def joinKey_(self, k) -> list:

        """ 
        joinKeylist追加 
        
        Parameters
        ----------
        k : Any
            joinキー
        """

        # joinKey初期化
        __joinKey = []
        __joinKey.clear()

        # list追加
        __joinKey.append(k)

        # 戻り値を返す
        return __joinKey