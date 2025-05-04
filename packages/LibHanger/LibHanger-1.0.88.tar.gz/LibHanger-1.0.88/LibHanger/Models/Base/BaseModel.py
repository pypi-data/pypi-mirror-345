from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr

class baseModel:
    """
    Modelクラス基底
    """
    
    rowState = None
    """行状態"""

    _fields = None
    """_fields"""
    
    _data = None
    """_data"""
    
    @declared_attr
    def __tablename__(cls):
        """
        テーブル名
        """
        return cls.__name__.lower()

# Baseクラス生成
Base = declarative_base(cls=baseModel)
