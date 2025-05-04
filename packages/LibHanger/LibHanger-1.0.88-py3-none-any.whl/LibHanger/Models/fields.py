class fields():
    
    """
    fieldsクラス
    """
    
    def __init__(self, __rows):
        
        """
        コンストラクタ
        """
        
        self.__rows = __rows
        self.__currentRowIndex = 0
        self.__columnName = ''
        
    @property
    def currentRowIndex(self):
        
        """
        カレント行インデックス(getter)
        """
        
        return self.__currentRowIndex

    @currentRowIndex.setter
    def currentRowIndex(self, __currentRowIndex):

        """
        カレント行インデックス(setter)
        """

        self.__currentRowIndex = __currentRowIndex

    @property
    def columnName(self):
        
        """
        カラム名(getter)
        """
        
        return self.__columnName

    @columnName.setter
    def columnName(self, __columnName):

        """
        カラム名(setter)
        """

        self.__columnName = __columnName
    
    @property
    def rows(self):

        """
        行情報List(getter)
        """
        
        return self.__rows
        
    @property
    def value(self):

        """
        fieldsの値を保持する(getter)
        """

        return getattr(self._fields__rows[self.__currentRowIndex], self.__columnName)

    @property
    def nextvalue(self):

        """
        次レコードfieldsの値を保持する(getter) 
        """

        return getattr(self._fields__rows[self.__currentRowIndex + 1], self.__columnName)
    
    @value.setter
    def value(self, value):
        
        """
        fieldsの値を保持する(setter)
        """
        
        # List - rows更新
        curRow = self._fields__rows[self.currentRowIndex]
        setattr(curRow, self.columnName, value)
        